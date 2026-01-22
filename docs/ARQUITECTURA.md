# Arquitectura del Sistema

Este documento describe la arquitectura técnica del sistema de control remoto del brazo robótico.

## Diagrama General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CAPA DE USUARIO                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [Usuario Remoto]                        [Usuario Local]                   │
│         │                                       │                           │
│         │ HTTP/WebSocket                        │ Pantalla Táctil           │
│         │ (por desarrollar)                     │ 3.5" Display              │
│         ▼                                       ▼                           │
│   ┌───────────┐                          ┌───────────────┐                  │
│   │  Servidor │ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ►│   Interfaz    │                  │
│   │    Web    │                          │  CustomTkinter│                  │
│   └───────────┘                          └───────────────┘                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RASPBERRY PI 5 (8GB)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   /pi-firmware/                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │   ┌─────────────┐     ┌──────────────┐     ┌──────────────────┐     │   │
│   │   │   app.py    │────►│ robot_client │────►│  broker/broker   │     │   │
│   │   │  (RobotApp) │     │    .py       │     │      .py         │     │   │
│   │   └─────────────┘     └──────────────┘     └────────┬─────────┘     │   │
│   │         │                                           │               │   │
│   │         │                                           │ Serial        │   │
│   │   ┌─────▼─────┐                                     │ /dev/ttyACM0  │   │
│   │   │    ui/    │                                     │               │   │
│   │   │  tabs/    │                                     │               │   │
│   │   │components/│                                     │               │   │
│   │   └───────────┘                                     │               │   │
│   │                                                     │               │   │
│   └─────────────────────────────────────────────────────┼───────────────┘   │
│                                                         │                   │
└─────────────────────────────────────────────────────────┼───────────────────┘
                                                          │
                                                          │ UART 115200 bps
                                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ARDUINO MEGA 2560                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   /mega-firmware/                                                           │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │   mega-firmware.ino                                                 │   │
│   │   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐      │   │
│   │   │  setup() │───►│ parser   │───►│  motion  │───►│telemetry │      │   │
│   │   │  loop()  │    │          │    │          │    │          │      │   │
│   │   └──────────┘    └──────────┘    └────┬─────┘    └──────────┘      │   │
│   │                                        │                            │   │
│   │                              ┌─────────▼─────────┐                  │   │
│   │                              │   AccelStepper    │                  │   │
│   │                              │   (6 instancias)  │                  │   │
│   │                              └─────────┬─────────┘                  │   │
│   │                                        │                            │   │
│   └────────────────────────────────────────┼────────────────────────────┘   │
│                                            │                                │
└────────────────────────────────────────────┼────────────────────────────────┘
                                             │
                           GPIO: STEP, DIR, ENABLE pins
                                             │
┌────────────────────────────────────────────┼────────────────────────────────┐
│                          ELECTRÓNICA DE POTENCIA                            │
├────────────────────────────────────────────┼────────────────────────────────┤
│                                            ▼                                │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                          DRIVERS                                    │   │
│   │                                                                     │   │
│   │   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │   │
│   │   │ TB6600  │ │ TB6600  │ │ TB6600  │ │ DRV8825 │ │ DRV8825 │       │   │
│   │   │   J1    │ │ J2 (×2) │ │   J3    │ │ J4      │ │ J5/J6   │       │   │
│   │   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘       │   │
│   │        │           │           │           │           │            │   │
│   └────────┼───────────┼───────────┼───────────┼───────────┼────────────┘   │
│            │           │           │           │           │                │
│            ▼           ▼           ▼           ▼           ▼                │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                          MOTORES                                    │   │
│   │                                                                     │   │
│   │   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │   │
│   │   │ NEMA17  │ │ NEMA24  │ │ NEMA17  │ │ NEMA17  │ │ NEMA17  │       │   │
│   │   │  5:1    │ │  ×2     │ │  5:1    │ │         │ │ ×2      │       │   │
│   │   │  Base   │ │ Hombro  │ │  Codo   │ │ Muñeca P│ │Muñeca/G │       │   │
│   │   └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘       │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Flujo de Datos

### Control de Motor (Usuario → Motor)

```
1. Usuario toca slider en UI
         │
         ▼
2. app.py captura evento
         │
         ▼
3. robot_client.send_command("M1100")
         │
         ▼
4. Serial Broker (opcional)
   - Convierte grados a pasos
   - Envía ACK al cliente
         │
         ▼
5. Arduino recibe "M1100\n"
         │
         ▼
6. parser.cpp → parseLine()
         │
         ▼
7. motion.cpp → handleMoveRelative()
         │
         ▼
8. AccelStepper → steppers[0].move(100)
         │
         ▼
9. GPIO pulsos STEP al driver TB6600
         │
         ▼
10. Motor NEMA17 gira
```

### Telemetría (Motor → Usuario)

```
1. loop() → updateMotors() detecta fin movimiento
         │
         ▼
2. Serial.print("D1\n") (Done axis 1)
         │
         ▼
3. Raspberry recibe por serial
         │
         ▼
4. robot_client.update_status()
         │
         ▼
5. UI actualiza posición mostrada
```

---

## Módulos Principales

### Raspberry Pi (`/pi-firmware`)

| Archivo | Responsabilidad |
|---------|-----------------|
| `main.py` | Entry point de la aplicación |
| `app.py` | Clase principal `RobotApp`, inicialización y UI |
| `robot_client.py` | Comunicación serial con Arduino |
| `config.py` | Constantes de configuración |
| `path_manager.py` | Gestión de trayectorias guardadas |
| `broker/broker.py` | Intermediario serial PC↔Arduino |
| `ui/theme.py` | Colores y estilos de la interfaz |
| `ui/tabs/` | Implementación de cada pestaña |
| `ui/components/` | Componentes reutilizables (sliders, botones) |

### Arduino Mega (`/mega-firmware`)

| Archivo | Responsabilidad |
|---------|-----------------|
| `mega-firmware.ino` | Setup y loop principal |
| `config.h` | Pines, constantes y límites |
| `parser.cpp/h` | Parsing de comandos ASCII |
| `motion.cpp/h` | Control de motores con AccelStepper |
| `telemetry.cpp/h` | Reporte de estado |
| `utils.cpp/h` | Utilidades (debug, watchdog) |

---

## Hilos y Concurrencia

### Raspberry Pi

```
┌──────────────────────────────────────────────────────────┐
│                    Proceso Principal                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│   [Main Thread]              [Status Thread]             │
│   ┌──────────────┐          ┌──────────────┐             │
│   │ CustomTkinter│          │ Polling Loop │             │
│   │  Event Loop  │◄─────────│ cada 200ms   │             │
│   │              │  after() │              │             │
│   └──────────────┘          └──────────────┘             │
│                                                          │
│   - Maneja UI                - Envía "S\n" al robot      │
│   - Responde a eventos       - Lee estado                │
│   - Thread-safe updates      - Actualiza self.axes       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Arduino

Arduino ejecuta en un solo hilo, pero el loop está diseñado para ser no bloqueante:

```cpp
void loop() {
    // 1. Procesar comandos (no bloqueante)
    if (Serial.available()) { ... }
    
    // 2. Actualizar motores (AccelStepper.run())
    updateMotors();
    
    // 3. Verificar timeouts
    checkTimeouts();
}
```

---

## Consideraciones de Tiempo Real

- **Arduino**: Loop sin delays, AccelStepper maneja timing de pulsos
- **Comunicación**: 115200 bps, comandos cortos (~5-10 caracteres)
- **UI**: Polling cada 200ms para balance entre responsividad y carga
- **Endstops**: Verificados en cada iteración de `updateMotors()`
