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
