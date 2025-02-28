import os
import random
import qrcode
from PIL import Image
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
    """Generates and saves a QR code with a random 4-digit number."""
    number = "".join(random.sample("0123456789", 4))  # Unique 4-digit number
    print(f"Generating QR Code for: {number}")

    if not os.path.exists("data"):
        os.makedirs("data")

    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(number)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")
        img = img.convert("RGB")
        filename = f"data/qr_code_{number}.jpg"
        img.save(filename, "JPEG")
        print_file(filename, True)

        print(f"QR code saved as {filename}")

    except Exception as e:
        print(f"Error generating QR code: {e}")

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

