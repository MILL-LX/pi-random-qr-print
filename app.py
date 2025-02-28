import os
import random
import qrcode
from PIL import Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO
import time
import atexit
from print_util import print_file

SWITCH_PIN = 4  # GPIO 4

def setup_gpio():
    """Configures the GPIO pin for the switch."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Enable internal pull-up

def generate_qr_code():
    """Generates and saves a QR code with a random 4-digit number, adding the number below the QR code."""
    number = "".join(random.sample("0123456789", 4))  # Unique 4-digit number
    print(f"Generating QR Code for: {number}")

    if not os.path.exists("data"):
        os.makedirs("data")

    try:
        # Generate QR code
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(number)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")
        img = img.convert("RGB")

        # Add text below the QR code
        img_with_text = add_text_below_qr(img, number)

        # Save final image
        filename = f"data/qr_code_{number}.jpg"
        img_with_text.save(filename, "JPEG")
        print_file(filename, True)

        print(f"QR code saved as {filename}")

    except Exception as e:
        print(f"Error generating QR code: {e}")

def add_text_below_qr(qr_image, text):
    """Adds the given text below the QR code using DejaVuSans-Bold.ttf at size 72."""
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_size = 72

    # Load the DejaVuSans-Bold font
    font = ImageFont.truetype(font_path, font_size)

    # Get image size
    qr_width, qr_height = qr_image.size
    text_height = 120  # Extra space for large text

    # Create new image with extra space for text
    new_img = Image.new("RGB", (qr_width, qr_height + text_height), "white")
    new_img.paste(qr_image, (0, 0))

    # Draw text on the new image
    draw = ImageDraw.Draw(new_img)
    bbox = draw.textbbox((0, 0), text, font=font)  # Get text size
    text_width = bbox[2] - bbox[0]  # Calculate text width
    text_x = (qr_width - text_width) // 2
    text_y = qr_height + 20  # Adjusted for spacing

    draw.text((text_x, text_y), text, fill="black", font=font)

    return new_img

def wait_for_button_release():
    """Debounce and wait for button release."""
    time.sleep(0.1)  # Debounce delay
    while GPIO.input(SWITCH_PIN) == GPIO.LOW:
        time.sleep(0.1)

def main():
    """Main loop to monitor switch state and trigger QR code generation."""
    setup_gpio()
    atexit.register(GPIO.cleanup)  # Ensure cleanup on exit
    print("Waiting for button press on GPIO 4...")

    try:
        while True:
            if GPIO.input(SWITCH_PIN) == GPIO.LOW:  # Button pressed
                generate_qr_code()
                wait_for_button_release()
                print("Waiting for next press...")

            time.sleep(0.1)  # Polling delay to reduce CPU usage

    except KeyboardInterrupt:
        print("\nExiting program...")

if __name__ == "__main__":
    main()

