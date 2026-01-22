# Protocolo de Comunicación Serial

Este documento describe el protocolo ASCII utilizado para la comunicación entre la Raspberry Pi y el Arduino Mega.

---

## Configuración

- **Baudrate**: 115200 bps
- **Formato**: 8N1 (8 bits, sin paridad, 1 bit de stop)
- **Terminador**: `\n` (newline)
- **Puerto típico**: `/dev/ttyACM0`

---

## Comandos

### Movimiento Relativo

Mueve un eje una cantidad de pasos relativa a su posición actual.

```
M<eje><pasos>
```

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `eje` | Número de eje (1-6) | `1` = Base |
| `pasos` | Pasos a mover (positivo/negativo) | `100`, `-50` |

**Ejemplos**:
```
M1100     → Mover eje 1, +100 pasos
M3-200    → Mover eje 3, -200 pasos
```

**Respuestas**:
- `D<eje>` → Movimiento completado (Done)
- `ENDSTOP<eje>` → Final de carrera alcanzado
- `ERR2` → Eje inválido
- `ERR4` → Fuera de límites
- `ERR6` → Endstop ya activo

---

### Movimiento Absoluto

Mueve un eje a una posición absoluta en pasos.

```
A<eje><posición>
```

**Ejemplos**:
```
A11000    → Mover eje 1 a posición 1000
A40       → Mover eje 4 a posición 0
```

**Respuestas**: Igual que movimiento relativo.

---

### Homing

Ejecuta la secuencia de homing (buscar final de carrera mínimo).

```
H<eje>
```

**Ejemplos**:
```
H1        → Homing del eje 1
H3        → Homing del eje 3
```

**Comportamiento**:
1. Motor se mueve lentamente hacia el mínimo (1/4 de velocidad normal)
2. Al detectar endstop LOW, se detiene
3. Posición se resetea a 0

**Respuestas**:
- (sin respuesta explícita si exitoso)
- `ERR2` → Eje inválido
- `ERR5` → Timeout de homing (>20s)

---

### Parada de Emergencia

Detiene todos los motores inmediatamente deshabilitando los drivers.

```
E
```

**Comportamiento**: Pone ENABLE_PIN en HIGH (drivers deshabilitados).

---

### Kill Axis

Detiene el movimiento de un eje específico.

```
K<eje>
```

**Ejemplos**:
```
K2        → Detener eje 2
```

**Respuestas**:
- `D<eje>` → Eje detenido
- `ERR2` → Eje inválido

---

### Configuración de Perfil

Configura velocidad o aceleración para todos los ejes.

```
P<param><valor>
```

| Param | Descripción | Unidad |
|-------|-------------|--------|
| `V` | Velocidad máxima | pasos/segundo |
| `A` | Aceleración | pasos/segundo² |

**Ejemplos**:
```
PV1500    → Velocidad máxima 1500 pasos/s
PA800     → Aceleración 800 pasos/s²
```

**Respuestas**:
- (sin respuesta si exitoso)
- `ERR1` → Parámetro inválido

---

### Consulta de Estado

Solicita el estado actual del robot.

```
S
```

**Respuesta** (una línea):
```
State:<estado> X:<pos> Y:<pos> Z:<pos> A:<pos> B:<pos> C:<pos> Endstops:<bits>
```

| Campo | Descripción | Valores |
|-------|-------------|---------|
| `State` | Estado actual | `IDLE`, `MOVING`, `ALARM`, `HOMING` |
| `X,Y,Z,A,B,C` | Posición de cada eje | Valor numérico (pasos) |
| `Endstops` | Estado de finales de carrera | 6 bits, ej: `100000` |

**Ejemplo de respuesta**:
```
State:IDLE X:0.00 Y:1500.00 Z:200.00 A:0.00 B:0.00 C:0.00 Endstops:000000
```

---

### Reset

Resetea el estado de alarma (si está implementado).

```
R
```

---

### Test Predefinido

Ejecuta una rutina de prueba predefinida.

```
T<id>
```

**Ejemplos**:
```
T1        → Ejecutar test 1 (cuadrado)
T2        → Ejecutar test 2 (círculo)
```

---

## Códigos de Error

| Código | Significado |
|--------|-------------|
| `ERR1` | Comando inválido (BadCmd) |
| `ERR2` | Eje inválido (BadAxis) |
| `ERR4` | Posición fuera de límites |
| `ERR5` | Timeout |
| `ERR6` | Endstop ya activo |

---

## Serial Broker (Opcional)

El broker (`broker/broker.py`) actúa como intermediario entre un PC remoto y el Arduino, añadiendo funcionalidad:

### Heartbeat

```
C         → Envía heartbeat
c         ← Respuesta del broker
```

### Conversión de Unidades

El broker puede convertir grados a pasos:

```
M190G     → Mover eje 1, 90 grados
M1100S    → Mover eje 1, 100 pasos (explícito)
```

La conversión usa la configuración de `config.yaml`:

```yaml
axes:
  1:
    steps_per_rev: 200
    gear_ratio: 5
```

Fórmula: `pasos = grados × steps_per_rev × gear_ratio / 360`

### ACK Inmediato

El broker responde `OK\n` inmediatamente al recibir un comando válido, antes de que el Arduino responda.

---

## Diagrama de Secuencia

### Movimiento Normal

```
 Raspberry Pi              Arduino Mega
      │                         │
      │    M1100\n             │
      ├────────────────────────►│
      │                         │ (motor empieza a moverse)
      │                         │
      │                         │ (motor termina)
      │         D1\n            │
      │◄────────────────────────┤
      │                         │
```

### Movimiento con Endstop

```
 Raspberry Pi              Arduino Mega
      │                         │
      │    M1-500\n            │
      ├────────────────────────►│
      │                         │ (motor empieza)
      │                         │ (endstop detectado)
      │     ENDSTOP1\n          │
      │◄────────────────────────┤
      │                         │
```

### Polling de Estado

```
 Raspberry Pi              Arduino Mega
      │                         │
      │    S\n                  │
      ├────────────────────────►│
      │                         │
      │ State:IDLE X:0 ...      │
      │◄────────────────────────┤
      │                         │
         (repite cada 200ms)
```

---

## Notas de Implementación

### Thread Safety

En `robot_client.py`, la comunicación serial está protegida por un lock:

```python
with self.lock:
    self.serial.write(cmd.encode())
    response = self.serial.readline()
```

### Timeout

El timeout de lectura serial es de 1 segundo. Comandos sin respuesta esperada no bloquean indefinidamente.

### Formato de Números

- Posiciones se envían como enteros o float con 2 decimales
- El Arduino usa `toInt()` para parsing, ignorando decimales
