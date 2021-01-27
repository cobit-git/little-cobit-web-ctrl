import cv2 
import numpy as np
import time
import os 
from cobit_opencv_lane_detect import CobitOpencvLaneDetect

class CobitOpenCVGetData:
    def __init__(self):
        self.cap = cv2.VideoCapture("data/car_video.avi")
        self.cv_detector = CobitOpencvLaneDetect()
        self.image = None
        self.angle = None
        self.index = 0
        self.jpeg = None

    def update(self):
        ret, self.image = self.cap.read()
        if ret:
            lanes, img_lane = self.cv_detector.get_lane(self.image)
            self.angle, self.img_angle = self.cv_detector.get_steering_angle(img_lane, lanes)
            if self.img_angle is not None:
                cv2.imwrite("%s_%03d_%03d.png" % ("data/img", self.index, self.angle), self.image)  
                self.index += 1  
                ret, self.jpeg = cv2.imencode('.jpg', self.img_angle)
                return True, self.jpeg.tobytes(), self.img_angle
        else:
            return False, None, None

    def remove_old_data(self):
        os.system("rm data/*.png")

    def finish(self):
        self.cap.release()
        cv2.destroyAllWindows()
        
if __name__ == '__main__':
    cam = CobitOpenCVGetData()
    loop = True

    cam.remove_old_data()

    while loop:
        ret, jpeg, img = cam.update()
        if ret:
            cv2.imshow("win", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            loop = False

    cam.finish()


        