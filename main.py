# main.py
import os
import cv2
import time
import math

try:
    from camera.capture_mock import MockCamera
    from actuation.valve_mock import MockValveController
except ImportError:# Fallback for direct script execution
    from MockCamera import MockCamera
    from MockValveController import MockValveController

# Configuration constants
MOCK_MODE = True
DROP_DISTANCE_M = 0.08      # 8 cm from camera focal point to air nozzle
INITIAL_VELOCITY_M_S = 0.5  # Seed exit speed from chute
GRAVITY = 9.81              # m/s^2
VALVE_LATENCY_MS = 3.0      # Mechanical opening delay
CAMERA_FOV_HEIGHT_M = 0.06  # The physical height the camera sees (e.g., 6 cm)
CHUTE_TO_TOP_FRAME_M = 0.01 # Distance from chute exit to the top edge of the camera view

def calculate_ejection_delay(y_pixel, frame_height=480): # Note: hsv_tuner resizes to 480
    # 1. Convert pixel position to physical distance down the frame
    pixel_ratio = y_pixel / float(frame_height)
    distance_down_frame_m = pixel_ratio * CAMERA_FOV_HEIGHT_M
    
    # 2. Calculate actual physical distance from chute to current seed position
    current_seed_drop_m = CHUTE_TO_TOP_FRAME_M + distance_down_frame_m
    
    # 3. Calculate how much further it has to fall to hit the nozzle
    remaining_distance_m = DROP_DISTANCE_M - current_seed_drop_m
    
    # 4. Calculate time for remaining distance (Simplified constant velocity for short drops)
    # Using v = u + at to find current velocity, then t = d/v for remaining
    current_velocity = INITIAL_VELOCITY_M_S + (GRAVITY * math.sqrt(2 * current_seed_drop_m / GRAVITY))
    t_arrival = remaining_distance_m / current_velocity
    
    t_arrival_ms = t_arrival * 1000.0
    delay_ms = max(0.0, t_arrival_ms - VALVE_LATENCY_MS)
    
    return delay_ms


def main():
    video_source = "demo1.mp4" if os.path.exists("demo1.mp4") else 0
    camera = MockCamera(video_source) if MOCK_MODE else None
    valve = MockValveController(pin=18)

    print(f"Starting pipeline in MOCK mode using source: {video_source}")
    while True:
        start_compute = time.time()
        ret, frame = camera.read()
        if not ret:
            break

        # --- Phase 2: Mock Defect Detection (HSV Thresholding) ---
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Sample defect mask: detect dark/discolored seeds
        mask = cv2.inRange(hsv, (0, 0, 0), (180, 255, 60))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            if cv2.contourArea(cnt) > 100:  # Filter noise
                x, y, w, h = cv2.boundingRect(cnt)

                # Compute latency & schedule pulse
                compute_latency_ms = (time.time() - start_compute) * 1000.0
                ejection_delay = calculate_ejection_delay(y) - compute_latency_ms

                valve.schedule_ejection(ejection_delay)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        cv2.imshow("Sorter Simulation", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()