import subprocess

print("--- GPIO Info (gpioinfo) ---")
try:
    # Try to use gpioinfo if available (part of libgpiod)
    print(subprocess.check_output("gpioinfo | grep -E 'SPI|spi|GPIO8|GPIO10|GPIO11|GPIO25|GPIO17'", shell=True).decode())
except:
    print("gpioinfo not found or failed.")

print("\n--- Pinctrl (raspi-gpio) ---")
try:
    # Check pin states
    print(subprocess.check_output("raspi-gpio get 8,10,11,25,17", shell=True).decode())
except:
    print("raspi-gpio failed.")
