// parser.cpp
#include "parser.h"
#include "config.h"
#include "motion.h"
#include "telemetry.h"
#include "utils.h"

void initParser() {
  // nothing to init for now
}

void parseLine(const String &line) {
  digitalWrite(ENABLE_PIN, LOW);   // re-enable drivers
  updateLastCommandTime();         // reset watchdog
  
  if (line.length() < 1) return;

  char cmd = line.charAt(0);
  bool ok = true;

  switch (cmd) {
    case 'M':  // Move relative: M<eje><valor>
      handleMoveRelative(line);
      break;

    case 'A':  // Move absolute: A<eje><pos>
      handleMoveAbsolute(line);
      break;

    case 'H':  // Homing: H<eje>
      handleHoming(line);
      break;

    case 'S':  // Status request
      sendTelemetry();
      break;

    case 'E':  // Emergency stop
      emergencyStop();
      Serial.print("OK\n");
      break;

    case 'K':  // Kill axis: K<eje>
      handleKillAxis(line);
      break;

    case 'P':  // Profile: P<param><v>
      handleProfile(line);
      break;

    default:
      Serial.print("ERR1\n");  // BadCmd
      ok = false;
      break;
  }

  if (ok && cmd != 'S' && cmd != 'E') {
    Serial.print("OK\n");
  }
}