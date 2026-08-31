# main.py
import os
import cv2
import time
import math

try:
    from camera.capture_mock import MockCamera
    from actuation.valve_mock import MockValveController
except ImportError:
    # Fallback for direct script execution
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

def calculate_ejection_delay(y_pixel, frame_height=480): 
    # 1. Convert pixel position to physical distance down the frame
    pixel_ratio = y_pixel / float(frame_height)
    distance_down_frame_m = pixel_ratio * CAMERA_FOV_HEIGHT_M
    
    # 2. Calculate actual physical distance from chute to current seed position
    current_seed_drop_m = CHUTE_TO_TOP_FRAME_M + distance_down_frame_m
    
    # 3. Calculate how much further it has to fall to hit the nozzle
    remaining_distance_m = DROP_DISTANCE_M - current_seed_drop_m
    
    # 4. Calculate time for remaining distance (Simplified constant velocity for short drops)
    current_velocity = INITIAL_VELOCITY_M_S + (GRAVITY * math.sqrt(2 * current_seed_drop_m / GRAVITY))
    t_arrival = remaining_distance_m / current_velocity
    
    t_arrival_ms = t_arrival * 1000.0
    delay_ms = max(0.0, t_arrival_ms - VALVE_LATENCY_MS)
    
    return delay_ms

def main():
    video_source = "finalSeedDemo.mp4" if os.path.exists("finalSeedDemo.mp4") else 0
    camera = MockCamera(video_source) if MOCK_MODE else None
    valve = MockValveController(pin=18)

    print(f"Starting pipeline in MOCK mode using source: {video_source}")

    TRIGGER_Y_LINE = 240  # The middle of your 480p resized frame
    
    while True:
        start_compute = time.time()
        ret, frame = camera.read()
        if not ret:
            break

        # --- Phase 2: Mock Defect Detection (HSV Thresholding) ---
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Sample defect mask: detect dark/discolored seeds
        mask = cv2.inRange(hsv, (0, 0, 0), (179, 255, 87))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            if cv2.contourArea(cnt) > 100:
                x, y, w, h = cv2.boundingRect(cnt)
                
                # Calculate the Center of Mass (Centroid) of the seed
                cy = y + (h // 2)
                cx = x + (w // 2)

                # Draw a blue virtual trigger line across the screen
                cv2.line(frame, (0, TRIGGER_Y_LINE), (640, TRIGGER_Y_LINE), (255, 0, 0), 1)

                # Draw a green dot at the seed's center
                cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

                # ONLY schedule the ejection if the seed's center is crossing the line
                # We use a small 10-pixel window to catch it as it falls past
                if TRIGGER_Y_LINE - 5 < cy < TRIGGER_Y_LINE + 5:
                    compute_latency_ms = (time.time() - start_compute) * 1000.0
                    
                    # Note: Pass the TRIGGER_Y_LINE to the math function instead of y
                    ejection_delay = calculate_ejection_delay(TRIGGER_Y_LINE) - compute_latency_ms
                    
                    valve.schedule_ejection(ejection_delay)
                    # Change box color to yellow to visually confirm the trigger fired
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 3)

        # Show the simulation window and listen for the 'q' quit command
        cv2.imshow("Sorter Simulation", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()