#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

// ===== PINS CONFIGURATION =====
// STEP and DIR pins for each of the 6 axes (1 to 6)
static const uint8_t STEP_PINS[6] = {54, 24, 26, 28, 30, 32};
static const uint8_t DIR_PINS[6]  = {55, 25, 27, 29, 31, 33};

// ENABLE pin: shared for all drivers (TB6600 and DRV8825 groups)
static const uint8_t ENABLE_PIN = 38;  // HIGH = disabled, LOW = enabled

// ===== ENDSTOP (LIMIT SWITCH) PINS =====
// Two limit switches per axis: MIN and MAX for homing and safety
static const uint8_t ENDSTOP_MIN_PINS[6] = {A1, A2, A3, A4, A5, A6};  // Home/min endstops
// Max travel endstops (currently unused; define pins when adding max limits)
static const uint8_t ENDSTOP_MAX_PINS[6] = {};

// ===== MOTION PARAMETERS =====
// Default motion profile values (can be changed at runtime via commands)
static const uint32_t DEFAULT_SPEED_STEPS_PER_SEC = 1200;    // Steps per second
static const uint32_t DEFAULT_ACCEL_STEPS_PER_SEC2 = 500;    // Steps per second^2

// Maximum and minimum allowed step counts or positions
static const int32_t MAX_POSITION_STEPS = 100000;  // e.g., 100k steps limit
static const int32_t MIN_POSITION_STEPS = 0;

// Timeout settings (ms)
static const uint32_t MOVE_TIMEOUT_MS = 10000;    // Timeout for move commands
static const uint32_t HOMING_TIMEOUT_MS = 20000;  // Timeout for homing

#endif // CONFIG_H