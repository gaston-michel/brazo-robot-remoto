import os
import subprocess

print("--- /dev/spi* ---")
try:
    print(subprocess.check_output("ls -l /dev/spi*", shell=True).decode())
except Exception as e:
    print(f"Error listing /dev/spi*: {e}")

print("\n--- Loaded Modules (spi) ---")
try:
    print(subprocess.check_output("lsmod | grep spi", shell=True).decode())
except:
    pass

print("\n--- Config.txt (tail) ---")
try:
    print(subprocess.check_output("tail -n 10 /boot/firmware/config.txt", shell=True).decode())
except:
    try:
        print(subprocess.check_output("tail -n 10 /boot/config.txt", shell=True).decode())
    except:
        print("Could not read config.txt")
