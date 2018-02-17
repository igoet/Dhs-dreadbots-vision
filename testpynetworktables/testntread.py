#!/usr/bin/env python

from __future__ import print_function

# pip install pynetworktables

from networktables import NetworkTables

NetworkTables.enableVerboseLogging()
NetworkTables.initialize(server='roborio-3656-frc.local')
print( "Connected says: %s" % NetworkTables.isConnected() )

import time
time.sleep( 2 )

sd = NetworkTables.getTable('SmartDashboard')

print( "Connected says: %s" % NetworkTables.isConnected() )

#sd = NetworkTables.getTable('/')
stables = sd.getSubTables()
print( "= NetworkTables %s = " % len(stables) )
for st in stables:
    print( "- '%s'" % st )
print(" ")

def ShowTable(sd):
    keys = sd.getKeys()
    print( "= NetworkTables %s = " % len(keys) )

    for k in keys:
        print( "%s" % k )
        val = sd.getValue(k)
        print( "%s = %s" % (k,val) )
    print(" ")

ShowTable(sd)    
# read known values.
def showValue(sd, key):
    val = sd.getNumber( key )
    print( "%s = %s" % (key,val) )


"""    
showValue(sd, "gear.contour_1.cx" )
showValue(sd, "gear.contour_1.cy" )
showValue(sd, "gear.contour_1.area" )
"""

sd = NetworkTables.getTable('Preferences')
ShowTable(sd)
showValue(sd, "hsv_h" )
showValue(sd, "hsv_s" )
showValue(sd, "hsv_v" )

NetworkTables.shutdown()
