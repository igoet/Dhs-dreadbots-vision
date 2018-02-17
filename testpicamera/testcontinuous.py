#!/usr/bin/env python

from __future__ import print_function

import io
import time
import picamera

"""
Demonstates continous image capture technique suggested here:
 - http://www.pyimagesearch.com/2015/03/30/accessing-the-raspberry-pi-camera-with-opencv-and-python/

"""

class Timer(object):
    def __init__(self, name):
        self.name = name
        self.t1 = time.time()
        pass

    def start(self):
        self.t1 = time.time()

    def stop(self):
        self.t2 = time.time()

    def elapsed(self):
        return self.t2-self.t1

    def show(self):
        print( "%s: %4.4f" % ( self.name, (self.t2-self.t1) ) )
#|

t = Timer( "Camera continous" )
idx=0
t.start()
with picamera.PiCamera() as camera:
    stream = io.BytesIO()
    for fooimg in camera.capture_continuous(stream, format='bgr', use_video_port=True):
        stream.truncate()
        stream.seek(0)
        idx=idx+1
        if idx>20:
            break
t.stop()

print( "%s iterations of image captures" % idx )
t.show()


        
