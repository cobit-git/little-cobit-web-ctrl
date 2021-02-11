import cv2 
import numpy as np
import time
import os 
from cobit_opencv_lane_detect import CobitOpencvLaneDetect

class CobitOpenCVGetData:
    def __init__(self):
        self.cap = cv2.VideoCapture('./data/car_video.avi')
        self.cv_detector = CobitOpencvLaneDetect()
        self.image = None
        self.index = 0

    def make_label(self):
        while True:
            ret, self.image = self.cap.read()
            if ret:
                lanes, img_lane = self.cv_detector.get_lane(self.image)
                #cv2.imshow("ddd", self.image)
                angle, img_angle = self.cv_detector.get_steering_angle(img_lane, lanes)
                if img_angle is None:
                    print("ssibal")
                    pass
                else:
                    cv2.imwrite("%s_%03d_%03d.png" % ("./data/video_label", self.index, angle), self.image)
                    self.index += 1	
                #if cv2.waitKey(1) & 0xFF == ord('q'):
                #    break
            else:
                print("cap error")
                break
        self.index = 0
        #cv2.destroyAllWindows()
        self.cap.release()

    def remove_old_data(self):
        os.system("rm data/*.png")

    def finish(self):
        self.cap.release()
        cv2.destroyAllWindows()
        
if __name__ == '__main__':
    cam = CobitOpenCVGetData()
    loop = True

    cam.remove_old_data()
    cam.make_label()

        