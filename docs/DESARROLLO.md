# Guía de Desarrollo

Esta guía proporciona información para desarrolladores que quieran contribuir al proyecto.

---

## Estructura del Proyecto

```
software/
├── README.md                 # Documentación principal
├── docs/                     # Documentación técnica
│   ├── ARQUITECTURA.md
│   ├── HARDWARE.md
│   ├── PROTOCOLO.md
│   └── DESARROLLO.md
├── mega-firmware/            # Firmware Arduino
│   ├── mega-firmware.ino
│   ├── config.h
│   ├── parser.cpp/h
│   ├── motion.cpp/h
│   ├── telemetry.cpp/h
│   └── utils.cpp/h
├── pi-firmware/              # Aplicación Raspberry Pi
│   ├── main.py
│   ├── app.py
│   ├── robot_client.py
│   ├── config.py
│   ├── path_manager.py
│   ├── requirements.txt
│   ├── broker/
│   │   ├── broker.py
│   │   └── config.yaml
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── theme.py
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── axis_slider.py
│   │   │   └── icon_tab_bar.py
│   │   └── tabs/
│   │       ├── __init__.py
│   │       ├── control_tab.py
│   │       ├── settings_tab.py
│   │       ├── tests_tab.py
│   │       └── paths_tab.py
│   └── assets/
│       └── icons/
├── test_driver/              # Código de prueba para drivers
└── test_drivers/             # Tests adicionales
```

---

## Configuración del Entorno

### Arduino

1. Instalar [Arduino IDE 2.0+](https://www.arduino.cc/en/software)
2. Instalar la librería **AccelStepper** desde el Library Manager
3. Seleccionar placa: `Arduino Mega or Mega 2560`
4. Seleccionar puerto

### Raspberry Pi

```bash
# Clonar repositorio
git clone https://github.com/<usuario>/brazo-robot-remoto.git
cd brazo-robot-remoto/pi-firmware

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

**Dependencias principales**:
- `customtkinter` - Framework UI
- `pyserial` - Comunicación serial
- `pyyaml` - Configuración del broker

### Desarrollo en Windows/PC

Para desarrollo sin hardware, se puede:

1. Usar un Arduino conectado por USB para probar la UI
2. Modificar `SERIAL_PORT` en `config.py` (ej: `COM3` en Windows)
3. Ejecutar `python main.py`

---

## Convenciones de Código

### Python

- **Estilo**: PEP 8
- **Docstrings**: Google style
- **Nombres**: 
  - Clases: `PascalCase`
  - Funciones/variables: `snake_case`
  - Constantes: `UPPER_SNAKE_CASE`

```python
class RobotClient:
    """Cliente para comunicación con el robot.
    
    Args:
        port: Puerto serial (ej: '/dev/ttyACM0')
        baud: Velocidad en baudios
    """
    
    def __init__(self, port: str = '/dev/ttyACM0', baud: int = 115200):
        self.port = port
        self.baud = baud
```

### C++ (Arduino)

- **Estilo**: Similar a Google C++ Style Guide
- **Nombres**:
  - Funciones: `camelCase`
  - Constantes: `UPPER_SNAKE_CASE`
  - Variables globales: evitar, usar `static`

```cpp
void handleMoveRelative(const String &line) {
    uint8_t axis = line.charAt(1) - '1';
    long value = line.substring(2).toInt();
    // ...
}
```

---

## Agregar un Nuevo Comando

### 1. Arduino - Parser

En `parser.cpp`, agregar el caso en `parseLine()`:

```cpp
void parseLine(const String &line) {
    char cmd = line.charAt(0);
    switch (cmd) {
        case 'M': handleMoveRelative(line); break;
        case 'A': handleMoveAbsolute(line); break;
        case 'H': handleHoming(line); break;
        // Agregar nuevo comando:
        case 'N': handleNuevoComando(line); break;
        default:
            Serial.print("ERR1\n");
    }
}
```

### 2. Arduino - Handler

Implementar la función en el módulo correspondiente:

```cpp
// En motion.cpp o nuevo archivo
void handleNuevoComando(const String &line) {
    // Parsear parámetros
    // Ejecutar lógica
    // Enviar respuesta
    Serial.print("OK\n");
}
```

### 3. Python - RobotClient

Agregar método en `robot_client.py`:

```python
def nuevo_comando(self, param1, param2):
    """Ejecuta el nuevo comando.
    
    Args:
        param1: Descripción
        param2: Descripción
    
    Returns:
        bool: True si exitoso
    """
    cmd = f"N{param1}{param2}"
    return self.send_command(cmd)
```

### 4. Broker (si aplica)

Si el comando necesita conversión de unidades, agregar regex y handler en `broker.py`.

---

## Agregar una Nueva Pestaña UI

### 1. Crear archivo de tab

En `ui/tabs/nueva_tab.py`:

```python
import customtkinter as ctk
from ui.theme import COLORS

class NuevaTab(ctk.CTkFrame):
    """Pestaña para nueva funcionalidad."""
    
    def __init__(self, parent, client):
        super().__init__(parent, fg_color=COLORS["background"])
        self.client = client
        self._build_ui()
    
    def _build_ui(self):
        # Construir widgets
        label = ctk.CTkLabel(self, text="Nueva Pestaña")
        label.pack(pady=20)
```

### 2. Registrar en __init__.py

En `ui/tabs/__init__.py`:

```python
from .control_tab import ControlTab
from .settings_tab import SettingsTab
from .tests_tab import TestsTab
from .paths_tab import PathsTab
from .nueva_tab import NuevaTab  # Agregar
```

### 3. Agregar a app.py

```python
from ui.tabs import ControlTab, SettingsTab, TestsTab, PathsTab, NuevaTab

# En _build_ui():
tabs = [
    ("Control", os.path.join(ASSETS_DIR, "control.png"), self._build_control_tab),
    # ...
    ("Nueva", os.path.join(ASSETS_DIR, "nueva.png"), self._build_nueva_tab),
]

def _build_nueva_tab(self, parent):
    self.nueva_tab = NuevaTab(parent, self.client)
    return self.nueva_tab
```

### 4. Agregar ícono

Crear `assets/icons/nueva.png` (recomendado: 24x24 píxeles, fondo transparente).

---

## Testing

### Arduino

Para probar el firmware sin el hardware completo:

1. Conectar Arduino a PC
2. Abrir Serial Monitor (115200 baud)
3. Enviar comandos manualmente:
   ```
   S
   M1100
   M1-100
   ```

### Python

```bash
# Ejecutar desde pi-firmware/
python -c "
from robot_client import RobotClient
client = RobotClient(port='/dev/ttyACM0')
print('Conectando...')
if client.connect():
    print('Conectado!')
    client.update_status()
    print(f'Estado: {client.status}')
    print(f'Ejes: {client.axes}')
    client.disconnect()
"
```

---

## Troubleshooting

### "Permission denied" en puerto serial (Linux)

```bash
sudo usermod -a -G dialout $USER
# Reiniciar sesión
```

### La pantalla táctil no responde

1. Verificar instalación de drivers según [lcdwiki](https://www.lcdwiki.com/3.5inch_RPi_Display)
2. Ejecutar calibración táctil si es necesario

### Los motores no se mueven

1. Verificar que `ENABLE_PIN` está en LOW (habilitado)
2. Verificar conexiones STEP/DIR
3. Verificar alimentación de drivers
4. Probar con `arduino_tester.py`

### Comunicación serial inestable

1. Verificar cable USB
2. Verificar que no hay otro proceso usando el puerto
3. Aumentar timeout en `robot_client.py`

---

## Roadmap

### En Progreso
- [ ] Detalles finales de la interfaz UI
- [ ] Construcción mecánica del brazo

### Próximos Pasos
- [ ] Servidor web para acceso remoto
- [ ] Autenticación de usuarios
- [ ] Streaming de video
- [ ] Cinemática inversa

### Ideas Futuras
- [ ] Aplicación móvil
- [ ] Integración con ROS2
- [ ] Visión artificial para pick & place automático

---

## Contacto

Para dudas o contribuciones, contactar a:

**Gastón Daniel Michel**  
GROVA - UTN FRSN
