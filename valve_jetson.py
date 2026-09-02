import Jetson.GPIO as GPIO
import time
import threading

class JetsonValveController:
    def __init__(self, pin=18):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)  # Use standard Broadcom pin numbering
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)
        print(f"[INIT] Physical Valve initialized on GPIO {self.pin}")

    def pulse_valve(self, duration_ms=10):
        # Fire the MOSFET
        GPIO.output(self.pin, GPIO.HIGH)
        time.sleep(duration_ms / 1000.0)
        GPIO.output(self.pin, GPIO.LOW)

    def schedule_ejection(self, delay_ms, duration_ms=10):
        threading.Timer(delay_ms / 1000.0, self.pulse_valve, args=[duration_ms]).start()

    def cleanup(self):
        GPIO.cleanup()