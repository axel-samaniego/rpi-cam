import time
import os
import cv2
import RPi.GPIO as GPIO
from picamera2 import Picamera2

# Define GPIO pin for the button
BUTTON_PIN = 21

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Define the directory to save images
SAVE_DIR = os.path.expanduser('~/rpi_axel/images')
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)



def capture_image(picam):
    # Define the image filename with timestamp
    img = picam.capture_array()
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    image_path = os.path.join(SAVE_DIR, f"image_{timestamp}.jpg")

    # Capture and save the image
    cv2.imwrite(image_path, img)
    
    print(f"Image saved to {image_path}")

def main():
    # Initialize the camera
    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration())
    picam2.preview_configuration.main.size = (800,800)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.preview_configuration.align()
    picam2.configure("preview")
    picam2.start()
    try:
        print("Press the button to capture an image...")
        while True:
            # Wait for the button press
            button_state = GPIO.input(BUTTON_PIN)
            if button_state == GPIO.LOW:
                print("Button pressed!")
                capture_image(picam2)
                # Debounce the button press
                time.sleep(0.5)
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        # Clean up GPIO
        GPIO.cleanup()
        print("Cleanup completed.")

if __name__ == "__main__":
    main()
