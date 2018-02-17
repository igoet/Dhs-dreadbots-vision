#!/usr/bin/env python3

from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.start_preview()
sleep(10)
camera.stop_preview()

for idx in range(0,10):
    fname='image-%s.jpg' % idx
    camera.capture(fname)
    print( "wrote: %s" % fname )
    sleep(2)
    



  
