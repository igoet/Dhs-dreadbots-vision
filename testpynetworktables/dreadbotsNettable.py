
#!/usr/bin/env python

from __future__ import print_function

# pip install pynetworktables

from networktables import NetworkTables

NetworkTables.initialize(server='roborio-3656-frc.local')

sd = NetworkTables.getTable('SmartDashboard')
pref = NetworkTables.getTable('SmartDashboard')

hsv_h_lo = prefs.getAutoUpdateValue( 'hsv_h_lo', 70.0 )
hsv_h_hi = prefs.getAutoUpateValue( 'hsv_h_hi', 120.0 )
hsv_s_lo = prefs.getAutoUpdateValue( 'hsv_s_lo', 0.0 )
hsv_s_hi = prefs.getAutoUpdateValue( 'hsv_s_hi', 255.0 )
hsv_v_lo = prefs.getAutoUpdateValue( 'hsv_v_lo', 100.0 )
hsv_v_hi = prefs.getAutoUpdateValue( 'hsv_v_hi', 255.0 )



    
