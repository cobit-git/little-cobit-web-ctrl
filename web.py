#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 24 20:10:44 2017
@author: wroscoe
remotes.py
The client and web server needed to control a car remotely.
"""


import os
import json
import time
import asyncio

import cv2

import requests
from tornado.ioloop import IOLoop
from tornado.web import Application, RedirectHandler, StaticFileHandler, \
    RequestHandler
from tornado.httpserver import HTTPServer
import tornado.gen
import tornado.websocket
from socket import gethostname
import threading 

# Conner
from adafruit_servokit import ServoKit
from cobit_car_motor_l9110 import CobitCarMotorL9110
from cobit_opencv_cam import CobitOpenCVCam

#from ... import utils

frame = None

class LocalWebController(tornado.web.Application):

    def __init__(self, port=8887, mode='user'):
        '''
        Create and publish variables needed on many of
        the web handlers.
        '''

        print('Starting Donkey Server...', end='')

        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.static_file_path = os.path.join(this_dir, 'templates', 'static')
        self.angle = 0.0
        self.throttle = 0.0
        self.mode = mode
        self.recording = False
        self.port = port

        self.num_records = 0
        self.wsclients = []
        self.loop = None


        handlers = [
            (r"/", RedirectHandler, dict(url="/drive")),
            (r"/drive", DriveAPI),
            (r"/wsDrive", WebSocketDriveAPI),
            (r"/wsCalibrate", WebSocketCalibrateAPI),
            (r"/calibrate", CalibrateHandler),
            (r"/video", VideoAPI),
            (r"/wsTest", WsTest),

            (r"/static/(.*)", StaticFileHandler,
             {"path": self.static_file_path}),
        ]

        settings = {'debug': True}
        super().__init__(handlers, **settings)
        print("... you can now go to {}.local:{} to drive "
              "your car.".format(gethostname(), port))

    def update(self):
        ''' Start the tornado webserver. '''
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.listen(self.port)
        self.loop = IOLoop.instance()
        self.loop.start()

    def update_wsclients(self):
        for wsclient in self.wsclients:
            try:
                data = {
                    'num_records': self.num_records
                }
                data_str = json.dumps(data)
                wsclient.write_message(data_str)
            except Exception as e:
                print(e)
                pass

    def run_threaded(self, img_arr=None, num_records=0):
        self.img_arr = img_arr
        self.num_records = num_records

        # Send record count to websocket clients
        if (self.num_records is not None and self.recording is True):
            if self.num_records % 10 == 0:
                if self.loop is not None:
                    self.loop.add_callback(self.update_wsclients)
        # Conner 
        print(self.throttle)
        if self.throttle > 0:
            self.motor.motor_all_start(int(self.throttle*100))
        else:
            self.motor.motor_all_start(0)
        angle_x = self.angle*100 + 90
        #print(angle_x)
        if angle_x > 30 and angle_x < 150:
            self.servo.servo[0].angle = angle_x
        return self.angle, self.throttle, self.mode, self.recording
        
    def run(self, img_arr=None):
        self.img_arr = img_arr
        return self.angle, self.throttle, self.mode, self.recording

    def shutdown(self):
        pass

    # Conner
    def motor_init(self):
        self.motor = CobitCarMotorL9110()
        self.servo = ServoKit(channels=16)

    # Conner
    def motor_stop(self):
        self.motor.motor_all_stop()
        self.servo.servo[0].angle = 90


class DriveAPI(RequestHandler):

    def get(self):
        data = {}
        self.render("templates/vehicle.html", **data)

    def post(self):
        '''
        Receive post requests as user changes the angle
        and throttle of the vehicle on a the index webpage
        '''
        data = tornado.escape.json_decode(self.request.body)
        self.application.angle = data['angle']
        self.application.throttle = data['throttle']
        self.application.mode = data['drive_mode']
        self.application.recording = data['recording']


class WsTest(RequestHandler):
    def get(self):
        data = {}
        self.render("templates/wsTest.html", **data)


class CalibrateHandler(RequestHandler):
    """ Serves the calibration web page"""
    async def get(self):
        await self.render("templates/calibrate.html")


class WebSocketDriveAPI(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("New client connected")
        self.application.wsclients.append(self)

    def on_message(self, message):
        data = json.loads(message)

        self.application.angle = data['angle']
        self.application.throttle = data['throttle']
        self.application.mode = data['drive_mode']
        self.application.recording = data['recording']

    def on_close(self):
        # print("Client disconnected")
        self.application.wsclients.remove(self)


class WebSocketCalibrateAPI(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("New client connected")

    def on_message(self, message):
        print(f"wsCalibrate {message}")
        data = json.loads(message)
        if 'throttle' in data:
            print(data['throttle'])
            self.application.throttle = data['throttle']

        if 'angle' in data:
            print(data['angle'])
            self.application.angle = data['angle']

        if 'config' in data:
            config = data['config']
            if self.application.drive_train_type == "SERVO_ESC":
                if 'STEERING_LEFT_PWM' in config:
                    self.application.drive_train['steering'].left_pulse = config['STEERING_LEFT_PWM']

                if 'STEERING_RIGHT_PWM' in config:
                    self.application.drive_train['steering'].right_pulse = config['STEERING_RIGHT_PWM']

                if 'THROTTLE_FORWARD_PWM' in config:
                    self.application.drive_train['throttle'].max_pulse = config['THROTTLE_FORWARD_PWM']

                if 'THROTTLE_STOPPED_PWM' in config:
                    self.application.drive_train['throttle'].zero_pulse = config['THROTTLE_STOPPED_PWM']

                if 'THROTTLE_REVERSE_PWM' in config:
                    self.application.drive_train['throttle'].min_pulse = config['THROTTLE_REVERSE_PWM']

            elif self.application.drive_train_type == "MM1":
                if ('MM1_STEERING_MID' in config) and (config['MM1_STEERING_MID'] != 0):
                        self.application.drive_train.STEERING_MID = config['MM1_STEERING_MID']
                if ('MM1_MAX_FORWARD' in config) and (config['MM1_MAX_FORWARD'] != 0):
                        self.application.drive_train.MAX_FORWARD = config['MM1_MAX_FORWARD']
                if ('MM1_MAX_REVERSE' in config) and (config['MM1_MAX_REVERSE'] != 0):
                    self.application.drive_train.MAX_REVERSE = config['MM1_MAX_REVERSE']

    def on_close(self):
        print("Client disconnected")


class VideoAPI(RequestHandler):
    '''
    Serves a MJPEG of the images posted from the vehicle.
    '''
    async def get(self):

        cam = CobitOpenCVCam()
        c =  threading.Thread(target=cam.update, args=())
        c.start()

        self.set_header("Content-type",
                        "multipart/x-mixed-replace;boundary=--boundarydonotcross")

        served_image_timestamp = time.time()
        my_boundary = "--boundarydonotcross\n"
        while True:

            interval = .01
            #if served_image_timestamp + interval < time.time(): #and 
                #    hasattr(self.application, 'img_arr'):

                #img = utils.arr_to_binary(self.application.img_arr)
            
            self.jpeg = cam.run_threaded()
            if self.jpeg is not None:
                self.write(my_boundary)
                self.write("Content-type: image/jpeg\r\n")
                self.write("Content-length: %s\r\n\r\n" % len(self.jpeg))
                self.write(self.jpeg)
                #served_image_timestamp = time.time()
                try:
                    await self.flush()
                except tornado.iostream.StreamClosedError:
                    pass
            else:
                await tornado.gen.sleep(interval)


class BaseHandler(RequestHandler):
    """ Serves the FPV web page"""
    async def get(self):
        data = {}
        await self.render("templates/base_fpv.html", **data)


class WebFpv(Application):
    """
    Class for running an FPV web server that only shows the camera in real-time.
    The web page contains the camera view and auto-adjusts to the web browser
    window size. Conjecture: this picture up-scaling is performed by the
    client OS using graphics acceleration. Hence a web browser on the PC is
    faster than a pure python application based on open cv or similar.
    """

    def __init__(self, port=8890):
        self.port = port
        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.static_file_path = os.path.join(this_dir, 'templates', 'static')

        """Construct and serve the tornado application."""
        handlers = [
            (r"/", BaseHandler),
            (r"/video", VideoAPI),
            (r"/static/(.*)", StaticFileHandler,
             {"path": self.static_file_path})
        ]

        settings = {'debug': True}
        super().__init__(handlers, **settings)
        print("Started Web FPV server. You can now go to {}.local:{} to "
              "view the car camera".format(gethostname(), self.port))

    def update(self):
        """ Start the tornado webserver. """
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.listen(self.port)
        IOLoop.instance().start()

    def run_threaded(self, img_arr=None):
        self.img_arr = img_arr

    def run(self, img_arr=None):
        self.img_arr = img_arr

    def shutdown(self):
        pass


if __name__=='__main__':
    app = LocalWebController()
    #cam = CobitOpenCVCam()
    t =  threading.Thread(target=app.update, args=())
    #c =  threading.Thread(target=cam.update, args=())
    t.daemon = True
    t.start()
    #c.start()

    app.motor_init()

    while True:
        app.run_threaded()
        #cam.run_threaded()
        #if frame is not None:
        #    cv2.imshow('my_win', frame)
        #    if cv2.waitKey(1) & 0xff == ord('q'):
        #        break
            
        #self.cap.release()
        #cv2.destroyAllWindows()

    #app.motor_stop()



