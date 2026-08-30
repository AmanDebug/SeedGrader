# actuation/valve_mock.py
import time
import threading

class MockValveController:
    def __init__(self, pin=18):
        self.pin = pin
        print(f"[INIT] Mock Valve initialized on virtual PIN {self.pin}")

    def pulse_valve(self, duration_ms=10):
        print(f"[{time.time():.4f}] >>> VALVE FIRED (Pulse: {duration_ms}ms) <<<")

    def schedule_ejection(self, delay_ms, duration_ms=10):
        print(f"[{time.time():.4f}] Ejection scheduled in {delay_ms:.2f}ms")
        threading.Timer(delay_ms / 1000.0, self.pulse_valve, args=[duration_ms]).start()