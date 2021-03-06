#!/usr/bin/env python

import cv2
import datetime
import math

from engine import BaseSensorPipeline

class DreadbotYellowboxSensor(BaseSensorPipeline):
    """yellowbox specific processing code is here."""
    
    def __init__(self, name, pipeline):
        BaseSensorPipeline.__init__(self, name, pipeline )  # Class the super class's __init__ method
        self.target_zone = (0.0, 1.0)  #just use then entire image to find boxes
        self.color = red = (0, 0, 255)

        # Filter contours based on their area
        self.minrad = 18.0
        self.minarea = math.pi * self.minrad * self.minrad
        
        #self.pipeline = pipeline

    def analyze(self, engine, features):
        """Analyze the blobs and summarize the information to send to the roboRIO"""
        self.engine = engine
        debug = self.engine.debug
        res = self.engine.getRes()

        lastannotated = self.engine.lastannotated
        resizefactor=1.0
        cx=int(res[0]/2)
        cy=int(res[1]/2)

        blobs=features.get("blobs", [])
        contours=features.get("contours", [])        

        if self.engine.blobsupport and debug:
            print( "blobs=%s" % blobs )

        if debug:
            print( "contours=%s" % len(contours) )
        self.targets = self.filter( blobs, contours )
        #self.targets = features # { "blobs": blobs, "contours": contours }
        now = datetime.datetime.now()

        bcount = 0
        if self.engine.blobsupport:
            if debug:
                print( "fblobs=%s" % self.targets.get( "blobs", [] ) )            

            for b in self.targets.get( "blobs", [] ):
                if debug:
                    print( "   blob=pt=%s, size=%s " % ( b.pt, b.size) )
                bx=int(b.pt[0])
                by=int(b.pt[1])
                if debug:
                    print( " - (x=%s , y=%s )" % (bx,by) ) 
                cv2.circle( lastannotated, (bx,by), int(b.size), self.color )
                cv2.putText( lastannotated, "#{}".format(bcount), (bx - 10, by - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55, self.color, 1)

                bcount+=1

        # Annotate contours if detected
        contours=self.targets.get( "contours", [] )
        cidx=0
        for c in contours:
            if debug:
                print( "  contour cx=%s cy=%s, area=%s" % (c.cx, c.cy, c.area) )
            #cv2.drawContours( lastannotated, c.array, contourIdx=-1, color=self.color, thickness=1)
            (brx, bry, brw, brh) = c.br
            cv2.rectangle( lastannotated, (brx, bry), (brx+brw,bry+brh), color=self.color ) 
            cv2.putText(lastannotated, "#{}".format(cidx+1), (c.cx - 10, c.cy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, self.color, 1)
            
            cidx += 1

        """
        Distance was for the gear
        if len(contours)>2:
            self.estimateDistance( contours[0], contours[1] )
            cv2.putText( lastannotated, "Distance: %4.2f inches" % self.estimatedDistance,  (20, res[1] - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, self.color, 1 )
        """

        showres=False
        if debug and showres:
            cv2.putText( lastannotated,
                         "res={res}".format( res=self.engine.getRes() ),
                     (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.35, self.color, 1 )
        cv2.putText( lastannotated, "%s %s" % (now, self.name),  (20, res[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, self.color, 1 )
        mode = "lowexpo" if self.engine.lowexposuremode else "bright"
        cv2.putText( lastannotated, "mode: %s" % mode,
                     ( res[0] - 100, res[1] - 10 ),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, self.color, 1 )

        imgcenter = (cx, cy)
        # Draw cross hairs
        cv2.line( lastannotated, (cx-5,cy),(cx+5, cy), self.color )
        cv2.line( lastannotated, (cx,cy+5),(cx, cy-5), self.color )

        top_y=int(self.target_zone[0]*res[1])
        bot_y=int(self.target_zone[1]*res[1])

        cv2.line( lastannotated, (0,top_y),(res[0],top_y), self.color )
        cv2.line( lastannotated, (0,bot_y),(res[0],bot_y), self.color )
        
        self.active = bcount>0 or cidx>0

        if len(self.targets.get( "countours", [] )) == 2:
            import copy
            self.realtargets = copy.deepcopy( self.targets )
            self.realblobcounter = 10
        else:
            self.realblobcounter -= 1

        # TODO: This should be moved into an engine method.
        # If we saw real contours a few cycles ago and we now have one contour
        #   write the files for review.
        if (self.realblobcounter>0 and len(self.targets.get( "countours", [] ))==1 and self.engine.logfails) or int(self.engine.nt3656.auton_mode) == 1:
            self.engine.saveImage( self.engine.rawCapture.array, lastannotated )
        

        if debug: # self.active and debug:
            res=self.engine.getRes()
            cv2.imshow( "Analyze", lastannotated ) # , res[0], res[1] )
            cv2.waitKey(1)

    #|

    def updateRobot(self, engine):
        self.engine = engine
        debug = self.engine.debug
        """
        yellowboxsensor.blob_1.active
        yellowboxsensor.blob_1.suggest_no
        yellowboxsensor.blob_1.cx
        yellowboxsensor.blob_1.cy
        yellowboxsensor.blob_1.radius
        """

        # Sort the blobs by size and return the largest objects
        blobs = []
        active = 0
        contours = sorted( self.targets.get( "contours", []), key=lambda c: c.area, reverse=True)
        active = len(contours)
        if self.engine.blobsupport:
            blobs = sorted( self.targets.get( "blobs", [] ), key=lambda b: b.size, reverse=True)
            active = len( contours ) + len( blobs )
        
        self.engine.nt3656.sd.putNumber( "%s.active" % self.name, active )

        def putNumber( name, val ):
            if debug:
                print( "%s=%s" % (name, val) )
            self.engine.nt3656.sd.putNumber( name, val )

        bigblobs = []
        if self.engine.blobsupport:
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
        if self.engine.blobsupport:
            bigblobs = sorted( bigblobs, key=lambda b: b.pt[0] )
        bigcontours = sorted( bigcontours, key=lambda c: c.cx )        

        if self.engine.blobsupport:
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
        self.engine.nt3656.sd.putNumber( "%s.suggest_no" % self.name, self.engine.suggest_no )
        self.engine.suggest_no += 1
    #|

class DreadbotAutolineSensor(BaseSensorPipeline):
    """autoline specific processing code is here."""
    
    def __init__(self, name, pipeline):
        BaseSensorPipeline.__init__( self, name, pipeline )  # Class the super class's __init__ method
        self.target_zone = (0.66, 1.0)  # The autoline should be in the bottom half of the image.
        self.color = green = (0,255,0)
        #self.pipeline = pipeline
    pass

    def analyze(self, engine, features):
        """Analyze the blobs and summarize the information to send to the roboRIO"""
        self.engine = engine
        debug = self.engine.debug
        res = self.engine.getRes()

        lastannotated = self.engine.lastannotated
        resizefactor=1.0
        cx=int(res[0]/2)
        cy=int(res[1]/2)

        lines=features.get("lines", [])

        if debug:
            print( "lines=%s" % len(lines) )
        self.targets = self.filter( lines=lines )
        now = datetime.datetime.now()

        bcount = 0
        
        # Annotate lines if detected
        lines=self.targets.get( "lines", [] )
        cidx=0
        for l in lines:
            if debug:
                print( "  line (%s,%s)->(%s,%s)" % (l.x1, l.y1, l.x2, l.y2) )
            (lx1, ly1, lx2, ly2) = (int(l.x1), int(l.y1), int(l.x2), int(l.y2))
            cv2.line( lastannotated, (lx1,ly1),(lx2,ly2), self.color )            
            """ Too many lines to annotate really.
            mx=int(min(l.x1,l.x2)+abs(l.x2-l.x1)/2)
            my=int(min(l.y1,l.y2)+abs(l.y2-l.y1)/2)
            cv2.putText(lastannotated, "#{}".format(cidx+1), ( mx -20 , my),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, self.color, 1)
            """
            
            cidx += 1

        showres=False
        if debug and showres:
            cv2.putText( lastannotated,
                         "res={res}".format( res=self.engine.getRes() ),
                     (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.35, self.color, 1 )
        cv2.putText( lastannotated, "%s %s" % (now, self.name),  (20, res[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, self.color, 1 )
        mode = "lowexpo" if self.engine.lowexposuremode else "bright"
        cv2.putText( lastannotated, "mode: %s" % mode,
                     ( res[0] - 100, res[1] - 10 ),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, self.color, 1 )

        imgcenter = (cx, cy)
        # Draw cross hairs
        cv2.line( lastannotated, (cx-5,cy),(cx+5, cy), self.color )
        cv2.line( lastannotated, (cx,cy+5),(cx, cy-5), self.color )

        top_y=int(self.target_zone[0]*res[1])
        bot_y=int(self.target_zone[1]*res[1])

        cv2.line( lastannotated, (0,top_y),(res[0],top_y), self.color )
        cv2.line( lastannotated, (0,bot_y),(res[0],bot_y), self.color )
        
        self.active = bcount>0 or cidx>0

        if debug: # self.active and debug:
            res=self.engine.getRes()
            cv2.imshow( "Analyze", lastannotated ) # , res[0], res[1] )
            cv2.waitKey(1)

    #|



class SensorFactory(object):
    """Given a target name return the appropriate grip piplein."""

    def getSensor(self, target):
        gpf = GripPipelineFactory()
        pipeline = gpf.getGripPipeline(target)        
        if target == "yellowbox":
            return DreadbotYellowboxSensor(target, pipeline)
        if target == "autoline":
            return DreadbotAutolineSensor(target, pipeline)
        return None


class GripPipelineFactory(object):
    """Given a target name return the appropriate grip piplein."""

    def getGripPipeline(self, target):
        if target == "yellowbox":
            from yellowboxgrip import GripPipeline

            return GripPipeline()
        if target == "autoline":
            from autolinegrip import GripPipeline

            return GripPipeline()

        return None
        

if __name__ == "__main__":
    sf = SensorFactory()
    import engine
    engine.main(sf)
