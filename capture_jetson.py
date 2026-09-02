import cv2

class JetsonCamera:
    def __init__(self, capture_width=1280, capture_height=720, framerate=120):
        pipeline = (
            f"nvarguscamerasrc sensor-id=0 exposuretimerange='100000 200000' ! "
            f"video/x-raw(memory:NVMM), width={capture_width}, height={capture_height}, format=NV12, framerate={framerate}/1 ! "
            f"nvvidconv ! video/x-raw, width=640, height=480, format=BGRx ! "
            f"videoconvert ! video/x-raw, format=BGR ! appsink drop=1"
        )
        self.cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
        
        if not self.cap.isOpened():
            raise RuntimeError("Failed to open camera. Check CSI cable and OpenCV GStreamer support.")

    def read(self):
        return self.cap.read()

    def release(self):
        self.cap.release()