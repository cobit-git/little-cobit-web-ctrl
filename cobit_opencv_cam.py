import cv2
import time

class CobitOpenCVCam:
    # OpenCV and camera init
    def __init__(self):
        
        self.frame = None
        self.ret = False
        self.cap = cv2.VideoCapture(0)
        self.cap.release()
        time.sleep(1)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 320)
        self.cap.set(4, 240)
        self.jpeg = None

    # return captured image (not using thread)
    def run(self):
        #return self.frame
         if self.jpeg is not None:
            return self.jpeg.tobytes()


    # return captured image (using thread)
    def run_threaded(self):
        #return self.frame
        if self.jpeg is not None:
            return self.jpeg.tobytes()

    # Video capture thread q
    def update(self):
        #self.ret, self.frame = self.cap.read()
        while (self.cap.isOpened()):
            self.ret, self.frame = self.cap.read()
            self.ret, self.jpeg = cv2.imencode('.jpg', self.frame)
            #cv2.imshow('my_win', img)
            #if cv2.waitKey(1) & 0xff == ord('q'):
            #    break
            
        self.cap.release()
        cv2.destroyAllWindows()

    # shutdonw camera 
    #def shutdonw(self):
