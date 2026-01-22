# 🤖 Brazo Robótico Remoto - Laboratorio GROVA

<div align="center">

![Estado](https://img.shields.io/badge/Estado-En%20Desarrollo-yellow)
![Licencia](https://img.shields.io/badge/Licencia-Académico-blue)
![Universidad](https://img.shields.io/badge/UTN-FRSN-green)

**Sistema de control remoto para brazo robótico de 6 grados de libertad accesible a través de internet.**

[Arquitectura](#-arquitectura) • [Hardware](#-hardware) • [Software](#-componentes-de-software) • [Instalación](#-instalación) • [Documentación](#-documentación)

</div>

---

## 📋 Descripción del Proyecto

Este proyecto desarrolla un **laboratorio remoto** que permite a usuarios externos controlar un brazo robótico de 6 DOF a través de internet. Forma parte del trabajo realizado con el **Grupo de Robótica y Visión Artificial (GROVA)** de la [UTN Facultad Regional San Nicolás](https://www.frsn.utn.edu.ar/).

El diseño mecánico está basado en el proyecto open-source [BCN3D Moveo](https://github.com/BCN3D/BCN3D-Moveo), con modificaciones para adaptarlo a las necesidades del laboratorio remoto.

### Objetivos

- 🌐 Permitir acceso remoto al laboratorio de robótica vía internet
- 🎓 Facilitar el aprendizaje práctico de robótica para estudiantes
- 🔧 Desarrollar una plataforma extensible para experimentos de control

---

## 🏗️ Arquitectura

El sistema se compone de tres capas principales:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USUARIO REMOTO                               │
│                    (Navegador Web / Cliente)                        │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ Internet (por desarrollar)
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                        RASPBERRY PI 5                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌────────────────┐  │
│  │   Interfaz UI   │◄──►│  Robot Client   │◄──►│  Serial Broker │  │
│  │  (CustomTkinter)│    │                 │    │                │  │
│  └─────────────────┘    └─────────────────┘    └───────┬────────┘  │
│                                                        │ UART      │
└────────────────────────────────────────────────────────┼───────────┘
                                                         │
┌────────────────────────────────────────────────────────┼───────────┐
│                       ARDUINO MEGA 2560                │           │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐          │           │
│  │  Parser  │◄──►│  Motion  │◄──►│ Telemetry│◄─────────┘           │
│  └──────────┘    └────┬─────┘    └──────────┘                      │
│                       │                                            │
│              ┌────────┴────────┐                                   │
│              │  AccelStepper   │                                   │
│              │   (6 ejes)      │                                   │
│              └────────┬────────┘                                   │
└───────────────────────┼────────────────────────────────────────────┘
                        │ STEP/DIR/EN
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DRIVERS Y MOTORES                                │
│   TB6600 (J1,J2,J3) + DRV8825 (J4,J5,J6) → NEMA17/NEMA24           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔩 Hardware

### Componentes Principales

| Componente | Modelo | Descripción |
|------------|--------|-------------|
| Microcontrolador | Arduino Mega 2560 | Control de motores en tiempo real |
| Computadora | Raspberry Pi 5 (8GB) | Interfaz, comunicación y servidor web |
| Display | 3.5" RPi Display | Pantalla táctil para control local |

### Configuración de Ejes

| Eje | Función | Motor | Driver | Fuente |
|-----|---------|-------|--------|--------|
| J1 | Base (rotación) | NEMA17 + reductor 5:1 | TB6600 | 24V 5A |
| J2 | Hombro | 2× NEMA24 (3.2 Nm) | 2× TB6600 | 36V 10A |
| J3 | Codo | NEMA17 + reductor 5:1 | TB6600 | 24V 5A |
| J4 | Muñeca pitch | NEMA17 | DRV8825 | 12V 10A |
| J5 | Muñeca roll | NEMA17 | DRV8825 | 12V 10A |
| J6 | Gripper/Pinza | NEMA17/Servo | DRV8825 | 12V 10A |

> 📄 Ver [docs/HARDWARE.md](docs/HARDWARE.md) para configuración detallada de drivers y conexiones.

---

## 💻 Componentes de Software

### `/mega-firmware` - Firmware Arduino

Firmware en C++ para Arduino Mega 2560 que maneja:

- **Control de motores**: Librería AccelStepper con perfiles de aceleración
- **Parser de comandos**: Protocolo ASCII simple y robusto
- **Homing**: Secuencia automática con finales de carrera
- **Telemetría**: Reporte de estado en tiempo real
- **Seguridad**: Parada de emergencia y límites de posición

### `/pi-firmware` - Aplicación Raspberry Pi

Aplicación Python que incluye:

- **Interfaz gráfica**: CustomTkinter optimizada para pantalla táctil 3.5"
- **Robot Client**: Comunicación serial con Arduino
- **Serial Broker**: Intermediario para conversión de unidades y protocolo
- **Path Manager**: Gestión de trayectorias predefinidas

#### Pestañas de la UI

| Pestaña | Función |
|---------|---------|
| Control | Jog manual de cada eje, visualización de posición |
| Settings | Configuración de velocidad y aceleración |
| Tests | Ejecución de rutinas de prueba predefinidas |
| Paths | Gestión y reproducción de trayectorias |

---

## 📦 Instalación

### Requisitos Previos

- Python 3.11+
- Arduino IDE 2.0+

### Raspberry Pi

```bash
cd pi-firmware
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python main.py
```

### Arduino Mega

1. Abrir `mega-firmware/mega-firmware.ino` en Arduino IDE
2. Seleccionar placa "Arduino Mega 2560"
3. Cargar el firmware

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md) | Arquitectura detallada del sistema |
| [docs/HARDWARE.md](docs/HARDWARE.md) | Configuración de hardware y conexiones |
| [docs/PROTOCOLO.md](docs/PROTOCOLO.md) | Protocolo de comunicación serial |
| [docs/DESARROLLO.md](docs/DESARROLLO.md) | Guía para contribuidores |

---

## 📊 Estado del Proyecto

| Componente | Estado |
|------------|--------|
| Mecánica (estructura) | 🔴 En construcción |
| Firmware Arduino | 🟢 Implementado |
| Comunicación Mega ↔ RPi | 🟢 Implementado |
| Interfaz UI | 🟡 Avanzado (detalles pendientes) |
| Servidor Web Remoto | 🔴 Por desarrollar |

---

## 📄 Licencia

Este proyecto es desarrollado en el contexto académico del grupo de investigación GROVA de la UTN FRSN. Consultar con los autores para uso fuera del ámbito educativo.

---

<div align="center">

**[⬆ Volver arriba](#-brazo-robótico-remoto---laboratorio-grova)**

</div>
