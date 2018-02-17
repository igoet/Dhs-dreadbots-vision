#!/usr/bin/env python


"""
A quick unit test to run a grip pipeline against an image on disk.

This is a great way to kick the tires on a python grip pipeline to
see if it detects the expected objects in the image.
"""

import argparse
import datetime
import copy

#import picamera
import io

import cv2
import numpy
import math
from enum import Enum

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

def main():
    ap = argparse.ArgumentParser( description="A utility to detect objects using a python grip pipeline" )

    ap.add_argument( "-i", "--image", help="Test image", default=None ) # , required=True )

    args = ap.parse_args()

    tester = DreadbotPipelineTester()
    while True:
        img = tester.getimage( imagefile=args.image  )
        features = tester.detect( img )

        tester.annotate( img, features)

        if args.image:
            break
            

    

def getpipeline(pipeline):
    from autolinegrip import GripPipeline
    #from yellowboxgrip import GripPipeline
    #from greenblobgrip import GripPipeline

    return GripPipeline()

"""
def getimage(imagefile):

    
    
    
    
def detect(imagefile):
"""

class DreadbotPipelineTester(object):

    def __init__(self):
        self.debug = True
        self.camera = None
        pass

    def getcamera(self):
        import picamera
        from picamera import PiCamera

        camera = PiCamera()
        camera.resolution = (400, 304)

        return camera

    def detect(self, img):
        
        #img = getimage( imagefile )

        print( "Getting the pipeline." )
        pipeline = getpipeline("yellowboxgrip")
    
        print( "Detect blobs" )
        #hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        
        pipeline.process( img )
        blobs = []
        contours = []
        lines = []
        
        if hasattr( pipeline, "find_blobs_output" ):
            blobs = pipeline.find_blobs_output
            print( "blobs=%s" % blobs )
            
        if hasattr( pipeline, "find_contours_output" ):
            contours = pipeline.find_contours_output
            print( "contours=%s" % contours )

        if hasattr( pipeline, "filter_lines_output" ):
            lines = pipeline.find_lines_output
            print( "lines=%s" % lines )
            
        return { "blobs": blobs,
                 "contours": contours,
                 "lines": lines }

    def getimage(self, imagefile):
        hsv=img=None
        if imagefile:
            print( "Loading the image: %s" % imagefile )
            img = cv2.imread( imagefile )
        else:
            if not(self.camera):
                self.camera = self.getcamera()
                
            imgfile =  "/tmp/testgrip.jpg" 
            self.camera.capture( imgfile )
            img = cv2.imread( imgfile )

        return img
        
    
    def annotate(self, img, features):
        """Take the image and annotate it with the features found."""

        res = (400, 302)
        target_zone = copy.deepcopy( res )
        cx=int(res[0]/2)
        cy=int(res[1]/2)
        
        now = datetime.datetime.now()
        annotated = numpy.copy( img )
        red = (0, 0, 255)

        bcount = 0
        if features.get( "blobs" ):
            blobs = features.get( "blobs", [] )
            print( "fblobs=%s" % blobs )            

            for b in blobs:
                print( "   blob=pt=%s, size=%s " % ( b.pt, b.size) )
                bx=int(b.pt[0])
                by=int(b.pt[1])
                if self.debug:
                    print( " - (x=%s , y=%s )" % (bx,by) ) 
                cv2.circle( annotated, (bx,by), int(b.size), red )
                cv2.putText(annotated, "#{}".format(bcount), (bx - 10, by - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55, red, 1)

                bcount+=1

        # Annotate contours if detected
        contours=features.get( "contours", [] )
        cidx=0
        for carr in contours:
            c = Contour(carr)
            if self.debug:
                #help(c)
                print( "  contour cx=%s cy=%s, area=%s" % (c.cx, c.cy, c.area) )
            #cv2.drawContours( annotated, c.array, contourIdx=-1, color=red, thickness=1)
            (brx, bry, brw, brh) = c.br
            cv2.rectangle( annotated, (brx, bry), (brx+brw,bry+brh), color=red ) 
            cv2.putText(annotated, "#{}".format(cidx+1), (c.cx - 10, c.cy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, red, 1)
            
            cidx += 1

        # Annotate lines if detected
        lines=features.get( "lines", [] )
        cidx=0
        for l in lines:
            #c = Contour(carr)
            if self.debug:
                #help(c)
                print( "  line x1=%s y1=%s x2=%s y2=%s" % (l.x1,l.y1,l.x2,l.y2) )
            #cv2.drawContours( annotated, c.array, contourIdx=-1, color=red, thickness=1)
            (lx1, ly1, lx2, ly2) = (int(l.x1), int(l.y1), int(l.x2), int(l.y2))
            cv2.line( annotated, (lx1,ly1),(lx2,ly2), red )            
            #cv2.rectangle( annotated, (brx, bry), (brx+brw,bry+brh), color=red )
            mx=int(abs(lx2-lx1)/2)
            my=int(abs(ly2-ly1)/2)
            cv2.putText(annotated, "#{}".format(cidx+1), ( mx -20 , my),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, red, 1)            
            cidx += 1            


            
        cv2.putText( annotated, "%s" % now,  (20, res[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, red, 1 )
        imgcenter = (cx, cy)
        cv2.line( annotated, (cx-5,cy),(cx+5, cy), red )
        cv2.line( annotated, (cx,cy+5),(cx, cy-5), red )

        top_y=int(target_zone[0]*res[1])
        bot_y=int(target_zone[1]*res[1])

        cv2.line( annotated, (0,top_y),(res[0],top_y), red )
        cv2.line( annotated, (0,bot_y),(res[0],bot_y), red )

        cv2.imwrite( "annotated.jpg", annotated )
        print( "Wrote annotated image to annotated.jpg" )
        cv2.imshow( "Analyze", annotated )

        if self.camera:
            cv2.waitKey(1) # 5000) # Show the image for 5 seconds
        else:
            hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
            cv2.imshow( "HSV", hsv )
            cv2.waitKey()
        
        pass
        

    
if __name__ == "__main__":
    main()
    

    
    
    
    
