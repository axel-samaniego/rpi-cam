#!/bin/bash

# GPIO pin number
GPIO=6

# Loop indefinitely
while true; do
    # Check if button is pressed
    if [ "$(pigpio read $GPIO)" = "0" ]; then
        echo "Button pressed!"
        echo "Starting Program!"
        # Replace '/path/to/your_program' with the actual path to your program
        python run_picam.py &
        sleep 0.5  # Debounce time
        while [ "$(pigpio read $GPIO)" = "0" ]; do
            sleep 0.1  # Wait for button release
        done
        echo "Button released!"
        break  # Exit the loop and terminate the script
    fi
    sleep 0.1  # Polling interval
done
