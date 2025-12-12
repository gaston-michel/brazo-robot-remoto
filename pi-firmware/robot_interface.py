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
import json

class PathManager:
    def __init__(self, filename="paths.json"):
        self.filename = filename
        self.paths = {}
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    self.paths = json.load(f)
            except Exception as e:
                print(f"Error loading paths: {e}")
                self.paths = {}
        else:
            self.paths = {}

    def save(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.paths, f, indent=4)
        except Exception as e:
            print(f"Error saving paths: {e}")

    def get_path_names(self):
        return list(self.paths.keys())

    def add_path(self, name, points=[]):
        self.paths[name] = points
        self.save()

    def delete_path(self, name):
        if name in self.paths:
            del self.paths[name]
            self.save()

    def get_path(self, name):
        return self.paths.get(name, [])

class Keyboard:
    def __init__(self, x, y, width, height, callback_enter, callback_cancel):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.callback_enter = callback_enter
        self.callback_cancel = callback_cancel
        self.visible = False
        self.text = ""
        self.keys = []
        
        # Simple QWERTY layout
        rows = [
            "1234567890",
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNM"
        ]
        
        key_h = 40
        key_w = 35
        start_y = y + 50
        
        for r, row_str in enumerate(rows):
            start_x = x + (width - (len(row_str) * key_w)) // 2
            for c, char in enumerate(row_str):
                self.keys.append(Button(start_x + c*key_w, start_y + r*key_h, key_w-2, key_h-2, char, 
                                      callback=lambda k=char: self.on_key(k)))
        
        # Space, Backspace, Enter, Cancel
        y_ctrl = start_y + 4 * key_h + 5
        self.keys.append(Button(x + 20, y_ctrl, 60, 40, "BS", callback=self.on_bs, color=Theme.RED))
        self.keys.append(Button(x + 90, y_ctrl, 150, 40, "SPACE", callback=lambda: self.on_key(" ")))
        self.keys.append(Button(x + 250, y_ctrl, 80, 40, "OK", callback=self.on_enter, color=Theme.GREEN))
        self.keys.append(Button(x + 340, y_ctrl, 60, 40, "X", callback=self.on_cancel, color=Theme.RED))

    def on_key(self, char):
        self.text += char

    def on_bs(self):
        self.text = self.text[:-1]

    def on_enter(self):
        if self.callback_enter:
            self.callback_enter(self.text)
        self.visible = False
        self.text = ""

    def on_cancel(self):
        if self.callback_cancel:
            self.callback_cancel()
        self.visible = False
        self.text = ""

    def show(self):
        self.visible = True
        self.text = ""

    def hide(self):
        self.visible = False

    def reset_keys(self):
        for k in self.keys:
            k.pressed = False

    def handle_touch(self, x, y):
        if not self.visible: return False
        # Consume all touches if visible (modal)
        if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
            for k in self.keys:
                if k.contains(x, y):
                    k.on_click()
                    return True
            return True # Consumed but no button hit
        return False

    def draw(self, draw):
        if not self.visible: return
        # Background
        draw.rectangle((self.x, self.y, self.x + self.width, self.y + self.height), fill=Theme.DARK_GRAY, outline=Theme.WHITE)
        
        # Text Input Display
        draw.rectangle((self.x+10, self.y+10, self.x+self.width-10, self.y+45), fill=Theme.BLACK, outline=Theme.WHITE)
        
        # Cursor Logic (Blink every 0.5s)
        cursor = "|" if int(time.time() * 2) % 2 == 0 else ""
        display_text = self.text + cursor
        
        draw.text((self.x+15, self.y+15), display_text, fill=Theme.WHITE, font=Theme.FONT_MAIN)
        
        for k in self.keys:
            k.draw(draw)

class Popup:
    def __init__(self, x, y, width, height, title, options):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.visible = False
        self.buttons = []
        
        btn_h = 50
        y_start = y + 40
        
        for label, callback in options:
            self.buttons.append(Button(x+20, y_start, width-40, btn_h, label, callback=self.wrap_callback(callback)))
            y_start += btn_h + 10
            
    def wrap_callback(self, cb):
        def wrapped():
            cb()
            self.hide()
        return wrapped

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def handle_touch(self, x, y):
        if not self.visible: return False
        if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
            for b in self.buttons:
                if b.contains(x, y):
                    b.on_click()
                    return True
            return True
        else:
            # Click outside closes popup?
            self.hide()
            return True
        return False

    def draw(self, draw):
        if not self.visible: return
        # Overlay background (semi-transparent fake)
        # We can't do real alpha easily with just draw, so just solid block
        draw.rectangle((self.x, self.y, self.x + self.width, self.y + self.height), fill=Theme.DARK_GRAY, outline=Theme.CYAN)
        draw.text((self.x+20, self.y+10), self.title, fill=Theme.CYAN, font=Theme.FONT_MAIN)
        for b in self.buttons:
            b.draw(draw)

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
        
        btn_connect = Button(240, 10, 100, 40, "Connect", callback=self.do_connect)
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

        # --- 3. Settings Screen ---
        s_settings = Screen("Settings")
        s_settings.add_widget(Label(10, 5, "Settings", color=Theme.YELLOW))
        
        # Speed Control
        self.cfg_speed = 1000
        s_settings.add_widget(Label(20, 50, "Max Speed:"))
        self.lbl_speed = Label(180, 50, f"{self.cfg_speed}", color=Theme.CYAN)
        s_settings.add_widget(self.lbl_speed)
        s_settings.add_widget(Button(140, 45, 35, 35, "-", callback=lambda: self.adj_speed(-100)))
        s_settings.add_widget(Button(240, 45, 35, 35, "+", callback=lambda: self.adj_speed(100)))
        
        # Accel Control
        self.cfg_accel = 500
        s_settings.add_widget(Label(20, 100, "Acceleration:"))
        self.lbl_accel = Label(180, 100, f"{self.cfg_accel}", color=Theme.CYAN)
        s_settings.add_widget(self.lbl_accel)
        s_settings.add_widget(Button(140, 95, 35, 35, "-", callback=lambda: self.adj_accel(-50)))
        s_settings.add_widget(Button(240, 95, 35, 35, "+", callback=lambda: self.adj_accel(50)))
        
        # Apply Button
        s_settings.add_widget(Button(300, 60, 100, 60, "Apply", callback=self.apply_profile, color=Theme.GREEN))
        
        # Port Selection
        s_settings.add_widget(Label(20, 160, "Serial Port:"))
        self.lbl_port = Label(20, 190, self.client.port, font=Theme.FONT_SMALL, color=Theme.GRAY)
        s_settings.add_widget(self.lbl_port)
        s_settings.add_widget(Button(250, 180, 150, 40, "Scan / Cycle", callback=self.cycle_ports))
        
        # Unlock / Reset
        s_settings.add_widget(Button(20, 230, 150, 40, "Unlock / Reset", callback=self.do_reset, color=Theme.YELLOW))

        self.screens.append(s_settings)

        # --- 4. Tests Screen ---
        s_tests = Screen("Tests")
        s_tests.add_widget(Label(10, 5, "Diagnostics", color=Theme.YELLOW))
        
        # Endstop Indicators
        s_tests.add_widget(Label(20, 50, "Endstops:"))
        self.lbl_endstops = []
        for i in range(6):
            # Small "LED" indicators
            # We use a Label "O" or similar, changing color
            x_pos = 120 + i * 40
            lbl = Label(x_pos, 50, "O", color=Theme.GRAY)
            self.lbl_endstops.append(lbl)
            s_tests.add_widget(lbl)
            # Axis label below
            s_tests.add_widget(Label(x_pos, 70, str(i+1), font=Theme.FONT_SMALL))

        # Test Patterns
        s_tests.add_widget(Label(20, 120, "Test Patterns:"))
        s_tests.add_widget(Button(20, 150, 140, 50, "Square Test", callback=lambda: self.client.run_test(1)))
        s_tests.add_widget(Button(180, 150, 140, 50, "Circle Test", callback=lambda: self.client.run_test(2)))
        s_tests.add_widget(Button(20, 210, 140, 50, "Full Range", callback=lambda: self.client.run_test(3)))
        
        # Init PathManager
        self.path_manager = PathManager()
        self.current_editing_path_name = None
        self.current_editing_point_index = -1
        
        # Init Overlays
        self.keyboard = Keyboard(0, 40, 480, 280, self.on_keyboard_enter, self.on_keyboard_cancel)
        self.popup = None # Dynamic
        
        self.screens.append(s_tests)

        # --- 5. Paths Screen ---
        self.s_paths = Screen("Paths") # Keep ref to update list
        self.s_paths.add_widget(Label(10, 5, "Saved Paths", color=Theme.YELLOW))
        self.s_paths.add_widget(Button(320, 5, 100, 40, "New Path", callback=self.on_new_path, color=Theme.GREEN))
        self.screens.append(self.s_paths)
        
        # --- 6. Path Details Screen (Points List) ---
        self.s_path_details = Screen("Path Details")
        self.s_path_details.add_widget(Label(10, 5, "Path Points", color=Theme.YELLOW))
        self.s_path_details.add_widget(Button(320, 5, 130, 40, "Add Point", callback=self.on_add_point, color=Theme.GREEN))
        self.s_path_details.add_widget(Button(380, 270, 80, 40, "Back", callback=lambda: self.set_screen(4), color=Theme.RED))
        self.screens.append(self.s_path_details)

        # --- 7. Point Edit Screen (Jog & Save) ---
        self.s_point_edit = Screen("Edit Point")
        self.s_point_edit.add_widget(Label(10, 5, "Adjust Position", color=Theme.YELLOW))
        
        # Live Coords Labels (for Edit Screen)
        self.lbl_edit_axes = []
        axes_names = ["X", "Y", "Z", "A", "B", "C"]
        for i, name in enumerate(axes_names):
            col = i // 3
            row = i % 3
            x_pos = 10 + col * 160
            y_pos = 40 + row * 25
            lbl = Label(x_pos, y_pos, f"{name}: 0.00", color=Theme.WHITE, font=Theme.FONT_SMALL)
            self.lbl_edit_axes.append(lbl)
            self.s_point_edit.add_widget(lbl)
            
            # Simple Jog Controls (Smaller to fit)
            # +/- buttons next to label
            self.s_point_edit.add_widget(Button(x_pos + 90, y_pos-2, 30, 25, "-", callback=lambda idx=i: self.move_axis(idx, -50))) # Smaller step
            self.s_point_edit.add_widget(Button(x_pos + 125, y_pos-2, 30, 25, "+", callback=lambda idx=i: self.move_axis(idx, 50)))

        self.s_point_edit.add_widget(Button(20, 260, 120, 50, "Save Point", callback=self.save_point, color=Theme.GREEN))
        self.s_point_edit.add_widget(Button(160, 260, 120, 50, "Cancel", callback=lambda: self.set_screen(5), color=Theme.RED)) # Back to Details
        
        self.screens.append(self.s_point_edit)

        # --- Navigation Bar (Global) ---
        # REPLACED by Hamburger Menu
        self.btn_menu = Button(430, 5, 45, 40, "EQ", callback=self.show_menu, color=Theme.GRAY)
        
        # --- Menu Screen ---
        s_menu = Screen("Menu")
        s_menu.add_widget(Label(10, 10, "Main Menu", color=Theme.CYAN))
        
        # Menu Options
        menu_items = [
            ("Status", 0),
            ("Control", 1),
            ("Settings", 2),
            ("Tests", 3),
            ("Paths", 4)
        ]
        
        y_start = 40
        for name, idx in menu_items:
            s_menu.add_widget(Button(40, y_start, 400, 40, name, callback=lambda i=idx: self.set_screen(i)))
            y_start += 50
            
        # Exit Button
        s_menu.add_widget(Button(40, y_start, 400, 40, "Exit", callback=self.exit_app, color=Theme.RED))
        
        # Back/Close Menu Button (Top Right)
        s_menu.add_widget(Button(430, 5, 45, 40, "X", callback=self.close_menu, color=Theme.RED))

        self.screens.append(s_menu)
        self.menu_screen_idx = len(self.screens) - 1
        
        # Keep track of previous screen to return to? 
        # Or just default to Status? 
        # set_screen logic handles simple switching.
        self.last_screen_idx = 0

    def refresh_paths_list(self):
        # Keep static widgets (Label + Button) = 2
        self.s_paths.widgets = self.s_paths.widgets[:2]
        
        names = self.path_manager.get_path_names()
        y_start = 60
        
        if not names:
            self.s_paths.add_widget(Label(20, 100, "No paths saved.", color=Theme.GRAY))
        else:
            for name in names:
                display_name = (name[:20] + '..') if len(name) > 20 else name
                btn = Button(20, y_start, 440, 40, display_name, callback=lambda n=name: self.on_path_select(n))
                self.s_paths.add_widget(btn)
                y_start += 50

    def refresh_path_details(self):
        # Keep static widgets (Label + Add + Back) = 3
        self.s_path_details.widgets = self.s_path_details.widgets[:3]
        
        # Update Title
        self.s_path_details.widgets[0].text = f"Path: {self.current_editing_path_name}"
        
        points = self.path_manager.get_path(self.current_editing_path_name)
        y_start = 60
        
        if not points:
            self.s_path_details.add_widget(Label(20, 100, "No points in path.", color=Theme.GRAY))
        else:
            for i, p in enumerate(points):
                # Format: P1: X:10 Y:20 ...
                # Just show first 3 axes for brevity or all if possible
                txt = f"P{i+1}: " + " ".join([f"{v:.1f}" for v in p[:3]])
                btn = Button(20, y_start, 440, 40, txt, callback=lambda idx=i: self.on_point_select(idx))
                self.s_path_details.add_widget(btn)
                y_start += 50

    def on_point_select(self, index):
        options = [
            ("Edit Point", lambda: self.open_point_edit(index)),
            ("Delete Point", lambda: self.delete_point(index))
        ]
        self.popup = Popup(90, 60, 300, 200, f"Point {index+1}", options)
        self.popup.show()

    def delete_point(self, index):
        points = self.path_manager.get_path(self.current_editing_path_name)
        if 0 <= index < len(points):
            points.pop(index)
            self.path_manager.add_path(self.current_editing_path_name, points) # Save
            self.refresh_path_details()

    def open_path_details(self, name):
        self.current_editing_path_name = name
        self.set_screen(5) # Path Details Index

    def on_add_point(self):
        self.open_point_edit(-1)

    def open_point_edit(self, index):
        self.current_editing_point_index = index
        # If editing existing, maybe move robot there? 
        # User request didn't specify, but usually safer NOT to auto-move.
        # Just assume we want to Jog to NEW position or Adjust FROM current.
        self.set_screen(6) # Point Edit Index

    def save_point(self):
        # Get current axes from client
        current_pos = self.client.axes # [x, y, z, a, b, c]
        
        points = self.path_manager.get_path(self.current_editing_path_name)
        
        if self.current_editing_point_index == -1:
            # Append
            points.append(current_pos)
        else:
            # Update
            if 0 <= self.current_editing_point_index < len(points):
                points[self.current_editing_point_index] = current_pos
        
        self.path_manager.add_path(self.current_editing_path_name, points) # Save
        # Return to Details
        self.set_screen(5)

    def on_new_path(self):
        self.keyboard.show()

    def on_keyboard_enter(self, text):
        if text:
            self.path_manager.add_path(text, [])
            self.refresh_paths_list()

    def on_keyboard_cancel(self):
        pass

    def on_path_select(self, name):
        # Show Popup Options
        options = [
            ("Edit Path", lambda: self.open_path_details(name)), 
            ("Delete Path", lambda: self.delete_path(name))
        ]
        self.popup = Popup(90, 60, 300, 200, f"Path: {name}", options)
        self.popup.show()

    def delete_path(self, name):
        self.path_manager.delete_path(name)
        self.refresh_paths_list()

    def set_screen(self, idx):
        self.current_screen_idx = idx
        if idx == 4: # Paths
            self.refresh_paths_list()
        elif idx == 5: # Path Details
            self.refresh_path_details()
        # idx 6 is Point Edit (updates live)

    def show_menu(self):
        self.last_screen_idx = self.current_screen_idx
        self.current_screen_idx = self.menu_screen_idx

    def close_menu(self):
        self.current_screen_idx = self.last_screen_idx

    def adj_speed(self, delta):
        self.cfg_speed = max(100, min(5000, self.cfg_speed + delta))
        self.lbl_speed.text = str(self.cfg_speed)

    def adj_accel(self, delta):
        self.cfg_accel = max(50, min(2000, self.cfg_accel + delta))
        self.lbl_accel.text = str(self.cfg_accel)

    def apply_profile(self):
        self.client.set_profile(self.cfg_speed, self.cfg_accel)

    def cycle_ports(self):
        ports = RobotClient.scan_ports()
        if not ports:
            self.lbl_port.text = "No ports found"
            return
        
        # Find current index
        try:
            current_idx = ports.index(self.client.port)
            next_idx = (current_idx + 1) % len(ports)
        except ValueError:
            next_idx = 0
            
        new_port = ports[next_idx]
        self.client.port = new_port
        self.lbl_port.text = new_port
        # Auto-reconnect?
        if self.client.connected:
            self.client.disconnect()
            self.client.connect()

    def do_reset(self):
        self.client.reset_alarm()

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
        # Use Absolute Positioning as requested
        # Calculate target based on current known position
        current_val = self.client.axes[axis]
        target = current_val + steps
        self.client.move_absolute(axis, target)

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
                    
                    # Priority 1: Keyboard Overlay
                    if self.keyboard.visible:
                        self.keyboard.handle_touch(tx, ty)
                        # Block other input
                    
                    # Priority 2: Popup Overlay
                    elif self.popup and self.popup.visible:
                        if not self.popup.handle_touch(tx, ty):
                            # Clicked outside
                            pass
                        # Block other input
                    
                    else:
                        # Global Menu Button (Only if NOT on menu screen)
                        if self.current_screen_idx != self.menu_screen_idx:
                            if self.btn_menu.contains(tx, ty):
                                self.btn_menu.on_click()
                                # Skip processing screen widgets if menu clicked
                                continue
                        
                        # Check Current Screen Widgets
                        self.screens[self.current_screen_idx].handle_touch(tx, ty)

                # 3. Draw
                # Update Status if connected
                self.client.update_status()
                
                # Update Labels
                if self.client.connected:
                    self.lbl_state.text = f"State: {self.client.status}"
                    for i, val in enumerate(self.client.axes):
                        self.lbl_axes[i].text = f"{['X','Y','Z','A','B','C'][i]}: {val:.2f}"
                        # Also update Edit Screen labels
                        if hasattr(self, 'lbl_edit_axes') and i < len(self.lbl_edit_axes):
                             self.lbl_edit_axes[i].text = f"{['X','Y','Z','A','B','C'][i]}: {val:.2f}"
                    
                    # Update Endstops
                    if hasattr(self.client, 'endstops') and len(self.client.endstops) >= 6:
                        for i in range(6):
                            is_triggered = (self.client.endstops[i] == '1')
                            self.lbl_endstops[i].color = Theme.RED if is_triggered else Theme.GREEN
                
                # Create blank image
                image = Image.new("RGB", (480, 320), "black")
                draw = ImageDraw.Draw(image)
                
                # Draw Current Screen
                self.screens[self.current_screen_idx].draw(draw)
                
                # Draw Global Menu Button (Overlay) - Only if NOT on menu screen
                if self.current_screen_idx != self.menu_screen_idx:
                    self.btn_menu.draw(draw)

                # Draw Popup Overlay
                if self.popup and self.popup.visible:
                    self.popup.draw(draw)

                # Draw Keyboard Overlay
                if self.keyboard.visible:
                    self.keyboard.draw(draw)
                    
                # 4. Flip and Display
                # Fix mirroring - Removed as user reported it is mirrored WITH this.
                # image = image.transpose(Image.FLIP_LEFT_RIGHT)
                self.device.display(image)
                
                # Cap FPS
                time.sleep(0.05)
                
                # Reset button states
                self.btn_menu.pressed = False
                for w in self.screens[self.current_screen_idx].widgets:
                    if isinstance(w, Button):
                        w.pressed = False
                
                # Also reset keyboard keys if visible
                if self.keyboard.visible:
                    self.keyboard.reset_keys()

        except KeyboardInterrupt:
            pass
        finally:
            self.client.disconnect()
            print("Exiting...")

if __name__ == "__main__":
    app = RobotApp()
    app.run()
