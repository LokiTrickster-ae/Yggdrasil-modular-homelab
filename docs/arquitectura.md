# 🏛️ Arquitectura del Chasis y Distribución Física

Este documento detalla la distribución de los componentes dentro de la estructura modular del homelab.

---

## 🏗️ 1. Planta Superior

- **Exterior (Frontal de 1U):**
  - Alberga los tres paneles principales: el panel del switch, el panel de keystones y un panel compartido que integra la Raspberry Pi (ésta de carácter interno) y la pantalla LCD.
- **Interior:**
  - Aloja la fuente de alimentación ATX.
  - _Para ver los retos de integración y el cambio de orientación de la Raspberry Pi con el SSD NVMe, consulta el [Diario de Troubleshooting](../docs/troubleshooting.md#issue-raspberry-pi)._

---

## 🧱 2. Planta Inferior

- **Interior:**
  - Destinada exclusivamente a albergar las dos placas base de los Lenovo colocadas en **posición vertical** (presindiendo de sus carcasas originales para optimizar el espacio).
  - _Para ver las decisiones de diseño sobre el chasis a medida, el flujo de aire contrapuesto y la solución de las tapas laterales con embudos térmicos, consulta los siguientes apartados del [Diario de Troubleshooting](../docs/troubleshooting.md#issue-chasis-inferior):_
    - _[Diseño del chasis inferior y sujeción estructural](../docs/troubleshooting.md#issue-chasis-inferior)_
    - _[Rediseño y reimpresión de las tapas laterales con embudos térmicos](../docs/troubleshooting.md#issue-tapas-laterales)_

---

## ⚡ 3. Distribución Eléctrica y Raíles

La fuente ATX suministra energía adaptada a las necesidades específicas de cada componente mediante una organización estructurada del cableado:

- **Línea de +12V:**
  - Alimentación principal para las placas base de los Lenovo ubicadas en la planta inferior (utilizando bifurcadores comerciales para duplicar los conectores de alimentación de forma segura).
  - Suministro de 12V para los ventiladores del sistema, regulados mediante transistores MOSFET y controlados por la Raspberry Pi Pico.
- **Línea de +5V:**
  - Destinada a alimentar de forma estable la Raspberry Pi 4 y el switch de red, evitando la necesidad de adaptadores de corriente externos adicionales.

---
