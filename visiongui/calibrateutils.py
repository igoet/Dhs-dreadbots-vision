
import numpy
import cv2

class CalibrateTool(object):

    def __init__(self, imagefile, p1, p2):
        self.imagefile = imagefile
        self.p1 = p1
        self.p2 = p2
        pass

    def analyze(self):
        img = cv2.imread( self.imagefile )
        # TODO: to make this truly generic the image should be cropped to the same
        #  size as the view port on the web page. Currently 400 by 300. If not
        #  the roi will be different than the intended region of interest.

        # crop_img = img[200:400, 100:300] # Crop from x1, x2, y1, y2 -> 100, 200, 300, 400

        x1=self.p1[0]
        x2=self.p2[0]
        y1=self.p1[1]
        y2=self.p2[1]        
        w=abs( x1 - x2 )
        h=abs( y1 - y2 )
        if x1>x2:
            t=x2
            x2=x1
            x1=t
        if y1>y2:
            t=y2
            y2=y1
            y1=t
        
        print( "crop=(y1=%s:y2=%s,x1=%s,x2=%s" % ( y1,y2, x1, x2 ) )
        cv2.cvtColor( img, cv2.COLOR_BGR2HSV )
        roi = img[ y1:y2, x1:x2 ]
        
        cv2.imwrite( "roi.jpg", roi )
        #print( "len(roi)=%s" % ( numpy.shape(roi) ) )

        #chans = cv2.split(roi)
        colors = ( "h", "s", "v" )

        histmap = {
            "h": None,
            "s": None,
            "v": None
        }

        for chan,color in enumerate(colors):
        #for (chan, color) in zip( chans, colors):
            rangemax = 256
            if color == "h":
                # OpenCV max hue value is 180
                rangemax = 180
            hist = cv2.calcHist( [roi], [chan], None, [rangemax], [0,rangemax] )
            #print( "%s" % hist )

            histmap[ color ] = hist
            
            """
            lastpnt=( xoff, yoff)
            for x in xrange( 0, rangemax-1 ):
                pnt=(xoff+x,yoff-int(hist[x][0]))
                #print( "%s -> %s" % (lastpnt,pnt) )
                cv2.line( plot, lastpnt, pnt, colormap.get( "color" ) )
                lastpnt = pnt
            """
        #print( "histmap=%s" % histmap )    
        return histmap

        
        
