import time
from PIL import Image, ImageDraw, ImageFont
import evdev
import select

class Theme:
    BLACK = "black"
    WHITE = "white"
    CYAN = "cyan"
    YELLOW = "yellow"
    GREEN = "green"
    RED = "red"
    GRAY = "#444444"
    DARK_GRAY = "#222222"
    
    FONT_MAIN = None
    FONT_SMALL = None

    @staticmethod
    def load_fonts():
        try:
            Theme.FONT_MAIN = ImageFont.truetype("DejaVuSans-Bold.ttf", 18)
            Theme.FONT_SMALL = ImageFont.truetype("DejaVuSans.ttf", 14)
        except IOError:
            Theme.FONT_MAIN = ImageFont.load_default()
            Theme.FONT_SMALL = ImageFont.load_default()

class TouchInput:
    def __init__(self, device_path=None):
        self.device_path = device_path
        self.device = None
        self.x = 0
        self.y = 0
        self.last_touch_time = 0
        self.touch_down = False
        
        # Calibration (approximate for 3.5 inch MPI3508/XPT2046)
        # These might need tuning!
        self.min_x = 200
        self.max_x = 3900
        self.min_y = 200
        self.max_y = 3900
        self.screen_width = 480
        self.screen_height = 320
        
        self._find_device()

    def _find_device(self):
        if self.device_path:
            try:
                self.device = evdev.InputDevice(self.device_path)
                return
            except:
                pass
        
        # Auto-detect
        try:
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            for dev in devices:
                if 'touch' in dev.name.lower() or 'ads7846' in dev.name.lower() or 'xpt2046' in dev.name.lower():
                    self.device = dev
                    print(f"Found touch device: {dev.name} at {dev.path}")
                    break
        except Exception as e:
            print(f"Error finding touch device: {e}")

    def update(self):
        if not self.device:
            return None

        # Non-blocking read
        r, w, x = select.select([self.device.fd], [], [], 0.0)
        if r:
            for event in self.device.read():
                if event.type == evdev.ecodes.EV_ABS:
                    if event.code == evdev.ecodes.ABS_X:
                        # Map X (Note: X/Y might be swapped depending on rotation)
                        # Assuming landscape where Touch X aligns with Screen X
                        self.x = self._map(event.value, self.min_x, self.max_x, 0, self.screen_width)
                    elif event.code == evdev.ecodes.ABS_Y:
                        self.y = self._map(event.value, self.min_y, self.max_y, 0, self.screen_height)
                elif event.type == evdev.ecodes.EV_KEY:
                    if event.code == evdev.ecodes.BTN_TOUCH:
                        self.touch_down = (event.value == 1)
                        if self.touch_down:
                            self.last_touch_time = time.time()
                            return (self.x, self.y)
        return None

    def _map(self, x, in_min, in_max, out_min, out_max):
        return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

class Widget:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.visible = True

    def contains(self, tx, ty):
        if not self.visible: return False
        return self.x <= tx <= self.x + self.w and self.y <= ty <= self.y + self.h

    def draw(self, draw):
        pass

    def on_click(self):
        pass

class Button(Widget):
    def __init__(self, x, y, w, h, text, callback=None, color=Theme.GRAY):
        super().__init__(x, y, w, h)
        self.text = text
        self.callback = callback
        self.color = color
        self.pressed = False

    def draw(self, draw):
        if not self.visible: return
        
        fill = Theme.CYAN if self.pressed else self.color
        outline = Theme.WHITE
        
        draw.rectangle((self.x, self.y, self.x + self.w, self.y + self.h), fill=fill, outline=outline)
        
        # Center text
        # Using getbbox if available (Pillow 8+), else fallback
        try:
            bbox = draw.textbbox((0, 0), self.text, font=Theme.FONT_MAIN)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except:
            text_w, text_h = draw.textsize(self.text, font=Theme.FONT_MAIN)
            
        tx = self.x + (self.w - text_w) // 2
        ty = self.y + (self.h - text_h) // 2
        
        text_color = Theme.BLACK if self.pressed else Theme.WHITE
        draw.text((tx, ty), self.text, fill=text_color, font=Theme.FONT_MAIN)

    def on_click(self):
        self.pressed = True
        if self.callback:
            self.callback()
        # Reset pressed state is handled by the loop usually, but for simple UI we might toggle
        # For now, let's assume it's momentary.

class Label(Widget):
    def __init__(self, x, y, text, color=Theme.WHITE, font=None):
        super().__init__(x, y, 0, 0)
        self.text = text
        self.color = color
        self.font = font or Theme.FONT_MAIN

    def draw(self, draw):
        if not self.visible: return
        draw.text((self.x, self.y), self.text, fill=self.color, font=self.font)

class Screen:
    def __init__(self, name):
        self.name = name
        self.widgets = []

    def add_widget(self, widget):
        self.widgets.append(widget)

    def draw(self, draw):
        for w in self.widgets:
            w.draw(draw)

    def handle_touch(self, x, y):
        for w in self.widgets:
            if w.contains(x, y):
                w.on_click()
                return True
        return False
