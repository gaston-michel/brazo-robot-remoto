#include "config.h"
#include "utils.h"
#include "parser.h"
#include "motion.h"
#include "telemetry.h"

void setup() {
  // Inicialización de utilidades (debug, watchdog)
  initUtils();

  // Puerto serie principal para comunicación con Raspberry Pi
  Serial1.begin(115200);
  while (!Serial1) { /* Esperar a que Serial1 esté listo */ }

  // Inicializar subsistemas
  initMotion();
  initTelemetry();
  initParser();
}

void loop() {
  // 1) Procesar comandos entrantes desde Raspberry Pi
  if (Serial1.available()) {
    String line = Serial1.readStringUntil('\n');
    if (line.length() > 0) {
      parseLine(line);
    }
  }

  // 2) Actualizar estado de motores (pasos pendientes)
  updateMotors();

  // 3) Comprobar timeouts y watchdog
  checkTimeouts();
}