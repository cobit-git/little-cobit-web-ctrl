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
        self.recording = False
        self.cv_detector = CobitOpencvLaneDetect()
        fourcc =  cv2.VideoWriter_fourcc('M','J','P','G')
        self.video_orig = cv2.VideoWriter('./data/car_video.avi', fourcc, 20.0, (320, 240))

    def get_jpeg(self):
        return self.jpeg.tobytes()

    # send jpeg image
    def update(self):
        ret, self.frame = self.cap.read()
        if self.lane_detect is False:
            if ret  == False:
                self.frame_ = np.zeros((240, 320, 3), np.uint8)
                cv2.putText(self.frame, 'No camera', (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1)
            ret, self.jpeg = cv2.imencode('.jpg', self.frame)
            angle_tmp = 90
            return angle_tmp, self.jpeg.tobytes()
        elif self.lane_detect is True:
            if self.recording is True:
                print("recording")
                self.video_orig.write(self.frame)
            lanes, frame_lane = self.cv_detector.get_lane(self.frame)
            angle, frame_angle = self.cv_detector.get_steering_angle(frame_lane, lanes)
            if ret == False or frame_angle is None:
                frame_angle = np.zeros((240, 320, 3), np.uint8)
                cv2.putText(frame_angle, 'No frame', (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1)
            ret, self.jpeg = cv2.imencode('.jpg', frame_angle)
            return angle, self.jpeg.tobytes()

    def set_lane_detect(self, value):
        self.lane_detect = value

    def get_lane_detect(self):
        return self.lane_detect

    def set_recording_status(self, value):
        print(value)
        self.recording = value

    def get_recording_status(self):
        return self.recording


if __name__ == '__main__':
    cam = CobitOpenCVCam()
    cam.update() 

