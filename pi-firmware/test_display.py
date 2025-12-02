import time
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import ili9486
from PIL import Image, ImageDraw, ImageFont

def main():
    # SPI configuration for Raspberry Pi
    # DC=24, RST=25 are common for these hats, but might need adjustment
    # CS=0 (CE0)
    serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25)
    
    # Initialize device
    # rotate=1 is standard landscape. We will fix mirroring in software.
    device = ili9486(serial, rotate=1)

    print("Display initialized. Drawing...")

    # Load a font
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
    except IOError:
        font = ImageFont.load_default()

    # Create a blank image manually
    # We use "RGB" mode.
    image = Image.new("RGB", device.size)
    draw = ImageDraw.Draw(image)

    # Draw on the image
    # Note: device.bounding_box is (0, 0, width-1, height-1)
    draw.rectangle((0, 0, device.width-1, device.height-1), outline="white", fill="black")
    draw.text((10, 10), "Grova Robot", fill="cyan", font=font)
    draw.text((10, 40), "Display Test", fill="yellow", font=font)
    draw.text((10, 70), "OK!", fill="green", font=font)

    # Fix mirroring by flipping the image
    print("Flipping image to fix mirror effect...")
    image = image.transpose(Image.FLIP_LEFT_RIGHT)

    # Send to display
    device.display(image)

    print("Drawing complete. Sleeping for 10 seconds...")
    time.sleep(10)
    print("Done.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
