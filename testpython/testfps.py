#!/usr/bin/env python

import time

lastupdate = None
frames = 0

while True:

    t1 = time.time()
    if not(lastupdate) or (t1 - lastupdate)>5.0:
        secs = 1
        if lastupdate:
            secs = (t1 - lastupdate)
        fps = (1.0 * frames) / secs
        
        with open( "status.txt", "w" ) as outf:
            msg = "fps: %.2f" % fps
            print( msg )
            outf.write( msg )
        lastupdate = t1
        frames=0
            
    frames = frames + 1
