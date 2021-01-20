from tornado.web import RequestHandler, Application, RedirectHandler, StaticFileHandler
import tornado.websocket
import tornado.ioloop
import json
import os 
import threading
import asyncio
import time 

from adafruit_servokit import ServoKit
from cobit_car_motor_l9110 import CobitCarMotorL9110

class DriveAPI(RequestHandler):
    def get(self):
        self.render("templates/vehicle_main.html")

class WebSocketDriveAPI(tornado.websocket.WebSocketHandler):
    def open(self):
        print("New client connected")

    def on_message(self, message):
        data = json.loads(message)
        self.application.angle = data['angle']
        self.application.throttle = data['throttle']
        self.application.mode = data['drive_mode']
        self.application.recording = data['recording']


class cobit_car_server(tornado.web.Application):
    def __init__(self, port = 8887):
        
        self.angle = 0.0
        self.throttle = 0.0
        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.static_file_path = os.path.join(this_dir, 'templates', 'static')

        handlers = [
            (r"/", RedirectHandler, dict(url="/drive")),
            (r"/drive", DriveAPI),
            (r"/static/(.*)", StaticFileHandler,
                {"path": self.static_file_path}),
            (r"/wsDrive", WebSocketDriveAPI),
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
        if throttle > 0:
            self.motor.motor_all_start(int(throttle*100))
        else:
            self.motor.motor_all_start(0)
        angle_x = angle*100 + 90
        if angle_x > 30 and angle_x < 150:
            self.servo.servo[0].angle = angle_x



if __name__=="__main__":
    app = cobit_car_server()
    t = threading.Thread(target=app.run, args=())
    t.daemon = True
    t.start()

    vc = vehicle_control()

    while True:
        time.sleep(0.1)
        vc.motor_control(app.get_angle(),app.get_throttle())
