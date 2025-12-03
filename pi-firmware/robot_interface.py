import time
import threading
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import ili9486
from PIL import Image, ImageDraw

from ui_framework import Theme, TouchInput, Screen, Button, Label
from robot_client import RobotClient

# --- Configuration ---
TOUCH_DEVICE_PATH = None # Auto-detect
SERIAL_PORT = '/dev/ttyACM0' # Adjust if needed

class RobotApp:
    def __init__(self):
        # Init Display
        # On Pi 5, sometimes we get spidev10.0 or similar weirdness, or we need to force it.
        # But usually port=0, device=0 is correct if config is right.
        # If spidev0.0 is missing, we might need 'dtoverlay=spi0-0' in config.txt
        try:
            self.serial_spi = spi(port=0, device=0, gpio_DC=24, gpio_RST=25)
        except Exception as e:
            print(f"Failed to open SPI0.0: {e}")
            print("Trying SPI10.0 (Pi 5 software SPI?)...")
            try:
                self.serial_spi = spi(port=10, device=0, gpio_DC=24, gpio_RST=25)
            except:
                raise e
                
        # Rotate 1 is landscape, but we mirror in software if needed. 
        # Based on previous test, we might need manual flip.
        self.device = ili9486(self.serial_spi, rotate=1)
        
        # Init Touch
        self.touch = TouchInput(TOUCH_DEVICE_PATH)
        
        # Init Robot Client
        self.client = RobotClient(port=SERIAL_PORT)
        
        # Load Resources
        Theme.load_fonts()
        
        # UI State
        self.current_screen_idx = 0
        self.screens = []
        self.running = True
        
        self._init_ui()

    def _init_ui(self):
        # --- 1. Status Screen ---
        s_status = Screen("Status")
        s_status.add_widget(Label(10, 10, "GROVA ROBOT", color=Theme.CYAN))
        
        self.lbl_connection = Label(10, 40, "Disconnected", color=Theme.RED)
        s_status.add_widget(self.lbl_connection)
        
        btn_connect = Button(350, 10, 100, 40, "Connect", callback=self.do_connect)
        s_status.add_widget(btn_connect)
        
        btn_estop = Button(50, 100, 380, 150, "E-STOP", callback=self.do_estop, color=Theme.RED)
        s_status.add_widget(btn_estop)
        
        self.screens.append(s_status)

        # --- 2. Control Screen ---
        s_control = Screen("Control")
        s_control.add_widget(Label(10, 10, "Manual Control", color=Theme.YELLOW))
        
        # Axis Controls (Simplified for demo)
        # 2 columns of 3 axes
        axes = ["X", "Y", "Z", "A", "B", "C"]
        for i, name in enumerate(axes):
            col = i % 2
            row = i // 2
            x_base = 10 + col * 240
            y_base = 50 + row * 80
            
            s_control.add_widget(Label(x_base, y_base, f"Axis {name}"))
            s_control.add_widget(Button(x_base, y_base+30, 60, 40, "-", callback=lambda idx=i: self.move_axis(idx, -100)))
            s_control.add_widget(Button(x_base+70, y_base+30, 60, 40, "+", callback=lambda idx=i: self.move_axis(idx, 100)))
            s_control.add_widget(Button(x_base+140, y_base+30, 60, 40, "H", callback=lambda idx=i: self.home_axis(idx), color=Theme.DARK_GRAY))

        self.screens.append(s_control)

        # --- Navigation Bar (Global) ---
        # We handle this in the main loop or as a special widget overlay
        self.nav_buttons = [
            Button(0, 280, 120, 40, "Status", callback=lambda: self.set_screen(0)),
            Button(120, 280, 120, 40, "Control", callback=lambda: self.set_screen(1)),
            Button(240, 280, 120, 40, "Settings", callback=lambda: self.set_screen(0)), # Placeholder
            Button(360, 280, 120, 40, "Exit", callback=self.exit_app, color=Theme.DARK_GRAY)
        ]

    def set_screen(self, idx):
        self.current_screen_idx = idx

    def do_connect(self):
        if self.client.connect():
            self.lbl_connection.text = "Connected"
            self.lbl_connection.color = Theme.GREEN
        else:
            self.lbl_connection.text = "Error"
            self.lbl_connection.color = Theme.RED

    def do_estop(self):
        self.client.emergency_stop()
        self.lbl_connection.text = "E-STOPPED"
        self.lbl_connection.color = Theme.RED

    def move_axis(self, axis, steps):
        self.client.move_relative(axis, steps)

    def home_axis(self, axis):
        self.client.home_axis(axis)

    def exit_app(self):
        self.running = False

    def run(self):
        print("Starting UI Loop...")
        try:
            while self.running:
                # 1. Update Touch
                touch_pos = self.touch.update()
                
                # 2. Handle Input
                if touch_pos:
                    tx, ty = touch_pos
                    # Check Nav Buttons first
                    handled = False
                    for btn in self.nav_buttons:
                        if btn.contains(tx, ty):
                            btn.on_click()
                            # Reset pressed state after a short delay or next frame
                            # For simplicity we just draw it pressed this frame
                            handled = True
                            break
                    
                    if not handled:
                        # Check Current Screen
                        self.screens[self.current_screen_idx].handle_touch(tx, ty)

                # 3. Draw
                # Create blank image
                image = Image.new("RGB", (480, 320), "black")
                draw = ImageDraw.Draw(image)
                
                # Draw Current Screen
                self.screens[self.current_screen_idx].draw(draw)
                
                # Draw Nav Bar
                for btn in self.nav_buttons:
                    btn.draw(draw)

                # 4. Flip and Display
                # Fix mirroring
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
                self.device.display(image)
                
                # Cap FPS
                time.sleep(0.05)
                
                # Reset button states (visual only)
                for btn in self.nav_buttons:
                    btn.pressed = False
                for w in self.screens[self.current_screen_idx].widgets:
                    if isinstance(w, Button):
                        w.pressed = False

        except KeyboardInterrupt:
            pass
        finally:
            self.client.disconnect()
            print("Exiting...")

if __name__ == "__main__":
    app = RobotApp()
    app.run()
