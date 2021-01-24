import cv2
import time
import numpy as np
from cobit_opencv_lane_detect import CobitOpencvLaneDetect

class CobitOpenCVCam:
    # OpenCV and camera init
    def __init__(self):
        
        self.frame = None
        self.ret = False
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 320)
        self.cap.set(4, 240)
        self.jpeg = None
        self.lane_detect = False
        self.cv_detector = CobitOpencvLaneDetect()

    def get_jpeg(self):
        return self.jpeg.tobytes()

    # send jpeg image
    def update(self):
        ret, frame_org = self.cap.read()
        self.frame = cv2.flip(frame_org, 0)
        if self.lane_detect is False:
            if ret  == False:
                self.frame_ = np.zeros((240, 320, 3), np.uint8)
                cv2.putText(self.frame, 'No camera', (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1)
            ret, self.jpeg = cv2.imencode('.jpg', self.frame)
            return self.jpeg.tobytes()
        elif self.lane_detect is True:
            lanes, frame_lane = self.cv_detector.get_lane(self.frame)
            angle, frame_angle = self.cv_detector.get_steering_angle(frame_lane, lanes)
            if ret == False or frame_angle is None:
                frame_angle = np.zeros((240, 320, 3), np.uint8)
                cv2.putText(frame_angle, 'No frame', (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1)
            ret, self.jpeg = cv2.imencode('.jpg', frame_angle)
            return self.jpeg.tobytes()

    def set_lane_detect(self, value):
        self.lane_detect = value

    def get_lane_detect(self):
        return self.lane_detect

if __name__ == '__main__':
    cam = CobitOpenCVCam()
    cam.update() 

