#ifndef UTILS_H
#define UTILS_H

#include <Arduino.h>

// Initialize utility subsystems (e.g., watchdogs)
void initUtils();

// Check for timeouts or watchdog events, called in loop()
void checkTimeouts();

// Print debug message over Serial (optional separate Serial)
void debugPrint(const String &msg);

// Update the last command time to reset the watchdog
void updateLastCommandTime();

#endif // UTILS_H