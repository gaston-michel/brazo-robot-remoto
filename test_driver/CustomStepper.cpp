#include "CustomStepper.h"

CustomStepper::CustomStepper(uint8_t interfaceType, uint8_t stepPin, uint8_t dirPin, uint8_t enablePin, DriverType driverType)
  : AccelStepper(interfaceType, stepPin, dirPin)
{
  pinMode(enablePin, OUTPUT);
  setEnablePin(enablePin);

  if (driverType == DRV8825) {
    // enable activo en LOW
    setPinsInverted(false, false, false);
  } else { // TB6600
    // enable activo en HIGH
    setPinsInverted(false, false, true);
  }
}
