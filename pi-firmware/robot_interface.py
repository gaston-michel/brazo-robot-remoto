import time
import threading
from PIL import Image, ImageDraw

from ui_framework import Theme, TouchInput, Screen, Button, Label
from robot_client import RobotClient

# --- Configuration ---
TOUCH_DEVICE_PATH = None # Auto-detect
SERIAL_PORT = '/dev/ttyACM0' # Adjust if needed

import os
import mmap

class FramebufferDevice:
    def __init__(self, path='/dev/fb1'):
        self.path = path
        self.width = 480
        self.height = 320
        self.bpp = 16 # Assuming RGB565
        self._init_fb()

    def _init_fb(self):
        # Simple check if file exists
        if not os.path.exists(self.path):
            # Fallback to fb0 if fb1 doesn't exist (e.g. if HDMI is disabled or it's the only display)
            if os.path.exists('/dev/fb0'):
                print(f"Warning: {self.path} not found, trying /dev/fb0")
                self.path = '/dev/fb0'
            else:
                raise FileNotFoundError(f"Framebuffer {self.path} not found")

    def display(self, image):
        # Convert PIL image to RGB565
        # This is a slow python implementation, ideally we'd use a library or C extension
        # But for this UI it might be enough.
        # Better yet: write RGB888 if the framebuffer supports it, or use a trick.
        
        # Check if we can just write RGB bytes
        # Most SPI TFT drivers use RGB565.
        
        # Let's try to use the raw file write.
        # Convert to RGB565:
        # RRRRRGGG GGGBBBBB
        
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        # Resize if needed (should match 480x320)
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height))

        pixels = image.load()
        with open(self.path, 'wb') as f:
            # Create a bytearray for the buffer
            # 480 * 320 * 2 bytes = 307200 bytes
            buf = bytearray(self.width * self.height * 2)
            idx = 0
            for y in range(self.height):
                for x in range(self.width):
                    r, g, b = pixels[x, y]
                    # RGB565 conversion
                    val = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                    buf[idx] = val & 0xFF
                    buf[idx+1] = (val >> 8) & 0xFF
                    idx += 2
            f.write(buf)
            
    # Helper to match luma interface
    @property
    def size(self):
        return (self.width, self.height)

class RobotApp:
    def __init__(self):
        # Init Display - Framebuffer Mode
        try:
            self.device = FramebufferDevice('/dev/fb1')
        except Exception as e:
            print(f"Framebuffer Error: {e}")
            print("Running in dummy mode (no display output)")
            # Dummy device for testing without screen
            class DummyDevice:
                def display(self, img): pass
                size = (480, 320)
            self.device = DummyDevice()
        
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
        
        self.lbl_state = Label(200, 40, "State: ???", color=Theme.YELLOW)
        s_status.add_widget(self.lbl_state)
        
        # Coordinate Labels
        self.lbl_axes = []
        axes_names = ["X", "Y", "Z", "A", "B", "C"]
        for i, name in enumerate(axes_names):
            # 2 columns: X,Y,Z left; A,B,C right
            col = i // 3
            row = i % 3
            x_pos = 10 + col * 160
            y_pos = 80 + row * 30
            lbl = Label(x_pos, y_pos, f"{name}: 0.00", color=Theme.WHITE)
            self.lbl_axes.append(lbl)
            s_status.add_widget(lbl)
        
        btn_connect = Button(350, 10, 100, 40, "Connect", callback=self.do_connect)
        s_status.add_widget(btn_connect)
        
        btn_estop = Button(350, 200, 100, 60, "E-STOP", callback=self.do_estop, color=Theme.RED)
        s_status.add_widget(btn_estop)
        
        self.screens.append(s_status)

        # ... (Control Screen remains similar) ...

        # --- 2. Control Screen ---
        s_control = Screen("Control")
        s_control.add_widget(Label(10, 5, "Manual Control", color=Theme.YELLOW))
        
        # Axis Controls
        # 2 columns of 3 axes
        # Renamed as requested
        axes_labels = ["Base", "Shoulder", "Elbow", "Wrist Pitch", "Wrist Roll", "Effector"]
        
        for i, name in enumerate(axes_labels):
            col = i % 2
            row = i // 2
            
            # Adjusted layout to fit 320px height with Nav bar at 280
            # Column width: 240
            # Row height: 75 (was 80)
            # Start Y: 35 (was 50)
            
            x_base = 10 + col * 240
            y_base = 35 + row * 75
            
            # Label
            s_control.add_widget(Label(x_base, y_base, name, font=Theme.FONT_SMALL))
            
            # Buttons (Smaller height: 35 instead of 40)
            # - Move Negative
            s_control.add_widget(Button(x_base, y_base+20, 60, 35, "-", callback=lambda idx=i: self.move_axis(idx, -100)))
            # + Move Positive
            s_control.add_widget(Button(x_base+70, y_base+20, 60, 35, "+", callback=lambda idx=i: self.move_axis(idx, 100)))
            # H Home
            s_control.add_widget(Button(x_base+140, y_base+20, 60, 35, "H", callback=lambda idx=i: self.home_axis(idx), color=Theme.DARK_GRAY))

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
                # Update Status if connected (every few frames to save bandwidth?)
                # For now, every frame is fine if serial is fast enough, or we throttle in client
                self.client.update_status()
                
                # Update Labels
                if self.client.connected:
                    self.lbl_state.text = f"State: {self.client.status}"
                    for i, val in enumerate(self.client.axes):
                        self.lbl_axes[i].text = f"{['X','Y','Z','A','B','C'][i]}: {val:.2f}"
                
                # Create blank image
                image = Image.new("RGB", (480, 320), "black")
                draw = ImageDraw.Draw(image)
                
                # Draw Current Screen
                self.screens[self.current_screen_idx].draw(draw)
                
                # Draw Nav Bar
                for btn in self.nav_buttons:
                    btn.draw(draw)

                # 4. Flip and Display
                # Fix mirroring - Removed as user reported it is mirrored WITH this.
                # image = image.transpose(Image.FLIP_LEFT_RIGHT)
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
