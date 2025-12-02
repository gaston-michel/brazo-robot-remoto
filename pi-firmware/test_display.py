import time
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import ili9486
from PIL import ImageFont

def main():
    # SPI configuration for Raspberry Pi
    # DC=24, RST=25 are common for these hats, but might need adjustment
    # CS=0 (CE0)
    serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25)
    
    # Initialize device
    # rotate=1 might be needed depending on orientation
    device = ili9486(serial, rotate=1)

    print("Display initialized. Drawing...")

    # Load a font
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
    except IOError:
        font = ImageFont.load_default()

    # Draw on the display
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((10, 10), "Grova Robot", fill="cyan", font=font)
        draw.text((10, 40), "Display Test", fill="yellow", font=font)
        draw.text((10, 70), "OK!", fill="green", font=font)

    print("Drawing complete. Sleeping for 10 seconds...")
    time.sleep(10)
    print("Done.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
