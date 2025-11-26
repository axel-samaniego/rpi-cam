#!/usr/bin/env python3
import os
import sys
import time
from dataclasses import dataclass

import RPi.GPIO as GPIO
from picamera2 import Picamera2, Preview


# ====== CONFIG ======

SAVE_DIR = "/home/pi/camera_photos"       # folder where photos are saved
IMG_NUM_FILE = "/home/pi/img_num.txt"     # file storing next image number

CAPTURE_BUTTON_PIN = 21   # pull button to GND to capture
QUIT_BUTTON_PIN = 6       # pull button to GND to quit the app

BUTTON_POLL_INTERVAL = 0.01  # seconds between GPIO polls


# ====== HELPER FUNCTIONS ======

def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def read_image_number() -> int:
    """Read next image number from file, or start at 1 if not present."""
    try:
        with open(IMG_NUM_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 1


def write_image_number(n: int):
    with open(IMG_NUM_FILE, "w") as f:
        f.write(str(n))


@dataclass
class ButtonState:
    capture_last: bool = True  # True = not pressed (because of pull-up)
    quit_last: bool = True


# ====== MAIN APP CLASS ======

class CameraApp:
    def __init__(self):
        print("[camera_app] Initializing...")

        # Setup storage
        ensure_dir(SAVE_DIR)
        self.img_num = read_image_number()
        print(f"[camera_app] Starting from image number {self.img_num}")

        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(CAPTURE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(QUIT_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.button_state = ButtonState()

        # Setup camera
        self.picam = Picamera2()

        # Configure preview
        # Adjust size to match your display resolution
        preview_config = self.picam.create_preview_configuration(
            main={"size": (800, 480), "format": "RGB888"}
        )
        self.picam.configure(preview_config)

        # Start preview (requires a graphical desktop / X / Wayland)
        self.picam.start_preview(Preview.QTGL)
        self.picam.start()
        print("[camera_app] Camera started, preview running.")

        self.running = True

    # ---------- Event handlers ----------

    def on_capture_button_pressed(self):
        """Capture a still and save to disk."""
        filename = f"image_{self.img_num:04d}.jpg"
        path = os.path.join(SAVE_DIR, filename)
        print(f"[camera_app] Capturing -> {path}")
        try:
            # This captures from the camera and writes directly to a JPEG file
            self.picam.capture_file(path)
            self.img_num += 1
            write_image_number(self.img_num)
            print("[camera_app] Capture complete.")
        except Exception as e:
            print(f"[camera_app] ERROR during capture: {e}", file=sys.stderr)

    def on_quit_button_pressed(self):
        """Request app shutdown."""
        print("[camera_app] Quit button pressed. Exiting...")
        self.running = False

    # ---------- Main loop ----------

    def main_loop(self):
        print("[camera_app] Entering main loop. Ready for button presses.")
        try:
            while self.running:
                self._poll_buttons()
                time.sleep(BUTTON_POLL_INTERVAL)
        except KeyboardInterrupt:
            print("[camera_app] KeyboardInterrupt received, exiting.")
        finally:
            self.cleanup()

    def _poll_buttons(self):
        # Buttons are wired to GND with pull-up; pressed == False
        capture_now = GPIO.input(CAPTURE_BUTTON_PIN)
        quit_now = GPIO.input(QUIT_BUTTON_PIN)

        # Detect *edge* from HIGH -> LOW (not-pressed -> pressed)
        if self.button_state.capture_last and not capture_now:
            self.on_capture_button_pressed()

        if self.button_state.quit_last and not quit_now:
            self.on_quit_button_pressed()

        self.button_state.capture_last = capture_now
        self.button_state.quit_last = quit_now

    # ---------- Cleanup ----------

    def cleanup(self):
        print("[camera_app] Cleaning up resources...")
        try:
            # Picamera2 cleanup
            try:
                self.picam.stop_preview()
            except Exception:
                pass
            try:
                self.picam.stop()
            except Exception:
                pass
            try:
                self.picam.close()
            except Exception:
                pass

            # GPIO cleanup
            GPIO.cleanup()
        finally:
            print("[camera_app] Cleanup complete. Bye.")


# ====== ENTRY POINT ======

def main():
    app = CameraApp()
    app.main_loop()


if __name__ == "__main__":
    main()
