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

    def update_status(self):
        # Ideally we'd parse 'S' command response here
        pass
