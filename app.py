import random
import qrcode
from PIL import Image
import RPi.GPIO as GPIO
import time

from print_util import print_file

# GPIO Pin Configuration
SWITCH_PIN = 4  # Changed to GPIO 4

def setup_gpio():
    """Configures the GPIO pin for the switch."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Enable internal pull-up

def generate_qr_code():
    """Generates and saves a QR code with a random 4-digit number."""
    number = "".join(random.sample("0123456789", 4))  # Unique 4-digit number
    print(f"Generating QR Code for: {number}")

    # Create a QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(number)
    qr.make(fit=True)

    # Convert QR code to an image
    img = qr.make_image(fill="black", back_color="white")
    img = img.convert("RGB")  # Ensure it's in RGB mode for JPG compatibility
    filename = f"data/qr_code_{number}.jpg"
    img.save(filename, "JPEG")
    print_file(filename, True)

    print(f"QR code saved as {filename}")

def main():
    """Main loop to monitor switch state and trigger QR code generation."""
    setup_gpio()
    print("Waiting for button press on GPIO 4...")

    try:
        while True:
            if GPIO.input(SWITCH_PIN) == GPIO.LOW:  # Button pressed
                generate_qr_code()
                
                # Wait for button release before continuing
                while GPIO.input(SWITCH_PIN) == GPIO.LOW:
                    time.sleep(0.1)
                
                print("Waiting for next press...")
            
            time.sleep(0.1)  # Polling delay to reduce CPU usage

    except KeyboardInterrupt:
        print("\nExiting program...")

    finally:
        GPIO.cleanup()  # Clean up GPIO on exit

if __name__ == "__main__":
    main()

