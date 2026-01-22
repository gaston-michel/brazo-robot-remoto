# Configuración de Hardware

Este documento detalla la configuración del hardware del brazo robótico, incluyendo motores, drivers y conexiones.

---

## Tabla de Ejes

| Eje | Función | Motor | Driver | Microstepping | Corriente | Fuente |
|-----|---------|-------|--------|---------------|-----------|--------|
| J1 | Base (rotación) | NEMA17 + reductor 5:1 | TB6600 | 1/4 paso | 1.5A | 24V 5A |
| J2 | Hombro (pitch) | 2× NEMA24 (3.2 Nm) | 2× TB6600 | 1/4 paso | 3.5A | 36V 10A |
| J3 | Codo | NEMA17 + reductor 5:1 | TB6600 | 1/4 paso | 1.5A | 24V 5A |
| J4 | Muñeca pitch | NEMA17 | DRV8825 | 1/8-1/16 | ~1A | 12V 10A |
| J5 | Muñeca roll | NEMA17 | DRV8825 | 1/8-1/16 | ~1A | 12V 10A |
| J6 | Gripper/Pinza | NEMA17/Servo | DRV8825 | 1/8-1/16 | ~1A | 12V 10A |

---

## Drivers TB6600

### Configuración de DIP Switches

#### Microstepping (S1, S2, S3)

| S1 | S2 | S3 | Microstepping |
|----|----|----|---------------|
| ON | ON | ON | NC |
| ON | ON | OFF | 1 (paso completo) |
| ON | OFF | ON | 2/A |
| **ON** | **OFF** | **OFF** | **1/4** ← Recomendado J1, J2, J3 |
| OFF | ON | ON | 8 |
| OFF | ON | OFF | 16 |
| OFF | OFF | ON | 32 |
| OFF | OFF | OFF | 2/B |

#### Corriente (S4, S5, S6)

| S4 | S5 | S6 | Corriente |
|----|----|----|-----------|
| ON | ON | ON | 0.5A |
| **ON** | **ON** | **OFF** | **1.5A** ← J1, J3 |
| ON | OFF | ON | 2.0A |
| ON | OFF | OFF | 2.5A |
| OFF | ON | ON | 3.0A |
| **OFF** | **OFF** | **OFF** | **3.5A** ← J2 |
| OFF | ON | OFF | NC |
| OFF | OFF | ON | NC |

### Conexiones TB6600

```
        TB6600
    ┌─────────────┐
    │ ENA-        │◄──── GND Arduino
    │ ENA+        │◄──── ENABLE_PIN (38) *bajo = habilitado
    │ DIR-        │◄──── GND Arduino  
    │ DIR+        │◄──── DIR_PIN del eje
    │ PUL-        │◄──── GND Arduino
    │ PUL+        │◄──── STEP_PIN del eje
    ├─────────────┤
    │ B-          │◄──── Motor bobina B-
    │ B+          │◄──── Motor bobina B+
    │ A-          │◄──── Motor bobina A-
    │ A+          │◄──── Motor bobina A+
    ├─────────────┤
    │ GND         │◄──── Fuente GND
    │ VCC         │◄──── Fuente +24V/+36V
    └─────────────┘
```

---

## Drivers DRV8825

### Ajuste de Corriente

El DRV8825 usa un potenciómetro para ajustar la corriente. La fórmula es:

```
I_max = V_ref / 0.5
```

Para 1A de corriente máxima: `V_ref = 0.5V`

### Configuración de Microstepping (M0, M1, M2)

| M0 | M1 | M2 | Microstepping |
|----|----|----|---------------|
| LOW | LOW | LOW | Paso completo |
| HIGH | LOW | LOW | 1/2 paso |
| LOW | HIGH | LOW | 1/4 paso |
| **HIGH** | **HIGH** | **LOW** | **1/8 paso** ← Recomendado muñeca |
| LOW | LOW | HIGH | 1/16 paso |
| HIGH | HIGH | HIGH | 1/32 paso |

### Conexiones DRV8825

```
         DRV8825
    ┌───────────────┐
    │ ENABLE        │◄──── ENABLE_PIN (bajo = habilitado)
    │ M0            │◄──── Config microstepping
    │ M1            │◄──── Config microstepping
    │ M2            │◄──── Config microstepping
    │ RESET         │◄──── VCC (pullup)
    │ SLEEP         │◄──── VCC (siempre activo)
    │ STEP          │◄──── STEP_PIN del eje
    │ DIR           │◄──── DIR_PIN del eje
    ├───────────────┤
    │ VMOT          │◄──── +12V
    │ GND (motor)   │◄──── GND fuente
    │ B2            │◄──── Motor bobina B-
    │ B1            │◄──── Motor bobina B+
    │ A1            │◄──── Motor bobina A+
    │ A2            │◄──── Motor bobina A-
    │ VDD           │◄──── +5V (lógica)
    │ GND (lógica)  │◄──── GND Arduino
    └───────────────┘
```

---

## Asignación de Pines Arduino Mega

### Pines de Control de Motores

```c
// Definido en config.h
static const uint8_t STEP_PINS[6] = {54, 24, 26, 28, 30, 32};
static const uint8_t DIR_PINS[6]  = {55, 25, 27, 29, 31, 33};
static const uint8_t ENABLE_PIN = 38;  // Compartido
```

| Eje | STEP | DIR |
|-----|------|-----|
| J1 (Base) | 54 | 55 |
| J2 (Hombro) | 24 | 25 |
| J3 (Codo) | 26 | 27 |
| J4 (Muñeca P) | 28 | 29 |
| J5 (Muñeca R) | 30 | 31 |
| J6 (Gripper) | 32 | 33 |

### Pines de Finales de Carrera

```c
static const uint8_t ENDSTOP_MIN_PINS[6] = {A1, A2, A3, A4, A5, A6};
```

| Eje | Pin Endstop MIN |
|-----|-----------------|
| J1 | A1 |
| J2 | A2 |
| J3 | A3 |
| J4 | A4 |
| J5 | A5 |
| J6 | A6 |

---

## Fuentes de Alimentación

### Distribución

```
Fuente 1 (24V 5A)
    ├──► TB6600 J1 (Base)
    └──► TB6600 J3 (Codo)

Fuente 2 (36V 10A)
    └──► TB6600 J2 (×2) (Hombro)

Fuente 3 (12V 10A)
    ├──► DRV8825 J4 (Muñeca pitch)
    ├──► DRV8825 J5 (Muñeca roll)
    └──► DRV8825 J6 (Gripper)
```

### Notas Importantes

> ⚠️ **GND Común**: Todas las fuentes deben compartir GND con el Arduino Mega.

> ⚠️ **Condensadores**: Agregar condensadores electrolíticos (100-470µF) en la entrada de cada driver.

---

## Raspberry Pi 5

### Pantalla 3.5" TFT

- **Modelo**: 3.5inch RPi Display (waveshare/lcdwiki compatible)
- **Resolución**: 480×320 píxeles
- **Interfaz**: SPI + GPIO para táctil
- **Documentación**: [lcdwiki.com/3.5inch_RPi_Display](https://www.lcdwiki.com/3.5inch_RPi_Display)

### Conexión Serial Arduino

```
Raspberry Pi              Arduino Mega
┌──────────┐              ┌──────────┐
│ USB      │◄─────USB────►│ USB      │
│          │              │          │
└──────────┘              └──────────┘
     │
     └──► /dev/ttyACM0 @ 115200 bps
```

---

## Diagrama de Conexiones General

```
                             ┌─────────────────────────────────────────┐
                             │              RASPBERRY PI 5             │
                             │                                         │
                             │    GPIO ──────► Pantalla 3.5" TFT       │
                             │    USB  ──────► Arduino Mega            │
                             │                                         │
                             └─────────────────────┬───────────────────┘
                                                   │
                                              USB/Serial
                                                   │
                             ┌─────────────────────▼───────────────────┐
                             │            ARDUINO MEGA 2560            │
                             │                                         │
                             │  Pin 38 (EN) ──────┬─► Todos los drivers│
                             │                    │                    │
                             │  Pines STEP/DIR ───┼─► Ver tabla abajo  │
                             │                    │                    │
                             │  Pines A1-A6 ──────┼─► Finales carrera  │
                             │                    │                    │
                             │  GND ──────────────┼─► GND común        │
                             └────────────────────┼────────────────────┘
                                                  │
          ┌───────────────────────────────────────┼───────────────────────────────────────┐
          │                                       │                                       │
          ▼                                       ▼                                       ▼
   ┌────────────┐                          ┌────────────┐                          ┌────────────┐
   │  Fuente 1  │                          │  Fuente 2  │                          │  Fuente 3  │
   │  24V 5A    │                          │  36V 10A   │                          │  12V 10A   │
   └──────┬─────┘                          └──────┬─────┘                          └──────┬─────┘
          │                                       │                                       │
     ┌────┴────┐                                  │                               ┌───────┼───────┐
     │         │                                  │                               │       │       │
     ▼         ▼                                  ▼                               ▼       ▼       ▼
┌─────────┐ ┌─────────┐                    ┌───────────────┐                ┌───────┐ ┌───────┐ ┌───────┐
│ TB6600  │ │ TB6600  │                    │ 2× TB6600     │                │DRV8825│ │DRV8825│ │DRV8825│
│   J1    │ │   J3    │                    │     J2        │                │  J4   │ │  J5   │ │  J6   │
└────┬────┘ └────┬────┘                    └───────┬───────┘                └───┬───┘ └───┬───┘ └───┬───┘
     │           │                                 │                            │         │         │
     ▼           ▼                                 ▼                            ▼         ▼         ▼
┌─────────┐ ┌─────────┐                    ┌───────────────┐                ┌───────┐ ┌───────┐ ┌───────┐
│ NEMA17  │ │ NEMA17  │                    │  2× NEMA24    │                │NEMA17 │ │NEMA17 │ │NEMA17 │
│  5:1    │ │  5:1    │                    │   (3.2 Nm)    │                │       │ │       │ │/Servo │
│  Base   │ │  Codo   │                    │    Hombro     │                │Muñeca │ │Muñeca │ │Gripper│
└─────────┘ └─────────┘                    └───────────────┘                │ Pitch │ │ Roll  │ │       │
                                                                            └───────┘ └───────┘ └───────┘
```

---

## Notas de Seguridad

1. **Parada de emergencia**: El pin ENABLE (38) en HIGH desactiva todos los drivers
2. **Finales de carrera**: Configurados con INPUT_PULLUP, activos en LOW
3. **Límites de software**: Posición mínima 0, máxima 100000 pasos
4. **Timeouts**: Movimiento 10s, Homing 20s

---

## Lista de Materiales (BOM)

### Electrónica

| Cantidad | Componente | Notas |
|----------|------------|-------|
| 1 | Arduino Mega 2560 | |
| 1 | Raspberry Pi 5 8GB | |
| 1 | Pantalla 3.5" TFT | SPI, táctil |
| 5 | TB6600 Stepper Driver | 1 sobrante |
| 6 | DRV8825 Stepper Driver | 4 sobrantes |
| 2 | NEMA24 3.2 Nm | Para J2 |
| 3 | NEMA17 + reductor 5:1 | J1, J3 + repuesto |
| 4 | NEMA17 | J4, J5, J6 + repuesto |
| 6 | Final de carrera (microswitch) | |

### Fuentes

| Cantidad | Especificación |
|----------|----------------|
| 2 | 24V 5A |
| 1 | 36V 10A |
| 1 | 12V 10A |
