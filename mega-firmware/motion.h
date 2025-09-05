#ifndef MOTION_H
#define MOTION_H

#include <Arduino.h>
#include <AccelStepper.h>

// Initialize motion subsystem and steppers
void initMotion();

// Called in loop to update steppers
void updateMotors();

// Command handlers
void handleMoveRelative(const String &line);
void handleMoveAbsolute(const String &line);
void handleHoming(const String &line);
void emergencyStop();
void handleKillAxis(const String &line);
void handleProfile(const String &line);

#endif // MOTION_H