import time
import os
import cv2
import RPi.GPIO as GPIO

# Define GPIO pin for the button
BUTTON_PIN = 21

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Define the directory to save images
home_directory = os.path.expanduser('~')

# Define the directory to save images
SAVE_DIR = os.path.join(home_directory, 'rpi_axel', 'images')
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)



def capture_image(cam):
    # Define the image filename with timestamp
    # Capture frame-by-frame
    ret, frame = cam.read()
    if not ret:
        print("Error: Failed to capture image.")
        return

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    image_path = os.path.join(SAVE_DIR, f"image_{timestamp}.jpg")

    # Capture and save the image
    cv2.imwrite(image_path, frame)
    print(f"Image saved to {image_path}")

def main():
    # Initialize the camera
    cam = cv2.VideoCapture(0, cv2.CAP_V4L2)
    
    try:
        print("Press the button to capture an image...")
        while True:
            # Wait for the button press
            button_state = GPIO.input(BUTTON_PIN)
            if button_state == GPIO.LOW:
                print("Button pressed!")
                capture_image(cam)
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
