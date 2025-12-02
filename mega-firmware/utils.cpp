#include "utils.h"
#include "config.h"

// Optionally use Serial (USB) for debug
#define DEBUG_SERIAL Serial

// Timestamps for last command received
static unsigned long lastCommandTime = 0;

void initUtils() {
  // Initialize debug serial if needed
  DEBUG_SERIAL.begin(9600);
  // Initialize lastCommandTime
  lastCommandTime = millis();
}

void checkTimeouts() {
  unsigned long now = millis();
  if ((now - lastCommandTime) > MOVE_TIMEOUT_MS) {
    // Timeout occurred: emergency stop
    DEBUG_SERIAL.println("[UTILS] Move timeout, executing emergency stop");
    // Use Serial to notify upstream
    Serial.print("ERR5\n");  // Timeout error code
    // Halt all steppers
    digitalWrite(ENABLE_PIN, HIGH);
    lastCommandTime = now;  // reset watchdog
  }
}

void debugPrint(const String &msg) {
  DEBUG_SERIAL.print("[DEBUG] ");
  DEBUG_SERIAL.println(msg);
}

// Call this when a command is successfully parsed
void updateLastCommandTime() {
  lastCommandTime = millis();
}
