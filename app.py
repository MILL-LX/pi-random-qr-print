import os
import random
import qrcode
from PIL import Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO
import time
import atexit
from datetime import datetime
from print_util import print_file

SWITCH_PIN = 4  # GPIO 4

def setup_gpio():
    """Configures the GPIO pin for the switch."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Enable internal pull-up

def generate_qr_code():
    """Generates and saves a QR code with a random 4-digit number, adding title, timestamp, and number below."""
    number = "".join(random.sample("0123456789", 4))  # Unique 4-digit number
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current date and time

    print(f"Generating QR Code for: {number} at {timestamp}")

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
        img_with_text = add_text_below_qr(img, number, timestamp)

        # Save final image
        filename = f"data/qr_code_{number}.jpg"
        img_with_text.save(filename, "JPEG")
        print_file(filename, True)

        print(f"QR code saved as {filename}")

    except Exception as e:
        print(f"Error generating QR code: {e}")

def add_text_below_qr(qr_image, number, timestamp):
    """Adds number (18pt under QR code), title ("Oficinas" & "Abertas" in 36pt), and timestamp (18pt) centered below."""
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    
    # Load fonts
    font_number = ImageFont.truetype(font_path, 18)  # 4-digit number (now 18pt)
    font_title = ImageFont.truetype(font_path, 36)  # "Oficinas" & "Abertas" in 36pt
    font_timestamp = ImageFont.truetype(font_path, 18)  # Timestamp (now 18pt)

    # Get QR image size
    qr_width, qr_height = qr_image.size
    text_height = 200  # Adjusted extra space for number, title, and timestamp

    # Create new image with extra space for text
    new_img = Image.new("RGB", (qr_width, qr_height + text_height), "white")
    new_img.paste(qr_image, (0, 0))

    # Draw text on the new image
    draw = ImageDraw.Draw(new_img)

    def draw_centered_text(text, font, y_offset):
        """Helper function to center text on the image."""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x_pos = (qr_width - text_width) // 2
        draw.text((x_pos, y_offset), text, fill="black", font=font)

    # Position all text elements centered
    number_y = qr_height + 10  # 10px below QR code
    oficinas_y = number_y + 30  # 30px below the number
    abertas_y = oficinas_y + 45  # 45px below "Oficinas"
    timestamp_y = abertas_y + 45  # 45px below "Abertas"

    draw_centered_text(number, font_number, number_y)
    draw_centered_text("Oficinas", font_title, oficinas_y)
    draw_centered_text("Abertas", font_title, abertas_y)
    draw_centered_text(timestamp, font_timestamp, timestamp_y)

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

