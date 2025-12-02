#include "motion.h"
#include "config.h"
#include "utils.h"

// Create AccelStepper objects for each axis
// DRIVER mode: STEP pin, DIR pin
AccelStepper steppers[6] = {
  AccelStepper(AccelStepper::DRIVER, STEP_PINS[0], DIR_PINS[0]),
  AccelStepper(AccelStepper::DRIVER, STEP_PINS[1], DIR_PINS[1]),
  AccelStepper(AccelStepper::DRIVER, STEP_PINS[2], DIR_PINS[2]),
  AccelStepper(AccelStepper::DRIVER, STEP_PINS[3], DIR_PINS[3]),
  AccelStepper(AccelStepper::DRIVER, STEP_PINS[4], DIR_PINS[4]),
  AccelStepper(AccelStepper::DRIVER, STEP_PINS[5], DIR_PINS[5])
};

// Track if stepper was moving in previous cycle to detect end of motion
static bool wasMoving[6] = {false, false, false, false, false, false};

void initMotion() {
  // Enable all drivers
  pinMode(ENABLE_PIN, OUTPUT);
  digitalWrite(ENABLE_PIN, LOW); // LOW = enabled

  // Configure each endstop
  for (uint8_t i = 0; i < 6; i++) {
    pinMode(ENDSTOP_MIN_PINS[i], INPUT_PULLUP);
  }

  // Configure each stepper
  for (uint8_t i = 0; i < 6; i++) {
    steppers[i].setMaxSpeed(DEFAULT_SPEED_STEPS_PER_SEC);
    steppers[i].setAcceleration(DEFAULT_ACCEL_STEPS_PER_SEC2);
    steppers[i].setCurrentPosition(0);
    wasMoving[i] = false;
  }
}

void updateMotors() {
  // Run each stepper and check end-of-motion to send confirmation
  for (uint8_t i = 0; i < 6; i++) {
    // Check endstops before moving - considerando la dirección
    bool endstopMinActive = (digitalRead(ENDSTOP_MIN_PINS[i]) == LOW);
    
    if (endstopMinActive) {
      // Si el endstop mínimo está activo, verificar si el movimiento es positivo
      long distanceToGo = steppers[i].distanceToGo();
      
      if (distanceToGo > 0) {
        // Movimiento positivo: permitir continuar (nos alejamos del límite)
        // No detener el motor
      } else if (distanceToGo < 0) {
        // Movimiento negativo: detener (nos acercamos más al límite)
        steppers[i].stop();
        Serial.print("ENDSTOP");
        Serial.print(i + 1);
        Serial.print("\n");
        wasMoving[i] = false;
        continue;
      } else {
        // No hay movimiento pendiente
        wasMoving[i] = false;
        continue;
      }
    }

    bool moving = (steppers[i].distanceToGo() != 0);
    steppers[i].run();
    // If it was moving and now stopped, send confirmation
    if (wasMoving[i] && !moving) {
      Serial.print("D");
      Serial.print(i + 1);
      Serial.print("\n");
    }
    wasMoving[i] = moving;
  }
}

void handleMoveRelative(const String &line) {
  // Format: M<eje><signed_steps>
  digitalWrite(ENABLE_PIN, LOW);
  uint8_t axis = line.charAt(1) - '1';
  long value = line.substring(2).toInt();

  if (axis >= 6) {
    Serial.print("ERR2\n"); // BadAxis
    return;
  }

  if (value < 0 && digitalRead(ENDSTOP_MIN_PINS[axis]) == LOW) {
    Serial.print("ERR6\n"); // Endstop already active
    return;
  }

  long target = steppers[axis].currentPosition() + value;
  if (target < MIN_POSITION_STEPS || target > MAX_POSITION_STEPS) {
    Serial.print("ERR4\n");
    return;
  }
  steppers[axis].move(value);
}

void handleMoveAbsolute(const String &line) {
  // Format: A<eje><abs_pos>
  digitalWrite(ENABLE_PIN, LOW);
  uint8_t axis = line.charAt(1) - '1';

  if (axis >= 6) {
    Serial.print("ERR2\n");
    return;
  }

  long pos = line.substring(2).toInt();
  if (pos < MIN_POSITION_STEPS || pos > MAX_POSITION_STEPS) {
    Serial.print("ERR4\n");
    return;
  }
  steppers[axis].moveTo(pos);
}

void handleHoming(const String &line) {
  // Format: H<eje>
  digitalWrite(ENABLE_PIN, LOW);
  uint8_t axis = line.charAt(1) - '1';
  if (axis >= 6) {
    Serial.print("ERR2\n");
    return;
  }

  // Verify endstops initial state
  if (digitalRead(ENDSTOP_MIN_PINS[axis]) == LOW) {
    steppers[axis].setCurrentPosition(0);
    return;
  }

  unsigned long start = millis();
  // Move slowly toward min endstop
  steppers[axis].setMaxSpeed(DEFAULT_SPEED_STEPS_PER_SEC / 4);
  steppers[axis].moveTo(-MAX_POSITION_STEPS);
  while (digitalRead(ENDSTOP_MIN_PINS[axis]) == HIGH) {
    steppers[axis].run();
    if (millis() - start > HOMING_TIMEOUT_MS) {
      Serial.print("ERR5\n"); // Timeout
      return;
    }
  }
  steppers[axis].setCurrentPosition(0);
  // Restore speed
  steppers[axis].setMaxSpeed(DEFAULT_SPEED_STEPS_PER_SEC);
}

void emergencyStop() {
  // Immediately disable all steppers
  digitalWrite(ENABLE_PIN, HIGH); // HIGH = disabled
}

void handleKillAxis(const String &line) {
  // Format: K<eje>
  digitalWrite(ENABLE_PIN, LOW);
  uint8_t axis = line.charAt(1) - '1';
  if (axis >= 6) {
    Serial.print("ERR2\n");
    return;
  }
  steppers[axis].stop();
  // Confirm axis stopped 
  Serial.print("D"); 
  Serial.print(axis + 1);
  Serial.print("\n");
}

void handleProfile(const String &line) {
  // Format: P<param><value>
  digitalWrite(ENABLE_PIN, LOW);
  char param = line.charAt(1);
  long val = line.substring(2).toInt();
  switch (param) {
    case 'V':
      for (uint8_t i = 0; i < 6; i++) steppers[i].setMaxSpeed(val);
      break;
    case 'A':
      for (uint8_t i = 0; i < 6; i++) steppers[i].setAcceleration(val);
      break;
    default:
      Serial.print("ERR1\n"); // BadCmd
      return;
  }
}