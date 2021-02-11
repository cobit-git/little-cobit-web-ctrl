from tornado.web import RequestHandler, Application, RedirectHandler, StaticFileHandler
import tornado.websocket
import tornado.ioloop
import json
import os 
import threading
import asyncio
import time 

import utils

from adafruit_servokit import ServoKit
from cobit_car_motor_l9110 import CobitCarMotorL9110
from cobit_opencv_cam import CobitOpenCVCam
from cobit_opencv_get_data import CobitOpenCVGetData

cam = None

CONST_DRIVE = 1 
CONST_LANE = 2 


class DriveAPI(RequestHandler):
    def get(self):
        print("drive API")
        self.render("templates/vehicle_teleop.html")
        cam.set_lane_detect(False)
        app.set_status(CONST_DRIVE)

class LaneAPI(RequestHandler):
    def get(self):
        print("Lane API")
        self.render("templates/lane_detect.html")
        app.set_status(CONST_LANE)

class LabelAPI(RequestHandler):
    def get(self):
        print("LabelAPI")
        self.render("templates/get_data.html")
        

class LaneButtonAPI(RequestHandler):
    async def post(self):
        print(self.request.body)
        # get args from POST request
        move = self.get_argument('move')
        recording = self.get_argument('recording')
        if move == "forward":
            cam.set_lane_detect(True)
        else: 
            cam.set_lane_detect(False)
        if recording == 'on':
            print("rrrr on")
            cam.set_recording_status(True) 
        else:
            print("rrrr off ")
            cam.set_recording_status(False)

class LabelButtonAPI(RequestHandler):
    async def post(self):
        print(self.request.body)
        # get args from POST request
        act = self.get_argument('action')
        if act == "start":
            print("labeling start")
            label_cam.remove_old_data()
            label_cam.make_label()
        elif act == "cancel":
            print("labeling cancel")
        elif act == "download":
            print("zip and download")
        

class VideoAPI(RequestHandler):
    #rves a MJPEG of the images posted from the vehicle.
    async def get(self):
        self.set_header("Content-type",
                        "multipart/x-mixed-replace;boundary=--boundarydonotcross")
        served_image_timestamp = time.time()
        my_boundary = "--boundarydonotcross\n"
        while True:
            interval = .01
            if served_image_timestamp + interval < time.time():
                angle, img = cam.update()
                self.write(my_boundary)
                self.write("Content-type: image/jpeg\r\n")
                self.write("Content-length: %s\r\n\r\n" % len(img))
                self.write(img)
                served_image_timestamp = time.time()
                try:
                    await self.flush()
                except tornado.iostream.StreamClosedError:
                    pass
               
            else:
                await tornado.gen.sleep(interval)

class VideoCVAPI(RequestHandler):
    #rves a MJPEG of the images posted from the vehicle.
    async def get(self):
        self.set_header("Content-type",
                        "multipart/x-mixed-replace;boundary=--boundarydonotcross")
        served_image_timestamp = time.time()
        my_boundary = "--boundarydonotcross\n"
        while True:
            interval = .01
            if served_image_timestamp + interval < time.time():
                angle, img = cam.update()
                if app.get_status() is CONST_LANE:
                    app.set_angle(angle)
                self.write(my_boundary)
                self.write("Content-type: image/jpeg\r\n")
                self.write("Content-length: %s\r\n\r\n" % len(img))
                self.write(img)
                served_image_timestamp = time.time()
                try:
                    await self.flush()
                except tornado.iostream.StreamClosedError:
                    pass
               
            else:
                await tornado.gen.sleep(interval)

class LabelVideoAPI(RequestHandler):
    #rves a MJPEG of the images posted from the vehicle.
    async def get(self):
        loop = True
        self.set_header("Content-type",
                        "multipart/x-mixed-replace;boundary=--boundarydonotcross")
        served_image_timestamp = time.time()
        my_boundary = "--boundarydonotcross\n"
        while loop:

            interval = .01
            if served_image_timestamp + interval < time.time():
                ret, jpeg = label_cam.update()
                if ret:
                    self.write(my_boundary)
                    self.write("Content-type: image/jpeg\r\n")
                    self.write("Content-length: %s\r\n\r\n" % len(jpeg))
                    self.write(jpeg)
                    served_image_timestamp = time.time()
                    try:
                        await self.flush()
                    except tornado.iostream.StreamClosedError:
                        pass
               
            else:
                await tornado.gen.sleep(interval)

class GetDataAPI(RequestHandler):
    async def get(self):
        print("GetDataAPI")


class WebSocketDriveAPI(tornado.websocket.WebSocketHandler):
    def open(self):
        print("New client connected")

    def on_message(self, message):
        data = json.loads(message)
        self.application.angle = float(data['angle']) * 100 + 90
        self.application.throttle = float(data['throttle']) * 100 
        self.application.mode = data['drive_mode']
        self.application.recording = data['recording']


    def on_close(self):
        print("Client disconnected")


class cobit_car_server(tornado.web.Application):

    def __init__(self, port = 8887):
        
        self.angle = 0.0
        self.throttle = 0.0
        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.static_file_path = os.path.join(this_dir, 'templates', 'static')
        self.status = CONST_DRIVE

        handlers = [
            (r"/", RedirectHandler, dict(url="/drive")),
            (r"/drive", DriveAPI),
            (r"/video", VideoAPI),
            (r"/video_cv", VideoCVAPI),
            (r"/static/(.*)", StaticFileHandler,
                {"path": self.static_file_path}),
            (r"/wsDrive", WebSocketDriveAPI),
            (r"/lane", LaneAPI),
            (r"/setparams", LaneButtonAPI),
            (r"/label", LabelAPI),
            (r"/label_cmd", LabelButtonAPI),
            #(r"/label_video", LabelVideoAPI), For using video div, uncommnet it.
        ]

        settings = {'debug': True}
        super().__init__(handlers, **settings)

    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.listen(8887)
        tornado.ioloop.IOLoop.current().start()

    def get_angle(self):
        return self.angle

    def set_angle(self, angle):
        self.angle = angle
        

    def get_throttle(self):
        return self.throttle

    def set_status(self, status):
        self.status = status
        
    def get_status(self):
        return self.status 
        
class vehicle_control:

    def __init__(self):
        self.motor = CobitCarMotorL9110()
        self.servo = ServoKit(channels=16)

    def motor_control(self, angle, throttle):
        if throttle >= 0 and throttle <= 100:
            self.motor.motor_move_forward(int(throttle))
        if angle >= 0 and angle <= 180:
            self.servo.servo[0].angle = angle

    def servo_control(self, angle):
        if angle > 30 and angle < 150:
            self.servo.servo[0].angle = angle

    def throttle_control(self, throttle):
        self.motor.motor_move_forward(throttle)

if __name__=="__main__":
    app = cobit_car_server()
    t = threading.Thread(target=app.run, args=())
    t.daemon = True
    t.start()
    cam = CobitOpenCVCam()
    label_cam = CobitOpenCVGetData()
    vc = vehicle_control()

    while True:
        time.sleep(0.1)
        status = app.get_status()
        if status is CONST_DRIVE:
            angle = app.get_angle()
            throttle = app.get_throttle()
            vc.motor_control(angle,throttle)
        elif status is CONST_LANE:
            if cam.get_lane_detect() is True:
                vc.motor_control(app.get_angle(),30)
            else:
                vc.motor_control(90,0)

            
