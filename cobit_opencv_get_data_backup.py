import cv2 
import numpy as np
import time
import os 
from cobit_opencv_lane_detect import CobitOpencvLaneDetect

class CobitOpenCVGetData:
    def __init__(self):
        self.cap = cv2.VideoCapture('data/car_video.avi')
        self.cv_detector = CobitOpencvLaneDetect()
        self.image = None
        self.angle = None
        self.index = 0
        self.jpeg = None

    def update(self):
        ret, self.image = self.cap.read()
        ret, self.jpeg = cv2.imencode('.jpg', self.image)
        return ret, self.jpeg.tobytes()
        '''
        if ret is False: 
            self.image = np.zeros((240, 320, 3), np.uint8)
            cv2.putText(self.image, 'No frame', (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1)
            ret, self.jpeg = cv2.imencode('.jpg', self.image)
            return ret, self.jpeg.tobytes()
        else:
            self.image = np.zeros((240, 320, 3), np.uint8)
            ret, self.jpeg = cv2.imencode('.jpg', self.image)
            return ret, self.jpeg.tobytes()
        '''

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
        ret, img = cam.update()
        print(ret)
        if ret:
            cv2.imshow("win", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cam.finish()


        