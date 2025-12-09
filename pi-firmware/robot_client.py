import serial
import time
import threading

class RobotClient:
    def __init__(self, port='/dev/ttyACM0', baud=115200):
        self.port = port
        self.baud = baud
        self.serial = None
        self.connected = False
        self.lock = threading.Lock()
        
        # Robot State
        self.axes = [0.0] * 6
        self.status = "DISCONNECTED"
        self.last_error = ""

    def connect(self):
        try:
            self.serial = serial.Serial(self.port, self.baud, timeout=1)
            time.sleep(2) # Wait for Arduino reset
            self.connected = True
            self.status = "IDLE"
            print(f"Connected to {self.port}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            self.connected = False
            self.status = "ERROR"
            return False

    def disconnect(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.connected = False
        self.status = "DISCONNECTED"

    def send_command(self, cmd):
        if not self.connected:
            return False
        
        with self.lock:
            try:
                full_cmd = cmd + "\n"
                self.serial.write(full_cmd.encode('utf-8'))
                # We could wait for OK here, but for UI responsiveness 
                # we might want to read in a separate thread or just fire-and-forget for now
                # For simplicity, let's read one line
                response = self.serial.readline().decode('utf-8').strip()
                if response.startswith("ERR"):
                    self.last_error = response
                    print(f"Command Error: {response}")
                    return False
                return True
            except Exception as e:
                print(f"Send error: {e}")
                self.disconnect()
                return False

    def move_relative(self, axis_idx, steps):
        # M<axis_1_based><steps>
        cmd = f"M{axis_idx+1}{steps}"
        return self.send_command(cmd)

    def home_axis(self, axis_idx):
        # H<axis_1_based>
        cmd = f"H{axis_idx+1}"
        return self.send_command(cmd)

    def emergency_stop(self):
        return self.send_command("E")

    def set_profile(self, speed, accel):
        # P<speed> <accel>
        # Example: P1000 500
        cmd = f"P{int(speed)} {int(accel)}"
        return self.send_command(cmd)

    def reset_alarm(self):
        # Assuming M999 or similar to reset alarm/unlock
        # Or maybe just re-homing?
        # For now, let's try a specific command if known, or just a soft reset.
        # Based on typical firmwares, $X is unlock.
        # Let's send a custom command or just re-enable.
        # If the firmware uses 'E' for Estop, maybe 'R' for Reset?
        # Let's assume 'R' for now based on common custom protocols, or we can ask.
        # Actually, let's just send a generic "Reset" command if defined.
        return self.send_command("R")

    @staticmethod
    def scan_ports():
        import glob
        # Linux style
        ports = glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*')
        return ports

        # Send 'S' command to get status
        # Expected format: "State:IDLE X:0.00 Y:0.00 Z:0.00 A:0.00 B:0.00 C:0.00"
        # Or similar, depending on firmware implementation.
        # Let's assume the firmware returns something like that.
        
        with self.lock:
            try:
                self.serial.write(b"S\n")
                response = self.serial.readline().decode('utf-8').strip()
                
                if not response:
                    return

                # Parse response
                # Example: "State:IDLE X:10.00 Y:20.00 ..."
                parts = response.split(' ')
                for part in parts:
                    if ':' in part:
                        key, val = part.split(':')
                        if key == "State":
                            self.status = val
                        elif key in ["X", "Y", "Z", "A", "B", "C"]:
                            # Map axis name to index
                            idx = ["X", "Y", "Z", "A", "B", "C"].index(key)
                            try:
                                self.axes[idx] = float(val)
                            except ValueError:
                                pass
            except Exception as e:
                print(f"Status update error: {e}")
                # Don't disconnect immediately on read error, might be noise
                pass
