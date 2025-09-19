#define STEP_PIN         43//54
#define DIR_PIN          45//55
#define ENABLE_PIN       47//38

#include "CustomStepper.h"

// Configuración del puerto de debug
#define DEBUG_SERIAL Serial
#define DEBUG_BAUD 9600

// Configuración de perfiles de movimiento
static const uint32_t DEFAULT_SPEED_STEPS_PER_SEC = 1200;    // Steps per second
static const uint32_t DEFAULT_ACCEL_STEPS_PER_SEC2 = 500;    // Steps per second^2

CustomStepper stepper = CustomStepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN, ENABLE_PIN, TB6600);

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

// Inicialización del sistema
void setup() {
  // Inicializar puerto de debug
  DEBUG_SERIAL.begin(DEBUG_BAUD);
  delay(1000);
  
  debugPrintln("=========================================");
  debugPrintln("INICIANDO PRUEBA DE DRIVER Y MOTOR");
  debugPrintln("=========================================");

  // Configurar pin ENABLE
  pinMode(ENABLE_PIN, OUTPUT);
  //stepper.setEnablePin(ENABLE_PIN); // This is now handled by CustomStepper
  //stepper.setPinsInverted(false, false, true); // This is now handled by CustomStepper
  stepper.disableOutputs();
  //digitalWrite(ENABLE_PIN, HIGH); // Inicialmente deshabilitado

  // Configurar steppers
  stepper.setMaxSpeed(DEFAULT_SPEED_STEPS_PER_SEC / 2); // Velocidad reducida para pruebas
  stepper.setAcceleration(DEFAULT_ACCEL_STEPS_PER_SEC2 / 2);
  stepper.setCurrentPosition(0);

  debugPrintln("Sistema inicializado correctamente");
  testStartTime = millis();
  testInProgress = true;
}

// Loop principal
void loop() {
  static bool testCompleted = false;

  if(!testCompleted && testInProgress){
    debugPrintln("\n=== PRUEBA 1: CONECTIVIDAD DE DRIVERS ===");
    
    // Probar ENABLE pin
    debugPrint("Probando pin ENABLE... ");
    //digitalWrite(ENABLE_PIN, LOW); // Habilitar
    stepper.enableOutputs();
    delay(500);
    //digitalWrite(ENABLE_PIN, HIGH); // Deshabilitar
    stepper.disableOutputs();
    delay(500);
    debugPrintln("OK");
    
    // Probar driver
    debugPrint("Probando Driver...");
    
    //digitalWrite(ENABLE_PIN, LOW); // Habilitar driver
    stepper.enableOutputs();
    
    // Pequeño movimiento para verificar funcionamiento
    stepper.move(200); // 200 pasos en una dirección
    
    unsigned long startTime = millis();
    while (stepper.distanceToGo() != 0 && millis() - startTime < 2000) {
      stepper.run();
    }
    
    delay(200);
    
    // Volver a posición inicial
    stepper.move(-200);
    startTime = millis();
    while (stepper.distanceToGo() != 0 && millis() - startTime < 2000) {
      stepper.run();
    }
    
    //digitalWrite(ENABLE_PIN, HIGH); // Deshabilitar
    stepper.disableOutputs();
    debugPrintln("OK");
    
    debugPrintln("Prueba completada");
    testCompleted = true;
    testInProgress = false;
  }

  // Verificar timeout
  if (millis() - testStartTime > TEST_TIMEOUT && testInProgress) {
    debugPrintln("\n=========================================");
    debugPrintln("TIMEOUT DE PRUEBA - SISTEMA DETENIDO");
    debugPrintln("=========================================");
    //digitalWrite(ENABLE_PIN, HIGH); // Emergency stop
    stepper.disableOutputs();
    testInProgress = false;
  }

  // Pequeño delay para estabilidad
  delay(100);
}
