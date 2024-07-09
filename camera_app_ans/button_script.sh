#!/bin/bash

# GPIO pin number
GPIO=6

# Set GPIO pin as input
gpio -g mode $GPIO in

# Loop indefinitely
while true; do
    # Wait for button press (LOW state)
    if [ "$(gpio -g read $GPIO)" = "0" ]; then
        echo "Button pressed!"
        # Replace '/path/to/your_program' with the actual path to your program
        /path/to/your_program &
        sleep 0.5  # Debounce time
        while [ "$(gpio -g read $GPIO)" = "0" ]; do
            sleep 0.1  # Wait for button release
        done
        echo "PiCam Starting!"
        break  # Exit the loop and terminate the script
    fi
    sleep 0.1  # Polling interval
done
