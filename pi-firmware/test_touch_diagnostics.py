import evdev

print("Scanning for input devices...")
try:
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    if not devices:
        print("No input devices found! (Are you running with sudo?)")
    else:
        for dev in devices:
            print(f"Device: {dev.path}")
            print(f"  Name: {dev.name}")
            print(f"  Phys: {dev.phys}")
            print("-" * 20)
except Exception as e:
    print(f"Error listing devices: {e}")
