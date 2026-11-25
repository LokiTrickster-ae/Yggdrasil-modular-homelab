"""
main.py - Refrigeración activa del homelab (Raspberry Pi Pico + MicroPython)

Hardware:
  - Bus 1-Wire en GPIO 19 (pull-up externa 4.7 kΩ a 3.3 V) con 3x DS18B20:
        004b -> interior fuente ATX
        00dd -> junto a la placa del Nodo Lenovo A
        0043 -> junto a la placa del Nodo Lenovo B
  - Ventilador fuente ATX   : PWM 25 kHz en GPIO 10
  - Ventilador nodos Lenovo : PWM 25 kHz en GPIO 12

Salida serie (una línea por ciclo, fácil de parsear desde una Raspberry Pi 4):
  004b=35.50;00dd=33.12;0043=ERR;atx=45;nodos=100

Fail-safe:
  - Si un sensor falla (None, error CRC, desconectado, lectura 85.0/-127.0),
    el ventilador que depende de él pasa al 100 % y se re-escanea el bus
    en el siguiente ciclo.
  - Watchdog de 8 s: si el programa se cuelga, la Pico se reinicia y los
    pines PWM quedan sin señal (un ventilador de 4 pines sin PWM gira al máximo).
"""

import time
import onewire
import ds18x20
from machine import Pin, PWM, WDT

# ----------------------------------------------------------------------------
# Configuración
# ----------------------------------------------------------------------------
PIN_ONEWIRE = 18
PIN_FAN_ATX = 10
PIN_FAN_NODOS = 12
PWM_FREQ_HZ = 25_000

# Sufijos (últimos 4 caracteres hex de la ROM) de cada sensor
ID_ATX = "004b"
ID_NODO_A = "00dd"
ID_NODO_B = "0043"
SENSOR_IDS = (ID_ATX, ID_NODO_A, ID_NODO_B)

CONVERSION_MS = 750          # Tiempo de conversión DS18B20 a 12 bits
INVALID_READINGS = (85.0, -127.0)  # 85.0 = valor de power-on reset; -127 = error
WDT_TIMEOUT_MS = 8000        # Máximo permitido por el RP2040 (~8.3 s)

led = machine.Pin("LED", machine.Pin.OUT)
led.toggle()

# ----------------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------------
def lerp(x, x0, x1, y0, y1):
    """Interpolación lineal de x en [x0, x1] hacia [y0, y1]."""
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)


def rom_suffix(rom):
    """Devuelve los últimos 4 caracteres hex de una dirección ROM."""
    return "".join("{:02x}".format(b) for b in rom)[-4:]


# ----------------------------------------------------------------------------
# Curvas térmicas (devuelven % de 0 a 100)
# ----------------------------------------------------------------------------
def curva_atx(t):
    """Fuente ATX: nunca por debajo del 30 %."""
    if t < 30.0:
        return 30.0
    if t < 45.0:
        return lerp(t, 30.0, 45.0, 30.0, 70.0)
    if t < 50.0:
        return lerp(t, 45.0, 50.0, 70.0, 100.0)
    return 100.0


def curva_nodos(t):
    """Nodos Lenovo: parado por debajo de 32 °C."""
    if t < 32.0:
        return 0.0
    if t < 45.0:
        return lerp(t, 32.0, 45.0, 25.0, 60.0)
    if t < 55.0:
        return lerp(t, 45.0, 55.0, 60.0, 100.0)
    return 100.0


# ----------------------------------------------------------------------------
# Ventiladores
# ----------------------------------------------------------------------------
class Fan:
    """Ventilador PWM de 4 pines (25 kHz)."""

    def __init__(self, pin_num):
        self.pwm = PWM(Pin(pin_num))
        self.pwm.freq(PWM_FREQ_HZ)
        self.percent = 100
        self.set(100)  # Arranque seguro: 100 % hasta tener lecturas válidas

    def set(self, percent):
        percent = max(0, min(100, int(round(percent))))
        self.percent = percent
        self.pwm.duty_u16(percent * 65535 // 100)


# ----------------------------------------------------------------------------
# Sensores
# ----------------------------------------------------------------------------
class SensorBus:
    """Gestiona el bus 1-Wire, el escaneo y la lectura por sufijo de ROM."""

    def __init__(self, pin_num):
        self.ds = ds18x20.DS18X20(onewire.OneWire(Pin(pin_num)))
        self.roms = {}          # sufijo -> ROM
        self.needs_rescan = True

    def scan(self):
        """Escanea el bus y asocia cada sensor conocido por su sufijo."""
        self.roms = {}
        try:
            for rom in self.ds.scan():
                suffix = rom_suffix(rom)
                if suffix in SENSOR_IDS:
                    self.roms[suffix] = rom
        except Exception as e:
            print("# ERROR escaneando bus:", e)
        # Si falta algún sensor, se seguirá intentando en los siguientes ciclos
        self.needs_rescan = len(self.roms) < len(SENSOR_IDS)
        if self.needs_rescan:
            faltan = [s for s in SENSOR_IDS if s not in self.roms]
            print("# AVISO: sensores no encontrados:", ",".join(faltan))

    def read_all(self):
        """
        Lanza una conversión y lee los 3 sensores.
        Devuelve dict {sufijo: temperatura_float | None}.
        """
        if self.needs_rescan:
            self.scan()

        temps = {s: None for s in SENSOR_IDS}

        try:
            self.ds.convert_temp()
        except Exception as e:
            print("# ERROR convert_temp:", e)
            self.needs_rescan = True
            return temps

        time.sleep_ms(CONVERSION_MS)

        for suffix in SENSOR_IDS:
            rom = self.roms.get(suffix)
            if rom is None:
                continue
            try:
                t = self.ds.read_temp(rom)  # Lanza excepción en error de CRC
            except Exception:
                t = None
            if t is None or t in INVALID_READINGS:
                t = None
            temps[suffix] = t

        # Cualquier fallo -> re-escaneo automático en el siguiente ciclo
        if any(v is None for v in temps.values()):
            self.needs_rescan = True

        return temps


# ----------------------------------------------------------------------------
# Programa principal
# ----------------------------------------------------------------------------
def fmt(t):
    return "ERR" if t is None else "{:.2f}".format(t)


def main():
    fan_atx = Fan(PIN_FAN_ATX)        # Ambos arrancan al 100 %
    fan_nodos = Fan(PIN_FAN_NODOS)
    bus = SensorBus(PIN_ONEWIRE)
    wdt = WDT(timeout=WDT_TIMEOUT_MS)

    print("# Control de refrigeración iniciado")

    while True:
        wdt.feed()
        temps = bus.read_all()
        wdt.feed()

        t_atx = temps[ID_ATX]
        t_a = temps[ID_NODO_A]
        t_b = temps[ID_NODO_B]

        # Circuito 1: fuente ATX
        if t_atx is None:
            fan_atx.set(100)
        else:
            fan_atx.set(curva_atx(t_atx))

        # Circuito 2: nodos Lenovo (máxima de ambos; si falla uno -> 100 %)
        if t_a is None or t_b is None:
            fan_nodos.set(100)
        else:
            fan_nodos.set(curva_nodos(max(t_a, t_b)))

        # Línea de telemetría parseable
        print("{}={};{}={};{}={};atx={};nodos={}".format(
            ID_ATX, fmt(t_atx),
            ID_NODO_A, fmt(t_a),
            ID_NODO_B, fmt(t_b),
            fan_atx.percent, fan_nodos.percent))


main()
