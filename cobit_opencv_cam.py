import cv2

class CobitOpenCVCam:
    # OpenCV and camera init
    def __init__(self):
        self.frame = None
        self.ret = False
        self.cap = cv2.VideoCapture(0)
        self.cap(3, 320)
        self.cap(4, 240)

    # return captured image (not using thread)
    def run(self):
        return self.frame

    # return captured image (using thread)
    def run_threaded(self):
        return self.frame

    # Video capture thread 
    def update(self):
        self.ret, self.frame = cap.read()

    # shutdonw camera 
    def shutdonw(self):
