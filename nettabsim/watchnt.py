#!/usr/bin/env python

from __future__ import print_function

import time
import sys

# pip install pynetworktables

from networktables import NetworkTables

NetworkTables.enableVerboseLogging()
NetworkTables.initialize(server='roborio-3656-frc.local')

# It takes a minute for network tables to initialize
t1=time.time()
timeout=15
now=time.time()
while not(NetworkTables.isConnected()) and (now-t1)<timeout:
      #print("..")
      sys.stdout.write( '.' )
      sys.stdout.flush()
      #print( ".", endl="" )
      now=time.time()
      time.sleep( 1 )

print( "\n" )
sd = NetworkTables.getTable('SmartDashboard')
"""
stables = sd.getSubTables()
print( "= NetworkTables %s = " % len(stables) )
for st in stables:
    print( "- '%s'" % st )
print(" ")
"""

def ShowTable(sd):
    #help(sd)
    keys = sd.getKeys()
    print( "= NetworkTables %s = " % len(keys) )

    #help(sd)
    for k in sorted(keys):
        #print( "%s" % k )
        val = sd.getValue(k, None)
        print( "%s = %s" % (k,val) )
    print(" ")

ShowTable(sd)    
