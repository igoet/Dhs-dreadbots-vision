#!/usr/bin/env python

from __future__ import print_function

import argparse
import time

"""
Dreadbot sensor processor loop. 

Runs continuously.
Monitors PI camera.
Detects yellowbox target blobs.
Communicates back to the roborio via NetworkTables.

TODO: Ask the drive team programmers to notify us when we are in auton mode. 
Set /SmartDashboard/yellowbox_mode = "on" when auton starts
Set /SmartDashboard/yellowbox_mode = "off" when auton stops

Doing this will put the pi into continous image capture mode, so we can save the pictures off for later
analysis and possible training.
"""

import io
import os
import os.path

import cv2
import numpy
import math
import time
import datetime
from enum import Enum
from threadpool import ThreadPool

userhome = os.path.expanduser( "~" )
exec(open(os.path.join( userhome, "dreadbots_config.py")).read())

debug = False
pool = ThreadPool(5)

def secofday(dt):
    """Given a datetime object return the number of seconds of the day that datetime occurs."""

    return dt.hour*3600 + dt.minute*60 + dt.second

def saveImageTask(parms):
    """Helper method for saving an image from the camera. Callable from a thread in a threadpool."""

    rawimage = parms.get( "rawimage" )
    annotated = parms.get( "annotated" )
    imgdir = parms.get( "imgdir" )

    if not(imgdir):
        now = datetime.datetime.now()
        seconds = secofday( now )
        imgdir = os.path.join( imagedir, "%s" % now.year, "%02d" % now.month, "%02d" % now.day, "%s" % seconds )

    if not(os.path.exists( imgdir ) ):
        os.makedirs( imgdir )

    rawfile = os.path.join( imgdir, "raw.jpg" )
    annotatedfile = os.path.join( imgdir, "annotated.jpg" )

    cv2.imwrite( rawfile, rawimage )
    cv2.imwrite( annotatedfile, annotated )

    if debug:
        print( "images written to %s" % imgdir )
    

class Contour(object):
    """Model for representing a contour found by opencv. Facilitates making the data slightly easier to send to the network tables."""
    def __init__(self, numpyNdarray ):
        self.area = None
        self.cx = None
        self.cy = None
        self.array = numpyNdarray
        self.br = cv2.boundingRect( self.array )
        (brx, bry, brw, brh) = self.br
        self.area =  brh * brw
        self.cx = brx + brw / 2
        self.cy = bry + brh / 2

    def __repr__(self):
        c = self
        print( "  contour cx=%s cy=%s, area=%s" % (c.cx, c.cy, c.area) )

        

class Timer(object):
    """Timer object. Useful for keeping tabs on the performance of the code."""
    
    def __init__(self, name):
        self.name = name
        self.t1 = time.time()
        self.t2 = None
        pass

    def start(self):
        self.t1 = time.time()

    def stop(self):
        self.t2 = time.time()

    def show(self):
        print( "%s: %4.4f" % ( self.name, (self.t2-self.t1) ) )
#|        


class DreadbotSensor(object):

    def __init__(self, sensor, pipeline, debug=False, lowexposuremode=False, logfails=False, nocamera=False):
        """@parms sensor = name of the sensor
           @parms pipeline = instance of a grip pipeline
           @parms debug    = run the sensor in debug mode, showing object detected in images.
           @parms logfails = If we detect things in one image, log subsequent cycles where the objects disappear.
        @parms nocamera = Allow the sensor code to run without camera input. It will fetch an image from /var/tmp/images/currentImage/raw.jpg and perform object detection on that.
        """
        self.blobsupport = False  # Use the pipeline's blob detection.
        self.updateCurrentImageInterval = 1.0 # number of seconds to encode a new jpg image for the web interface / GUI.
        self.imagedir = imagedir # "images/" take the value from dreadbots_config.py now.
        self.pipeline = pipeline
        self.camera = None
        self.nocamera = nocamera
        self.lowexposuremode = lowexposuremode
        self.nt3656 = None
        self.initNetTables()
        
        try:
            # Allow execution of code on non-pi linux hardware
            import picamera
            
            self.camera = picamera.PiCamera()
            self.camera.resolution = (400, 304)
            self.initCamera()
        except:
            if not(self.nocamera):
                raise
                
        #self.sd = NetworkTables.getTable('SmartDashboard')

        self.lastannotated = None
        self.lastraw = None
        self.targets = {
            "blobs": [],
            "contours": []
            }
        
        self.debug = debug
        self.logfails = logfails
        self.rawCapture = None

        self.realtargets = {}
        self.realblobcounter = 0

        self.minrad = 18.0
        self.minarea = math.pi * self.minrad * self.minrad

        # Info in the protocol to send back
        self.name = sensor
        self.suggest_no = 0
        self.active = False
        self.lastsave = None

        """ target_zone: A filter band of where we expect the blobs to 
              appear in the image expressed in a percentage.
              0.25 indicates we expect the target blobs to appear in the
              quarter above and below the center of the image. """
        self.target_zone = (0.05, 0.95)  #just use lowest half of image
        if self.name == "gear":
            self.target_zone = (0.5, 1.0)  #just use lowest half of image
            
        if self.name == "highgoal":
            self.target_zone = (0.0,1.0) # accept contours in the entire image for the high goal

        if self.camera and not(self.lowexposuremode):
            #self.camera.brightness = int( self.nt3656.vis_cam_brightness )
            pass
        self.estimatedDistance = -1
        self.focalLength = 328.0 # measured in pixels
        self.yellowbox_mode = self.name == "yellowbox"
        self.goal_mode = self.name == "highgoal"
        

    def initCamera(self):
        """Logic to initialize the camera should be set here. Note the brightness is set in the main processing loop should it be
          adjusted via nettables."""

        # Info about these settings can be found here.
        # http://picamera.readthedocs.io/en/release-1.10/api_camera.html
        if self.camera:
            if self.lowexposuremode:
                self.camera.resolution = (400,304)
                self.camera.framerate = 32
                self.camera.shutter_speed = int( self.nt3656.shutter_speed )  # in microsecs
                self.camera.awb_mode = 'off'
                self.camera.awb_gains = (2,2)
                self.camera.exposure_mode = 'off'
            else:
                # TODO: to be able to toggle between bright and low exposure we would need to save the original camera statements to toggle.
                #self.camera.brightness = 30
                pass
            print( "camera.resolution={res}".format( res=(self.camera.resolution)) )
        
    def initNetTables(self):
        from nt3656 import Nt3656
        self.nt3656 = Nt3656()

    def isAutonomous(self):
        """Check network tables to see if the robot is using us."""

        # When the roborio is using set the smartdashboard yellowbox_mode var to on, otherwise we assume we are NOT use.
        active = None
        if self.yellowbox_mode:
            active = self.nt3656.yellowbox_mode
        else:
            active = self.nt3656.highgoal_mode

        return active == "on"

    def getImage(self):
        camera = self.camera

        if not(camera):
            # read an image from /var/tmp/images/currentImage/raw.jpg instead of capturing from the camera
            tmpcurimg = os.path.join(  tmpimagedir, "currentImage", "raw.jpg" ) 
            image = cv2.imread( tmpcurimg )
            return image

        from picamera.array import PiRGBArray
        
        # Create the in-memory stream
        #stream = io.BytesIO()
        #camera.capture(stream, format='bgr',use_video_port=True)
        #data = numpy.fromstring( stream.getvalue(), dtype=numpy.uint8)
        #image = cv2.imdecode(data, 1)

        #if not(self.rawCapture):
        self.rawCapture = PiRGBArray(camera)
        # use_video_port=True, from picamera docs. The image captured this way
        #  is of lower quality but faster. Seems to be roughly 5 times faster.
        camera.capture(self.rawCapture, format="bgr", use_video_port=True)
        image = self.rawCapture.array.copy()
        return image
#|


    def getRes(self):
        res = (400,304)
        if self.camera:
            res = self.camera.resolution

        return res
    #|

    def cp(self):
        res= self.getRes()
        cx=int(res[0]/2)
        cy=int(res[1]/2)

        return (cx,cy)


    def filter(self, blobs, contours=[]):
        """Use the target_zone to filter blobs that are likely not of interest."""

        res=self.getRes()
        center=self.cp()
        top_y=self.target_zone[0]*res[1]
        bot_y=self.target_zone[1]*res[1]

        fblobs = []
        if self.blobsupport:
            # blob support activity now optional
            for b in blobs:
                if b.size>self.minrad:            
                    if b.pt[1] >= top_y and b.pt[1] <= bot_y:
                        fblobs.append( b )

        fcontours = []
        for carr in contours:
            c = Contour( carr )
            if c.area>self.minarea:
                if c.cy >= top_y and c.cy <= bot_y:
                    fcontours.append( c )
            """    
            (brx, bry, brh, brw) = cv2.boundingRect( c )
            area =  brh * brw
            #c.area = area
            if area>self.minarea:
                c.cx = brx + brw / 2
                c.cy = bry + brh / 2
            """
                

        self.targets[ "blobs" ] = fblobs
        self.targets[ "contours" ] = fcontours

        return self.targets

    def estimateDistance(self, c1, c2):
        """Using simalrity estimate the distance of the goal."""

        tarWidthInches=9.0

        c1br = c1.br
        c2br = c2.br

        c1mpx = abs( c1br[1] - c1br[0])/2
        c2mpx = abs( c2br[1] - c2br[0])/2        
        
        perceivedWidthInPixels=abs( c1mpx - c2mpx )
        dist = (tarWidthInches * self.focalLength) / perceivedWidthInPixels

        self.estimatedDistance = dist
        return dist

    def analyze(self, features):
        """Analyze the blobs and summarize the information to send to the roboRIO"""
        self.lastannotated= self.lastraw.copy()
        res = self.getRes()
        resizefactor=1.0
        cx=int(res[0]/2)
        cy=int(res[1]/2)

        blobs=features.get("blobs", [])
        contours=features.get("contours", [])        

        red = (0, 0, 255)
        if self.blobsupport and self.debug:
            print( "blobs=%s" % blobs )

        if self.debug:
            print( "contours=%s" % len(contours) )
        self.targets = self.filter( blobs, contours )
        #self.targets = features # { "blobs": blobs, "contours": contours }
        now = datetime.datetime.now()

        if self.debug:
            #cv2.resizeWindow( "Analyze", 800, 600 )
            res=self.getRes()
            cv2.imshow( "Raw", self.lastannotated ) # , res[0], res[1] )
            cv2.waitKey(1)

        bcount = 0
        if self.blobsupport:
            if self.debug:
                print( "fblobs=%s" % self.targets.get( "blobs", [] ) )            

            for b in self.targets.get( "blobs", [] ):
                if self.debug:
                    print( "   blob=pt=%s, size=%s " % ( b.pt, b.size) )
                #bx=int(cx - int(b.pt[0] * resizefactor))
                #by=int(cy - int(b.pt[1] * resizefactor))
                bx=int(b.pt[0])
                by=int(b.pt[1])
                if self.debug:
                    print( " - (x=%s , y=%s )" % (bx,by) ) 
                cv2.circle( self.lastannotated, (bx,by), int(b.size), red )
                cv2.putText(self.lastannotated, "#{}".format(bcount), (bx - 10, by - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55, red, 1)

                bcount+=1

        # Annotate contours if detected
        contours=self.targets.get( "contours", [] )
        cidx=0
        for c in contours:
            if self.debug:
                print( "  contour cx=%s cy=%s, area=%s" % (c.cx, c.cy, c.area) )
            #cv2.drawContours( self.lastannotated, c.array, contourIdx=-1, color=red, thickness=1)
            (brx, bry, brw, brh) = c.br
            cv2.rectangle( self.lastannotated, (brx, bry), (brx+brw,bry+brh), color=red ) 
            cv2.putText(self.lastannotated, "#{}".format(cidx+1), (c.cx - 10, c.cy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, red, 1)
            
            cidx += 1

        if len(contours)>2:
            self.estimateDistance( contours[0], contours[1] )
            cv2.putText( self.lastannotated, "Distance: %4.2f inches" % self.estimatedDistance,  (20, res[1] - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, red, 1 )            

        showres=False
        if debug and showres:
            cv2.putText( self.lastannotated,
                         "res={res}".format( res=self.getRes() ),
                     (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.35, red, 1 )
        cv2.putText( self.lastannotated, "%s %s" % (now, self.name),  (20, res[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, red, 1 )
        mode = "lowexpo" if self.lowexposuremode else "bright"
        cv2.putText( self.lastannotated, "mode: %s" % mode,
                     ( res[0] - 100, res[1] - 10 ),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, red, 1 )

        imgcenter = (cx, cy)
        # Draw cross hairs
        cv2.line( self.lastannotated, (cx-5,cy),(cx+5, cy), red )
        cv2.line( self.lastannotated, (cx,cy+5),(cx, cy-5), red )

        top_y=int(self.target_zone[0]*res[1])
        bot_y=int(self.target_zone[1]*res[1])

        cv2.line( self.lastannotated, (0,top_y),(res[0],top_y), red )
        cv2.line( self.lastannotated, (0,bot_y),(res[0],bot_y), red )
        
        self.active = bcount>0 or cidx>0

        if len(self.targets.get( "countours", [] )) == 2:
            import copy
            self.realtargets = copy.deepcopy( self.targets )
            self.realblobcounter = 10
        else:
            self.realblobcounter -= 1

        # If we saw real contours a few cycles ago and we now have one contour
        #   write the files for review.
        if (self.realblobcounter>0 and len(self.targets.get( "countours", [] ))==1 and self.logfails) or int(self.nt3656.auton_mode) == 1:
            self.saveImage( self.rawCapture.array, self.lastannotated )
        

        if self.debug: # self.active and self.debug:
            res=self.getRes()
            cv2.imshow( "Analyze", self.lastannotated ) # , res[0], res[1] )
            cv2.waitKey(1)
        #|

        now = datetime.datetime.now()
        """
        if self.camera and self.active and \
           ( not(self.lastsave) or (now - self.lastsave).seconds> 5.0 ) :
            self.lastsave = now
            self.saveImage( self.rawCapture.array, self.lastannotated )
            self.lastraw = self.rawCapture.array
            #print( "Wrote %s" % f )
        """
        if self.isAutonomous(): # and self.camera
            if self.camera:
                self.saveImage( self.rawCapture.array, self.lastannotated )
                self.lastraw = self.rawCapture.array
            else:
                self.saveImage( None, None )

    def success(self):
        """Unit test code, to determine if the last processimage was successful or not"""

        return len( self.targets.get( "blobs" , [] ) ) == 2 or \
               len( self.targets.get( "contours", [] ) ) == 2


    def saveImage(self, rawimage, annotated, imgdir=None):
        # queue the image to be written by a thread.
        _imgdir=imgdir if imgdir else self.imagedir 
        pool.add_task( saveImageTask, { "rawimage": rawimage, "annotated": annotated, "imgdir": imgdir } )
        
    def _saveImage(self, rawimage, annotated,imgdir=None):
        if not(imgdir):
            now = datetime.datetime.now()
            self.suggest_no += 1
            seconds = secofday( now )
            imgdir = os.path.join( self.imagedir, "%s" % now.year, "%02d" % now.month, "%02d" % now.day, "%s" % seconds )

        if not(os.path.exists( imgdir ) ):
            os.makedirs( imgdir )

        rawfile = os.path.join( imgdir, "raw.jpg" )
        annotatedfile = os.path.join( imgdir, "annotated.jpg" )

        cv2.imwrite( rawfile, rawimage )
        cv2.imwrite( annotatedfile, annotated )

        if self.debug:
            print( "images written to %s" % imgdir )

    def updateRobot(self):
        """
        yellowboxsensor.blob_1.active
        yellowboxsensor.blob_1.suggest_no
        yellowboxsensor.blob_1.cx
        yellowboxsensor.blob_1.cy
        yellowboxsensor.blob_1.radius
        """

        # Sort the blobs by size and return the two largest blobs
        blobs = []
        active = 0
        contours = sorted( self.targets.get( "contours", []), key=lambda c: c.area, reverse=True)
        active = len(contours)
        if self.blobsupport:
            blobs = sorted( self.targets.get( "blobs", [] ), key=lambda b: b.size, reverse=True)
            active = len( contours ) + len( blobs )
        
        self.nt3656.sd.putNumber( "%s.active" % self.name, active )

        def putNumber( name, val ):
            if self.debug:
                print( "%s=%s" % (name, val) )
            self.nt3656.sd.putNumber( name, val )

        bigblobs = []
        if self.blobsupport:
            bidx=1
            for b in blobs:
                bigblobs.append( b )
                if bidx>2:
                    break
                bidx += 1

        """
        bigcontours = []
        cidx=1
        for c in contours:
            bigcontours.append( c )
            if cidx>2:
                break
            cidx += 1
        """
        bigcontours = contours

        # Order the blobs by their x value.
        if self.blobsupport:
            bigblobs = sorted( bigblobs, key=lambda b: b.pt[0] )
        bigcontours = sorted( bigcontours, key=lambda c: c.cx )        

        if self.blobsupport:
            # Write each blob to the network table
            bidx=1
            for b in bigblobs:
            
                putNumber( "%s.blob_%s.cx" % (self.name, bidx), b.pt[0] )
                putNumber( "%s.blob_%s.cy" % (self.name, bidx), b.pt[1] )
                putNumber( "%s.blob_%s.radius" % (self.name, bidx), b.size )           
                bidx += 1
                if bidx>2:
                    break

        # Write each contour to the network table
        cidx=1        
        for c in bigcontours:
            putNumber( "%s.contour_%s.cx" % (self.name, cidx), c.cx )
            putNumber( "%s.contour_%s.cy" % (self.name, cidx), c.cy )
            putNumber( "%s.contour_%s.area" % (self.name, cidx), c.area )           
            cidx += 1
            if cidx>2:
                break            

        # if we didn't find 2 blobls, write -1 for x value for both
        if cidx < 2:
            putNumber( "%s.contour_%s.cx" % (self.name, 1), -1 )
            putNumber( "%s.contour_%s.cx" % (self.name, 2), -1 )

        self.targets[ "blobs" ] = bigblobs
        self.targets[ "contours" ] = bigcontours        
        
        # Update the suggest_no last to guard against partial writes or network failures
        self.nt3656.sd.putNumber( "%s.suggest_no" % self.name, self.suggest_no )
        self.suggest_no += 1

    def processimage(self, imagefile ):
        """Convenience method primarily for training"""
        self.lastannotated = cv2.imread( imagefile )

        return self._processimage( self.lastannotated )

        
    def _processimage(self, image ):        
        """Primary method for using grip pipelines for processing the image."""

        gtimer = Timer("GRIP Pipeline")
        atimer = Timer("Analyze Blobs")
        nttimer = Timer( "Read NetTable")

        if True: # self.nt3656.isConnected():
            nttimer.start()
            nt3656 = self.nt3656
            """
            self.pipeline.__hsv_threshold_hue = \
                    [ nt3656.hsv_h_lo, nt3656.hsv_h_hi ]
            self.pipeline.__hsv_threshold_saturation = \
                    [ nt3656.hsv_s_lo, nt3656.hsv_s_hi ]
            self.pipeline.__hsv_threshold_value = \
                    [ nt3656.hsv_v_lo, nt3656.hsv_v_hi ]
            """
            """
            self.pipeline.setHsv( [ nt3656.hsv_h_lo, nt3656.hsv_h_hi ],
                                  [ nt3656.hsv_s_lo, nt3656.hsv_s_hi ],
                                  [ nt3656.hsv_v_lo, nt3656.hsv_v_hi ] )
            """
            if self.debug:
                print( "lowexpusure_mode=%s" % self.lowexposuremode )
                print( "shutter_speed=%s" % self.camera.shutter_speed )
                """
                import json
                with open( "nt3656.json", "w" ) as outf:
                    outf.write( json.dumps( self.nt3656 ) )
                """

            """
            if self.debug:
                print("hsv_threshold_hue=%s" % self.pipeline.__hsv_threshold_hue)
                print("hsv_threshold_saturation=%s" % self.pipeline.__hsv_threshold_saturation)
                print("hsv_threshold_value=%s" % self.pipeline.__hsv_threshold_value)
            """
            if self.camera:
                if  not(self.lowexposuremode):
                    # self.camera.brightness = int( self.nt3656.vis_cam_brightness )
                    pass
                else:
                    #self.camera.shutter_speed = int( self.nt3656.shutter_speed )  # in microsecs
                    pass
                    
            nttimer.stop()

        gtimer.start()
        self.pipeline.process( image )
        features={'blobs':[], 'countours':[]}
        blobs = []
        if hasattr( self.pipeline, "find_blobs_output" ):
            features[ 'blobs' ] = self.pipeline.find_blobs_output
        
        contours = []
        if hasattr( self.pipeline, "find_contours_output" ):
            # scoop out contours if you have them
            features[ 'contours' ] = self.pipeline.find_contours_output
            
        gtimer.stop()        
        atimer.start()
        self.analyze( features )
        atimer.stop()        

    def saveCurrentImage(self):
        """
        # For the gui (visionui) write the current image out for the casual observer.
        """
        lastannotated = self.lastannotated if self.lastannotated != None else self.lastraw
        if self.camera:
            self.saveImage( self.lastraw,
                            lastannotated,
                            os.path.join(  tmpimagedir, "currentImage" ) ) 
        #urimg =  "currentImage.jpg" )
        #cv2.imwrite(  curimg, self.lastannotated )

        
    def watch(self):
        """Watch the camera detecting Pipeline blobs as they appear. Main processing loop."""

        itimer = Timer("getImage")
        gtimer = Timer("GRIP Pipeline")
        atimer = Timer("Analyze Blobs")
        utimer = Timer("Update Robo RIO")

        #timers = [ itimer, gtimer, atimer, utimer ]
        timers = [ itimer, utimer ]
        lastimageupdate=None

        if self.debug:
            cv2.namedWindow( "Analyze", cv2.WINDOW_NORMAL )
            #cv2.resizeWindow( "Analyze", 800, 600 )     
        
        while True:
            try:
                # Keep the loop running despite a failure
                tw1=time.time()
                itimer.start()
                self.lastraw = self.getImage( )
                # Provide an updated image to potentially render in the web interface
                now=datetime.datetime.now()
                if not(lastimageupdate) or (now-lastimageupdate).seconds>self.updateCurrentImageInterval:
                    self.saveCurrentImage()
                    lastimageupdate=now
                
                itimer.stop()
                if self.debug:
                    print( type( self.lastraw ) )
                self._processimage( self.lastraw )
                if True: # not(self.debug): Turns out we want to see pictures and update the robot
                    utimer.start()
                    self.updateRobot()
                    utimer.stop()

                if self.debug:
                    for t in timers:
                        t.show()
            except:
                if self.debug:
                    # Raise the exception in debug mode, continue running otherwise
                    raise
                print("Ignoring exception")
                    


    

#from yellowboxgrip import GripPipeline

def main():
    global debug
    
    print("Let the pi warm up. Sleeping (0.5 secs)")
    time.sleep(3) # Let things warm on the pie?
    ap = argparse.ArgumentParser( description="Dreadbot Sensor Prototype" )
    ap.add_argument( "--debug","-d", action="store_true", default=False,
                     help="Debug mode. Show the camera image and annotations" )
    ap.add_argument( "--logfails","-l", action="store_true", default=False,
                     help="Dilengently log frames where the targets disappear after a detection.")
    ap.add_argument( "--target", "-t", default="yellowbox",
                     help="Choose yellowbox or highgoal target." )
    ap.add_argument( "--nocamera", "-n", action="store_true", default=False,
                     help="Debug the sensor without raspberry pi hardware. See code for more details." )
#changed default to True for lowexposure
    ap.add_argument( "--lowexposure", "-e", action="store_true", default=False,
                     help="Use low exposure mode instead of low brightness." )
    
    args = ap.parse_args()

    assert args.target in [ "yellowbox", "highgoal" ], "Invalid target '%s' must be either 'yellowbox' or 'highgoal'"

    pipeline=None
    if args.target == "yellowbox":
        from yellowboxgrip import GripPipeline
        #from greenblobgrip import GripPipeline
        pipeline=GripPipeline()
    if args.target == "highgoal":
        from highgoalgrip import GripPipeline
        pipeline=GripPipeline()

    #NetworkTables.initialize(server='roborio-3656-frc.local')
    debug = args.debug
    sensor = DreadbotSensor(
        args.target, pipeline,
        debug=args.debug,
        lowexposuremode=args.lowexposure,
        logfails=args.logfails,
        nocamera=args.nocamera
    )


    sensor.watch()

if "__main__" == __name__:
    main()
        
