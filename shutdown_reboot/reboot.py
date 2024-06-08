import RPi.GPIO as GPIO
import time
import os

# Define the GPIO pin
BUTTON_PIN = 21

try:
    # Set up the GPIO pin
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def button_callback(channel):
        print("Button was pushed!")
        os.system("sudo reboot")

    # Add event detection on the GPIO pin
    GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)

    while True:
        time.sleep(1)  # Keep the script running

except Exception as e:
    print("Error:", e)

finally:
    GPIO.cleanup()  # Clean up GPIO on script exit
