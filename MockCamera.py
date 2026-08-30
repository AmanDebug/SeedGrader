# camera/capture_mock.py
import cv2

class MockCamera:
    def __init__(self, source=0): # 0 for webcam or "path/to/test_video.mp4"
        self.cap = cv2.VideoCapture(source)

    def read(self):
        ret, frame = self.cap.read()
        if not ret and isinstance(self.cap, cv2.VideoCapture):
            # Loop the test video continuously
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
        return ret, frame

    def release(self):
        self.cap.release()