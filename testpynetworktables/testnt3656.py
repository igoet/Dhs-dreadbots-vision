#!/usr/bin/env python

from __future__ import print_function

from nt3656 import Nt3656

import time
time.sleep(2)

nt3656 = Nt3656()
print( "hsv_h_lo=%s" % nt3656.hsv_h_lo )
print( "hsv_h_hi=%s" % nt3656.hsv_h_hi )
print( "hsv_s_lo=%s" % nt3656.hsv_s_lo )
print( "hsv_s_hi=%s" % nt3656.hsv_s_hi )
print( "hsv_v_lo=%s" % nt3656.hsv_v_lo )
print( "hsv_v_hi=%s" % nt3656.hsv_v_hi )
print( "vis_cam_brightness=%s" % nt3656.vis_cam_brightness )

