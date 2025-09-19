/*
 * Script de Prueba para Drivers y Motores del Brazo Robot 6DOF
 * 
 * Este script prueba:
 * 1. Conectividad de los 6 drivers de motores
 * 2. Funcionamiento de los endstops
 * 3. Movimientos básicos en cada eje
 * 4. Sistema de homing
 * 5. Comunicación serie
 * 
 * Instrucciones:
 * - Cargar este código en Arduino Mega
 * - Abrir monitor serie a 9600 baudios para ver mensajes de debug
 * - El script se ejecuta automáticamente al reiniciar
 * - Observar LEDs de los drivers y movimiento de motores
 */

#include <AccelStepper.h>
#include "config.h"

// Configuración del puerto de debug
#define DEBUG_SERIAL Serial
#define DEBUG_BAUD 9600

// Crear objetos AccelStepper para cada eje
AccelStepper steppers[6] = {
  AccelStepper(AccelStepper::DRIVER, STEP_PINS[0], DIR_PINS[0]),
  AccelStepper(AccelStepper::DRIVER, STEP_PINS[1], DIR_PINS[1]),
  AccelStepper(AccelStepper::DRIVER, STEP_PINS[2], DIR_PINS[2]),
  AccelStepper(AccelStepper::DRIVER, STEP_PINS[3], DIR_PINS[3]),
  AccelStepper(AccelStepper::DRIVER, STEP_PINS[4], DIR_PINS[4]),
  AccelStepper(AccelStepper::DRIVER, STEP_PINS[5], DIR_PINS[5])
};

// Variables de estado
bool testInProgress = false;
unsigned long testStartTime = 0;
const unsigned long TEST_TIMEOUT = 120000; // 2 minutos timeout

// Funciones de utilidad para debug
void debugPrint(const String &msg) {
  DEBUG_SERIAL.print("[TEST] ");
  DEBUG_SERIAL.println(msg);
}

void debugPrintln(const String &msg) {
  DEBUG_SERIAL.println("[TEST] " + msg);
}

// Función para esperar un tiempo con debug
void waitWithDebug(unsigned long ms, const String &message) {
  debugPrint(message + " - Esperando " + String(ms/1000) + " segundos...");
  unsigned long start = millis();
  while (millis() - start < ms) {
    delay(100);
    DEBUG_SERIAL.print(".");
  }
  DEBUG_SERIAL.println(" OK");
}

// Inicialización del sistema
void setup() {
  // Inicializar puerto de debug
  DEBUG_SERIAL.begin(DEBUG_BAUD);
  delay(1000);
  
  debugPrintln("=========================================");
  debugPrintln("INICIANDO PRUEBAS DE DRIVERS Y MOTORES");
  debugPrintln("=========================================");
  
  // Configurar pines de endstops como entrada con pullup
  for (uint8_t i = 0; i < 6; i++) {
    pinMode(ENDSTOP_MIN_PINS[i], INPUT_PULLUP);
  }
  
  // Configurar pin ENABLE
  pinMode(ENABLE_PIN, OUTPUT);
  digitalWrite(ENABLE_PIN, HIGH); // Inicialmente deshabilitado
  
  // Configurar steppers
  for (uint8_t i = 0; i < 6; i++) {
    steppers[i].setMaxSpeed(DEFAULT_SPEED_STEPS_PER_SEC / 2); // Velocidad reducida para pruebas
    steppers[i].setAcceleration(DEFAULT_ACCEL_STEPS_PER_SEC2 / 2);
    steppers[i].setCurrentPosition(0);
  }
  
  debugPrintln("Sistema inicializado correctamente");
  testStartTime = millis();
  testInProgress = true;
}

// Prueba 1: Verificar conectividad de drivers
void testDriverConnectivity() {
  debugPrintln("\n=== PRUEBA 1: CONECTIVIDAD DE DRIVERS ===");
  
  // Probar ENABLE pin
  debugPrint("Probando pin ENABLE... ");
  digitalWrite(ENABLE_PIN, LOW); // Habilitar
  delay(500);
  digitalWrite(ENABLE_PIN, HIGH); // Deshabilitar
  delay(500);
  debugPrintln("OK");
  
  // Probar cada driver individualmente
  for (uint8_t axis = 0; axis < 6; axis++) {
    debugPrint("Probando Driver Eje " + String(axis + 1) + "... ");
    
    digitalWrite(ENABLE_PIN, LOW); // Habilitar drivers
    
    // Pequeño movimiento para verificar funcionamiento
    steppers[axis].move(50); // 50 pasos en una dirección
    
    unsigned long startTime = millis();
    while (steppers[axis].distanceToGo() != 0 && millis() - startTime < 2000) {
      steppers[axis].run();
    }
    
    delay(200);
    
    // Volver a posición inicial
    steppers[axis].move(-50);
    startTime = millis();
    while (steppers[axis].distanceToGo() != 0 && millis() - startTime < 2000) {
      steppers[axis].run();
    }
    
    digitalWrite(ENABLE_PIN, HIGH); // Deshabilitar
    debugPrintln("OK");
    delay(500);
  }
  
  debugPrintln("Prueba de conectividad completada");
}

// Prueba 2: Verificar endstops
void testEndstops() {
  debugPrintln("\n=== PRUEBA 2: VERIFICACIÓN DE ENDSTOPS ===");
  
  for (uint8_t axis = 0; i < 6; axis++) {
    debugPrint("Verificando Endstop Eje " + String(axis + 1) + " (MIN)... ");
    
    int endstopState = digitalRead(ENDSTOP_MIN_PINS[axis]);
    
    if (endstopState == LOW) {
      debugPrintln("ACTIVADO (LOW) - Verificar conexión");
    } else {
      debugPrintln("DESACTIVADO (HIGH) - OK");
    }
    
    delay(200);
  }
  
  debugPrintln("Verificación de endstops completada");
}

// Prueba 3: Movimientos básicos
void testBasicMovements() {
  debugPrintln("\n=== PRUEBA 3: MOVIMIENTOS BÁSICOS ===");
  
  digitalWrite(ENABLE_PIN, LOW); // Habilitar drivers
  
  for (uint8_t axis = 0; axis < 6; axis++) {
    debugPrintln("Moviendo Eje " + String(axis + 1) + " en ambas direcciones");
    
    // Movimiento positivo
    debugPrint("  Dirección POSITIVA... ");
    steppers[axis].move(200);
    unsigned long startTime = millis();
    while (steppers[axis].distanceToGo() != 0 && millis() - startTime < 5000) {
      steppers[axis].run();
    }
    debugPrintln("OK");
    
    waitWithDebug(1000, "  Pausa");
    
    // Movimiento negativo
    debugPrint("  Dirección NEGATIVA... ");
    steppers[axis].move(-200);
    startTime = millis();
    while (steppers[axis].distanceToGo() != 0 && millis() - startTime < 5000) {
      steppers[axis].run();
    }
    debugPrintln("OK");
    
    waitWithDebug(1500, "  Pausa entre ejes");
  }
  
  digitalWrite(ENABLE_PIN, HIGH); // Deshabilitar
  debugPrintln("Prueba de movimientos básicos completada");
}

// Prueba 4: Sistema de homing (opcional)
void testHoming() {
  debugPrintln("\n=== PRUEBA 4: SISTEMA DE HOMING ===");
  debugPrintln("ADVERTENCIA: Asegúrese de que los endstops estén conectados");
  debugPrintln("Presione cualquier tecla en Serial para continuar o 'S' para saltar...");
  
  // Esperar input del usuario
  unsigned long waitStart = millis();
  while (millis() - waitStart < 10000) { // 10 segundos timeout
    if (DEBUG_SERIAL.available()) {
      char input = DEBUG_SERIAL.read();
      if (input == 'S' || input == 's') {
        debugPrintln("Prueba de homing omitida por usuario");
        return;
      }
      break;
    }
    delay(100);
  }
  
  digitalWrite(ENABLE_PIN, LOW); // Habilitar drivers
  
  for (uint8_t axis = 0; axis < 6; axis++) {
    debugPrint("Homing Eje " + String(axis + 1) + "... ");
    
    // Verificar que el endstop no esté ya activado
    if (digitalRead(ENDSTOP_MIN_PINS[axis]) == LOW) {
      debugPrintln("Endstop ya activado - Omitiendo homing");
      continue;
    }
    
    // Movimiento lento hacia el endstop
    steppers[axis].setMaxSpeed(DEFAULT_SPEED_STEPS_PER_SEC / 4);
    steppers[axis].moveTo(-MAX_POSITION_STEPS);
    
    unsigned long startTime = millis();
    bool homed = false;
    
    while (millis() - startTime < HOMING_TIMEOUT_MS) {
      steppers[axis].run();
      
      if (digitalRead(ENDSTOP_MIN_PINS[axis]) == LOW) {
        steppers[axis].stop();
        steppers[axis].setCurrentPosition(0);
        homed = true;
        break;
      }
    }
    
    // Restaurar velocidad normal
    steppers[axis].setMaxSpeed(DEFAULT_SPEED_STEPS_PER_SEC);
    
    if (homed) {
      debugPrintln("OK - Posición 0 establecida");
    } else {
      debugPrintln("TIMEOUT - Verificar endstop y conexiones");
    }
    
    waitWithDebug(1000, "  Pausa");
  }
  
  digitalWrite(ENABLE_PIN, HIGH); // Deshabilitar
  debugPrintln("Prueba de homing completada");
}

// Prueba 5: Comunicación serie
void testSerialCommunication() {
  debugPrintln("\n=== PRUEBA 5: COMUNICACIÓN SERIE ===");
  
  // Inicializar Serial1 para comunicación con Raspberry Pi
  Serial1.begin(115200);
  delay(1000);
  
  debugPrint("Enviando mensaje de prueba a Raspberry Pi... ");
  Serial1.println("TEST: Drivers y motores funcionando correctamente");
  debugPrintln("OK");
  
  debugPrintln("Verifique en la Raspberry Pi que recibió el mensaje");
  waitWithDebug(2000, "");
  
  debugPrintln("Prueba de comunicación serie completada");
}

// Función principal de pruebas
void runTests() {
  testDriverConnectivity();
  waitWithDebug(2000, "Preparando siguiente prueba");
  
  testEndstops();
  waitWithDebug(2000, "Preparando siguiente prueba");
  
  testBasicMovements();
  waitWithDebug(3000, "Preparando siguiente prueba");
  
  testHoming();
  waitWithDebug(2000, "Preparando siguiente prueba");
  
  testSerialCommunication();
}

// Loop principal
void loop() {
  static bool testsCompleted = false;
  
  if (!testsCompleted && testInProgress) {
    // Ejecutar pruebas solo una vez
    runTests();
    testsCompleted = true;
    
    debugPrintln("\n=========================================");
    debugPrintln("PRUEBAS COMPLETADAS");
    debugPrintln("=========================================");
    debugPrintln("Resumen:");
    debugPrintln("- Verifique que todos los drivers respondieron");
    debugPrintln("- Confirme movimientos suaves en todos los ejes");
    debugPrintln("- Verifique estado de endstops");
    debugPrintln("- Confirme funcionamiento de homing");
    debugPrintln("- Verifique comunicación con Raspberry Pi");
    
    digitalWrite(ENABLE_PIN, HIGH); // Asegurar que los drivers estén deshabilitados
    
    debugPrintln("\nSistema listo para operación normal");
    debugPrintln("Cargar 'mega-firmware.ino' para funcionamiento completo");
    
    testInProgress = false;
  }
  
  // Verificar timeout
  if (millis() - testStartTime > TEST_TIMEOUT && testInProgress) {
    debugPrintln("\n=========================================");
    debugPrintln("TIMEOUT DE PRUEBAS - SISTEMA DETENIDO");
    debugPrintln("=========================================");
    digitalWrite(ENABLE_PIN, HIGH); // Emergency stop
    testInProgress = false;
  }
  
  // Pequeño delay para estabilidad
  delay(100);
}
