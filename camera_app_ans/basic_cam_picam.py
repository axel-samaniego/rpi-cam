import time
import os
import cv2
import RPi.GPIO as GPIO
import sys
from picamera2 import Picamera2
import subprocess

class PiCam:
    def __init__(self):
        # Define GPIO pin for the button
        self.CAP_BUTTON_PIN = 21
        self.QUIT_BUTTON_PIN = 6
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.CAP_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.QUIT_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.IMG_NUM_FILE = "/home/rpi_axel/rpi_axel/projects/rpi-cam/img_num.txt"
        self.img_num = self.read_image_number()
        

        # Define the directory to save images
        # Get the home directory programmatically

        # Define the directory to save images
        self.SAVE_DIR = '/home/rpi_axel/rpi_axel/images'
        if not os.path.exists(self.SAVE_DIR):
            os.makedirs(self.SAVE_DIR)

        self.picam = self.create_cam()


    def write_image_number(self):
        with open(self.IMG_NUM_FILE, 'w') as file:
            file.write(str(self.img_num))
        print("Num save complete")

    def read_image_number(self):
        # open the img_num file
        if os.path.exists(self.IMG_NUM_FILE):
            with open(self.IMG_NUM_FILE, 'r') as file:
                img_num = int(file.read().strip())
        else:
            img_num = 0

        return img_num

    def create_cam(self):
        
        picam2 = Picamera2()
        picam2.configure(picam2.create_still_configuration())
        picam2.preview_configuration.main.size = (800,800)
        picam2.preview_configuration.main.format = "RGB888"
        picam2.preview_configuration.align()
        picam2.configure("preview")
        picam2.start()
        return picam2

    def capture_image(self):
        # Define the image filename with timestamp
        img = self.picam.capture_array()
        image_path = os.path.join(self.SAVE_DIR, f"image_{self.img_num:04d}.jpg")
        # self.display_image(img)

        # Capture and save the image
        cv2.imwrite(image_path, img)
        self.img_num+=1
        print(f"Image saved to {image_path}")
        self.write_image_number()
    
    def display_image(self, img):
        cv2.namedWindow('Captured Image', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('Captured Image', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        img_color_fixed = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cv2.imshow('Captured Image', img_color_fixed)
        cv2.waitKey(3000)  # Display the image for 3000 ms (3 seconds)
        cv2.destroyAllWindows()

    
    def terminate_cam(self):
        print("Cleaning GPIO and closing camera")
        GPIO.cleanup()
        self.picam.close()
        subprocess.Popen(['/home/rpi_axel/.pyenv/shims/python', 'start_on_button.py'])
        print("Cleanup completed.")
        sys.exit()

    def run_cam(self):    
        # Initialize the camera
        
        try:
            print("Press the button to capture an image...")
            while True:
                # Wait for the button press
                cap_button_state = GPIO.input(self.CAP_BUTTON_PIN)
                quit_button_state = GPIO.input(self.QUIT_BUTTON_PIN)
                if cap_button_state == GPIO.LOW:
                    print("Button pressed!")
                    self.capture_image()
                    # Debounce the button press
                    time.sleep(0.5)
                if quit_button_state == GPIO.LOW:
                    print("Button pressed to terminate program")
                    self.terminate_cam()

        except KeyboardInterrupt:
            print("Program terminated by user.")
        finally:
            # Clean up GPIO
            self.terminate_cam
       

