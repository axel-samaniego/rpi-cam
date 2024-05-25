import cv2
import RPi.GPIO as GPIO
import time

# Define GPIO pin for the button
BUTTON_PIN = 21

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Define the directory to save images
SAVE_DIR = '~/rpi_axel/images'  # Change this to your desired directory

# Initialize the camera
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()

def capture_image():
    # Capture frame-by-frame
    ret, frame = camera.read()
    if not ret:
        print("Error: Failed to capture image.")
        return

    # Define the image filename with timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    image_path = f"{SAVE_DIR}image_{timestamp}.jpg"

    # Save the captured image
    cv2.imwrite(image_path, frame)
    print(f"Image saved to {image_path}")

try:
    print("Press the button to capture an image...")
    while True:
        # Wait for the button press
        button_state = GPIO.input(BUTTON_PIN)
        if button_state == GPIO.LOW:
            print("Button pressed!")
            capture_image()
            # Debounce the button press
            time.sleep(0.5)

except KeyboardInterrupt:
    print("Program terminated by user.")

finally:
    # Release the camera and clean up GPIO
    camera.release()
    GPIO.cleanup()
    print("Cleanup completed.")