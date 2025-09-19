
#ifndef CustomStepper_h
#define CustomStepper_h

#include <AccelStepper.h>
#include <Arduino.h>

enum DriverType {
  DRV8825,
  TB6600
};

class CustomStepper : public AccelStepper {
public:
  CustomStepper(uint8_t pins, uint8_t stepPin, uint8_t dirPin, uint8_t enablePin, DriverType driverType = DRV8825);

private:
  uint8_t _enablePin;
  DriverType _driverType;
};

#endif
