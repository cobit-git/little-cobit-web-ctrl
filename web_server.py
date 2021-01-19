from tornado.web import RequestHandler, Application, RedirectHandler, StaticFileHandler
import tornado.websocket
import tornado.ioloop
import json
import os 
import threading
import asyncio
import time 

class DriveAPI(RequestHandler):
    def get(self):
        #data = {}
        self.render("templates/vehicle_main.html")

class WebSocketDriveAPI(tornado.websocket.WebSocketHandler):
    #wsclients = []
    def open(self):
        #self.wsclients.append(self)
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


if __name__=="__main__":
    app = cobit_car_server()
    t = threading.Thread(target=app.run, args=())
    t.daemon = True
    t.start()

    while True:
        time.sleep(1)
        print(app.get_angle())
'''
class cobit_car_server(threading.Thread):
    def __init__(self, port = 8887):
        
        threading.Thread.__init__(self) 
        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.static_file_path = os.path.join(this_dir, 'templates', 'static')

        self.app = Application([
            (r"/", RedirectHandler, dict(url="/drive")),
            (r"/drive", DriveAPI),
            (r"/static/(.*)", StaticFileHandler,
                {"path": self.static_file_path}),
            (r"/wsDrive", WebSocketDriveAPI),
        ])


    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.app.listen(8887)
        tornado.ioloop.IOLoop.current().start()


if __name__=="__main__":
    t = cobit_car_server()
    t.daemon = True
    t.start()

    while True:
        time.sleep(1)
'''