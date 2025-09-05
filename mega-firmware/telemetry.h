#ifndef TELEMETRY_H
#define TELEMETRY_H

#include <Arduino.h>

// Initialize telemetry subsystem
void initTelemetry();

// Read sensors and positions, send telemetry string over Serial1
void sendTelemetry();

#endif // TELEMETRY_H