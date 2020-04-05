import json
from gpiozero import LED, Button
import picamera
import cv2
import io
import picamera
import logging
import socketserver
from os import curdir, sep
from threading import Condition
from http import server
from urllib.parse import urlparse
from urllib.parse import parse_qs
import threading
import time

led = LED(17)
button = Button(21, pull_up=True)

light_state = False
safety_state = "open"

def is_safe():
    global safety_state
    if button.is_pressed:
        safety_state = ""
        return True
    else:
        safety_state = "open"
        return False

def turn_off():
    global light_state
    led.off()
    light_state = False
    return report_state()

def monitor_state():
    print("Monitoring...");
    while(True):
        if not is_safe():
            turn_off()
        time.sleep(.3);

t0 = threading.Thread(target=monitor_state, args=());
t0.start();

def report_state():
    return json.dumps({'ison': light_state, 'safety_state': safety_state})

on_thread = None
def timed_turn_off(duration):
    try:
        time_per_loop = .2
        while(duration > 0):
            time.sleep(time_per_loop)
            duration = duration - time_per_loop
        turn_off()
    except:
        print("Cancelled timer.")

def turn_on(duration):
    global light_state, on_thread
    if is_safe():
        light_state = True
        led.on()
        if (on_thread != None):
            on_thread.raise_exception()
        on_thread = threading.Thread(target=timed_turn_off, args=(duration));
        on_thread.start();
    else:
        light_state = False
        led.off()
    return report_state()

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            # Extract query param
            name = 'World'
            query_components = parse_qs(urlparse(self.path).query)
            if 'name' in query_components:
                name = query_components["name"][0]

            f = open(curdir + sep + self.path, 'rb')
            self.wfile.write(f.read())
            f.close()
        elif self.path == '/code.js':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            # Extract query param
            name = 'World'
            query_components = parse_qs(urlparse(self.path).query)
            if 'name' in query_components:
                name = query_components["name"][0]

            f = open(curdir + sep + self.path, 'rb')
            self.wfile.write(f.read())
            f.close()
        elif self.path == '/on':
            self.send_response(200)
            self.send_header('Content-Type', 'text/javascript')
            self.end_headers()

            # Extract query param
            duration = '15'
            query_components = parse_qs(urlparse(self.path).query)
            if 'duration' in query_components:
                duration = query_components["duration"][0]

            self.wfile.write(turn_on(duration).encode())
        elif self.path == '/off':
            self.send_response(200)
            self.send_header('Content-Type', 'text/javascript')
            self.end_headers()
            self.wfile.write(turn_off().encode())
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'text/javascript')
            self.end_headers()
            self.wfile.write(report_state().encode())
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()

