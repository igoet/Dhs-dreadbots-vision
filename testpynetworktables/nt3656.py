#!/usr/bin/env python

from __future__ import print_function

# pip install pynetworktables

from networktables import NetworkTables
from networktables.util import ntproperty

NetworkTables.initialize(server='roborio-3656-frc.local')

"""
+        self.__hsv_threshold_hue = [53.0, 103.0]
+        self.__hsv_threshold_saturation = [0.0, 255.0]
+        self.__hsv_threshold_value = [100.0, 255.0]
+#        self.__hsv_threshold_hue = [53.0, 106.0]
+#        self.__hsv_threshold_saturation = [0.0, 230.0]
+#        self.__hsv_threshold_value = [100.0, 255.0]
"""

class Nt3656(object):
    """Read / Write access to nettables."""
    writeDefault=False
    hsv_h_lo = ntproperty( '/Preferences/hsv_h_lo', 50.0, writeDefault=writeDefault ) #changed from 20
    hsv_h_hi = ntproperty( '/Preferences/hsv_h_hi', 90.0 , writeDefault=writeDefault ) #changed from 50
    hsv_s_lo = ntproperty( '/Preferences/hsv_s_lo',   10.0 , writeDefault=writeDefault )
    hsv_s_hi = ntproperty( '/Preferences/hsv_s_hi', 255.0 , writeDefault=writeDefault )
    hsv_v_lo = ntproperty( '/Preferences/hsv_v_lo', 20 , writeDefault=writeDefault ) #changed from -10.1
    hsv_v_hi = ntproperty( '/Preferences/hsv_v_hi', 255.0 , writeDefault=writeDefault )
    vis_cam_brightness = ntproperty( '/Preferences/vis_cam_brightness', 30, writeDefault = writeDefault )
    
    def __init__(self):
        self.sd = NetworkTables.getTable('SmartDashboard')
        self.prefs = NetworkTables.getTable('Preferences')        
        pass

    def isConnected(self):
        return NetworkTables.isConnected()
        
        

#help(prefs)





    
