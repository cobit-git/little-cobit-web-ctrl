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

cam = None

class DriveAPI(RequestHandler):
    def get(self):
        self.render("templates/vehicle_teleop.html")

class LaneAPI(RequestHandler):
    def get(self):
        print("LaneAPI")
        self.render("templates/lane_detect.html")


class LaneButtonAPI(RequestHandler):
    async def post(self):
        print(self.request.body)
        # get args from POST request
        move = self.get_argument('move')
        recording = self.get_argument('recording')
        if move == "forward":
            print("go")
            cam.set_lane_detect(True)
            vc.throttle_control(20)
        else: 
            print("stop")
            cam.set_lane_detect(False)
            vc.throttle_control(0)
        if recording == 'on':
            print("recoridng on")
            
        else:
            print("recording off")

class VideoAPI(RequestHandler):
    #rves a MJPEG of the images posted from the vehicle.
    async def get(self):
        print("VideoAPI")
        self.set_header("Content-type",
                        "multipart/x-mixed-replace;boundary=--boundarydonotcross")
        served_image_timestamp = time.time()
        my_boundary = "--boundarydonotcross\n"
        while True:

            interval = .01
            if served_image_timestamp + interval < time.time():
                angle, img = cam.update()
                vc.servo_control(angle)
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

class WebSocketDriveAPI(tornado.websocket.WebSocketHandler):
    def open(self):
        print("New client connected")

    def on_message(self, message):
        data = json.loads(message)
        self.application.angle = data['angle']
        self.application.throttle = data['throttle']
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

        handlers = [
            (r"/", RedirectHandler, dict(url="/drive")),
            (r"/drive", DriveAPI),
            (r"/video", VideoAPI),
            (r"/static/(.*)", StaticFileHandler,
                {"path": self.static_file_path}),
            (r"/wsDrive", WebSocketDriveAPI),
            (r"/lane", LaneAPI),
            (r"/setparams", LaneButtonAPI),
        ]

        settings = {'debug': True}
        super().__init__(handlers, **settings)


    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.listen(8887)
        tornado.ioloop.IOLoop.current().start()

    def get_angle(self):
        return self.angle

    def get_throttle(self):
        return self.throttle

class vehicle_control:
    def __init__(self):
        self.motor = CobitCarMotorL9110()
        self.servo = ServoKit(channels=16)

    def motor_control(self, angle, throttle):
        if throttle > 0.1:
            self.motor.motor_move_forward(int(throttle*100))
        elif throttle <= 0.1 and throttle >= -0.1:
            self.motor.motor_stop()
        else:
            self.motor.motor_move_backward(-1*(int(throttle*100)))
            
        angle_x = angle*100 + 90
        if angle_x > 30 and angle_x < 150:
            self.servo.servo[0].angle = angle_x

    def servo_control(self, angle):
        if angle > 30 and angle < 150:
            self.servo.servo[0].angle = angle

    def throttle_control(self, throttle):
        print("test-e")
        self.motor.motor_move_forward(throttle)


if __name__=="__main__":
    app = cobit_car_server()
    t = threading.Thread(target=app.run, args=())
    t.daemon = True
    t.start()
    cam = CobitOpenCVCam()

    vc = vehicle_control()

    while True:
        time.sleep(0.1)
        #vc.motor_control(app.get_angle(),app.get_throttle())
s