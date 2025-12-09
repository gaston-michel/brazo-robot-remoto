import evdev
import sys

def find_touch_device():
    try:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for dev in devices:
            if 'touch' in dev.name.lower() or 'ads7846' in dev.name.lower() or 'xpt2046' in dev.name.lower():
                return dev
    except Exception as e:
        print(f"Error finding devices: {e}")
    return None

def main():
    dev = find_touch_device()
    if not dev:
        print("No touch device found!")
        return

    print(f"Found device: {dev.name} at {dev.path}")
    print("------------------------------------------------")
    print("TOUCH CALIBRATION MODE")
    print("Please touch the following points and note the RAW values printed:")
    print("1. TOP-LEFT")
    print("2. TOP-RIGHT")
    print("3. BOTTOM-RIGHT")
    print("4. BOTTOM-LEFT")
    print("------------------------------------------------")
    print("Press Ctrl+C to exit")

    try:
        for event in dev.read_loop():
            if event.type == evdev.ecodes.EV_ABS:
                if event.code == evdev.ecodes.ABS_X:
                    print(f"ABS_X: {event.value}", end='\t')
                elif event.code == evdev.ecodes.ABS_Y:
                    print(f"ABS_Y: {event.value}")
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
