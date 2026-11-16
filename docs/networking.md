
# Arquitectura y Diseño de Red

## 1. Situación inicial (Topología plana)

Antes de desplegar el homelab, la red doméstica dependía integramente del **HGu de la operadora** actuando como ONT, router, firewall y AP. Todos los cliente, tanto clableados a través de un switch no gestionable coomo inalámbricos, convivían dentro de un único dominio de broadcast y subred plana.

Esta topología presenta varias limitaciones críticas para alojar servicios autoalojados de forma segura:

* **Ausencia de segmentación (Red plana):** Los dispositivos IoT, equipos personales y futuros nodos del laboratorio compartían la misma subred sin aislamiento a nivel de capa 2 ni control de tráfico entre ellos.
* **Limitaciones de gestión y enrutamiento:** El firmware del router de operadora restringía la creación de VLANs (802.1Q), reglas granulares de firewall y el despliegue nativo de túneles VPN seguros para acceso remoto.
* **Escalabilidad reducida:** Al no contar con conmutación gestionable ni separación lógica de tráfico, añadir servidores o servicios expuestos suponía un riesgo directo para los equipos principales de la red doméstica.

<div align="center">
    <img src="/assets/diagrams/DiagramaRedAntes.png" alt="Estado actual del homelab" width="650" />
</div>

---

## 2. Arquitectura objetivo (Diseño segmentado — Planificado)

Para resolver las limitaciones de la red plana y preparar una base segura para el homelab, se ha diseñado una topología segmentada mediante **VLANs (802.1Q)** delegando la gestión principal de la red a un router propio (**GL.iNet GL-MT3000 / Beryl AX**) y conmutación gestionable (**Zyxel GS1200-8**).### Decisiones clave de diseño

| Componente / Área | Decisión adoptada | Justificación técnica |
| :--- | :--- | :--- |
| **Router principal** | GL.iNet GL-MT3000 (Beryl AX) | Asume el rol de gateway, firewall entre VLANs, punto de acceso Wi-Fi principal y servidor VPN (WireGuard). |
| **Integración ISP** | HGU con Wi-Fi apagado y DMZ al Beryl | Mantiene la conectividad de fibra de Movistar evitando interferencias inalámbricas y simplificando el reenvío de puertos hacia el nuevo firewall (asumiendo doble NAT controlado). |
| **Conmutación** | Zyxel GS1200-8 conectado vía Trunk 802.1Q | Permite transportar múltiples VLANs desde el puerto LAN del Beryl y asignar puertos individuales en modo *access* según el perfil de cada equipo. |
| **Aislamiento del Lab** | Nodos en VLAN dedicada (`VLAN 20`) | Separa los servicios de infraestructura (Raspberry Pi 4 para DNS/logs y nodos Lenovo V530s) de los equipos de uso diario. |
| **Equipos personales** | Switch anterior y PC en `VLAN 30` | Reutiliza el switch no gestionable existente aislándolo en una VLAN de confianza independiente del laboratorio. |
| **Cobertura Cocina** | Repetidor TP-Link sobre SSID de confianza | Solución pragmática inicial para extender cobertura inalámbrica sin obra; migrable a punto de acceso cableado si se requiere mayor rendimiento. |