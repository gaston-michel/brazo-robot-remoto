#include "telemetry.h"
#include "config.h"

void initTelemetry() {
  // Nothing specific to init for telemetry yet
}

void sendTelemetry() {
  // Build telemetry string in format:
  // S:pos0,pos1,pos2,pos3,pos4,pos5,min0,min1,min2,min3,min4,min5[,max0,max1,max2,max3,max4,max5]\n
  String msg = "S:";

  // Append current positions
  for (uint8_t i = 0; i < 6; i++) {
    msg += String( steppers[i].currentPosition() );
    if (i < 5) msg += ",";
  }

  // Append limit switch states (MIN)
  msg += ",";
  for (uint8_t i = 0; i < 6; i++) {
    int state = digitalRead( ENDSTOP_MIN_PINS[i] );
    msg += String( state );
    if (i < 5) msg += ",";
  }

  // Optionally append MAX endstops if defined
  bool maxDefined = sizeof(ENDSTOP_MAX_PINS) / sizeof(ENDSTOP_MAX_PINS[0]) == 6;
  if (maxDefined) {
    msg += ",";
    for (uint8_t i = 0; i < 6; i++) {
      int state = digitalRead( ENDSTOP_MAX_PINS[i] );
      msg += String( state );
      if (i < 5) msg += ",";
    }
  }

  msg += "\n";
  Serial1.print(msg);
}