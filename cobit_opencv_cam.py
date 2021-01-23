import cv2
import time
import numpy as np

class CobitOpenCVCam:
    # OpenCV and camera init
    def __init__(self):
        
        self.frame = None
        self.ret = False
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 320)
        self.cap.set(4, 240)
        self.jpeg = None


    # send jpeg image
    def update(self):
        ret, frame = self.cap.read()
        if ret  == False:
            frame_ = np.zeros((240, 320, 3), np.uint8)
            cv2.putText(image, 'No camera', (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

if __name__ == '__main__':
    cam = CobitOpenCVCam()
    cam.update() 

