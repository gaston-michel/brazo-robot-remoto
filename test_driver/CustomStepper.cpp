
#include "CustomStepper.h"

CustomStepper::CustomStepper(uint8_t pins, uint8_t stepPin, uint8_t dirPin, uint8_t enablePin, DriverType driverType)
  : AccelStepper(pins, stepPin, dirPin)
{
  pinMode(enablePin, OUTPUT);
  setEnablePin(enablePin);
  if (driverType == DRV8825) {
    setPinsInverted(false, false, false); // DRV8825: enable LOW
  } else { // TB6600
    setPinsInverted(false, false, true); // TB6600: enable HIGH
  }
}
