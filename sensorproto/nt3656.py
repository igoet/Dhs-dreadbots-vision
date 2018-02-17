#!/usr/bin/env python

from __future__ import print_function

"""
TODO: Ask the drive programming team to set this when they enter auton mode. 

/SmartDashboard/auton_mode [0 or 1] 0: off, 1, on
"""

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

pipeline.hsv_threshold_hue=[50, 90]
pipeline.hsv_threshold_saturation=[0.0, 255.0]
pipeline.hsv_threshold_value=[20, 255.0]


"""

class Nt3656(object):
    """Read / Write access to nettables."""
    writeDefault=True
    hsv_h_lo = ntproperty( '/Preferences/hsv_h_lo', 50.0, writeDefault=writeDefault ) #changed from 20
    hsv_h_hi = ntproperty( '/Preferences/hsv_h_hi', 103.0 , writeDefault=writeDefault ) #changed from 50
    hsv_s_lo = ntproperty( '/Preferences/hsv_s_lo',   0.0 , writeDefault=writeDefault )
    hsv_s_hi = ntproperty( '/Preferences/hsv_s_hi', 230.0 , writeDefault=writeDefault )
    hsv_v_lo = ntproperty( '/Preferences/hsv_v_lo', 20 , writeDefault=writeDefault ) #changed from -10.1
    hsv_v_hi = ntproperty( '/Preferences/hsv_v_hi', 255.0 , writeDefault=writeDefault )
    vis_cam_brightness = ntproperty( '/Preferences/vis_cam_brightness', 30, writeDefault = writeDefault )
    gear_mode = ntproperty( '/SmartDashboard/gear_mode', "off", writeDefault = writeDefault )
    highgoal_mode = ntproperty( '/SmartDashboard/highgoal_mode', "off", writeDefault = writeDefault )
    shutter_speed = ntproperty( '/Preferences/vis_cam_shutter_speed', 5000, writeDefault = writeDefault ) # 5000
    auton_mode = ntproperty( '/SmartDashboard/auton_mode', 0, writeDefault=False) # The rio should write this value
    
    
    def __init__(self):
        self.sd = NetworkTables.getTable('SmartDashboard')
        self.prefs = NetworkTables.getTable('Preferences')
        #self.banana()
        pass

    def banana(self):
        # detect a banana
        self.hsv_h_lo = 190
        self.hsv_h_hi = 255
        self.hsv_s_lo = 150
        self.hsv_s_hi = 190
        self.hsv_v_lo = 200
        self.hsv_v_hi = 255

        

    def isConnected(self):
        return NetworkTables.isConnected()
        
        

#help(prefs)





    
