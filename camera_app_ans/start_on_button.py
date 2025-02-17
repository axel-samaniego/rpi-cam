#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import subprocess

# GPIO pin number
GPIO_PIN = 6

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        # Wait for button press (LOW state)
        input_state = GPIO.input(GPIO_PIN)
        if input_state == GPIO.LOW:
            print("Button pressed!")
            print("Running Program!")            
            break  # Exit the loop and terminate the script

        time.sleep(0.1)  # Polling interval

finally:
    GPIO.cleanup()  # Clean up GPIO on exit
    subprocess.Popen(['python', '/home/rpi_axel/rpi_axel/projects/rpi-cam/camera_app_ans/run_picam.py'])
    exit()
