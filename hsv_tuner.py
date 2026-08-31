import os

import cv2
import numpy as np


def nothing(x):
    pass


def main():
    video_source = "finalSeedDemo.mp4" if os.path.exists("finalSeedDemo.mp4") else 0
    cap = cv2.VideoCapture(video_source)

    # Create a window with interactive sliders
    cv2.namedWindow("Trackbars")
    cv2.resizeWindow("Trackbars", 400, 250)

    cv2.createTrackbar("Hue Min", "Trackbars", 0, 179, nothing)
    cv2.createTrackbar("Hue Max", "Trackbars", 179, 179, nothing)
    cv2.createTrackbar("Sat Min", "Trackbars", 0, 255, nothing)
    cv2.createTrackbar("Sat Max", "Trackbars", 255, 255, nothing)
    cv2.createTrackbar("Val Min", "Trackbars", 0, 255, nothing)
    cv2.createTrackbar("Val Max", "Trackbars", 255, 255, nothing)

    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop the video
            continue

        # Resize for easier viewing on laptop screens
        frame = cv2.resize(frame, (640, 480))

        # Convert the BGR image to HSV
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Read the current positions of all sliders
        h_min = cv2.getTrackbarPos("Hue Min", "Trackbars")
        h_max = cv2.getTrackbarPos("Hue Max", "Trackbars")
        s_min = cv2.getTrackbarPos("Sat Min", "Trackbars")
        s_max = cv2.getTrackbarPos("Sat Max", "Trackbars")
        v_min = cv2.getTrackbarPos("Val Min", "Trackbars")
        v_max = cv2.getTrackbarPos("Val Max", "Trackbars")

        # Create a mask using the slider values
        lower_bound = np.array([h_min, s_min, v_min])
        upper_bound = np.array([h_max, s_max, v_max])
        mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)

        # Apply the mask to the original frame
        result = cv2.bitwise_and(frame, frame, mask=mask)

        # Show the windows
        cv2.imshow("Original Feed", frame)
        cv2.imshow("Binary Mask", mask)
        cv2.imshow("Filtered Result", result)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()