#!/usr/bin/env python

from __future__ import print_function

# pip install pynetworktables

from networktables import NetworkTables

NetworkTables.initialize(server='roborio-3656-frc.local')

sd = NetworkTables.getTable('SmartDashboard')

"""

= Proposed robot movement protocol. =

      +y  +z
       |  /
       | / 
       |/
-x ____/______ +x
      /|
     / |
    /  |
  -z  -y 

FOV = Field of Vision

== Cameras ==
We will have three cameras labeled:

 * goalsensor = The camera used to sight the goal target.
 * gearsensor = The camera used to sight the gear target.
 * ropesensor = The camera used to find the rope target.


We will prefix suggestion fields with these names. E.g.
 * goalsensor.active
 * gearsensor.active
 * ropesensor.active

== Suggestion Fields ==

*.suggest_no
  Is a sequence generated by the camera code. The robioRIO can store the last value it has seen to decide if the information is stale and shouldn't be used.

*.active
  Is an indicator that indicates if the camera observes a target it is interested in. 1 indicates there is a target of interest. 0 indicates a target can not be found. If a active is 0, the driver should probably spin the robot until it finds a target.

If an goal/target is sighted in the camera. 
   Set goalsensor.active to 1 or a positve value
else:
   Set goalsensor.active to 0

If a the target is to left of the FOV:
   goalsensor.x_adj = negative number indicating the distance from the center
else:
   goalsensor.x_adj = positive number indicating the distance from the center

If the target is high in the FOV:
   goalsensor.z_adj = positive number indicating the distance from the center
else:
   goalsensor.z_adj = negative number indicating the distance from the center

The y_adj may also be set but will likely be meaningless as our current robot won't be able to change it's targeting by adjusting it's angle or height to the target.


"""

print( "Dreadbots, go!" )

print( "Set goalsensor values" )
sd.putNumber('goalsensor.suggest_no', 1012) # suggest number to let the robiorio no if the values have been updated. Stale values should be ignored?
sd.putNumber('goalsensor.active', 1)
sd.putNumber('goalsensor.cx', 1) # suggest a movement to the right
sd.putNumber('goalsensor.cy', 1) # suggest a movement to the front

print( "Set gearsensor values" )
sd.putNumber('gearsensor.suggest_no', 1012) # suggest number to let the robiorio no if the values have been updated. Stale values should be ignored?
sd.putNumber('gearsensor.active', 0)
sd.putNumber('gearsensor.cxj', 1) # suggest a movement to the right
sd.putNumber('gearsensor.cy', 1) # suggest a movement to the front

print( "Set gearsensor values" )
sd.putNumber('ropesensor.suggest_no', 1012) # suggest number to let the robiorio no if the values have been updated. Stale values should be ignored?
sd.putNumber('ropesensor.active', 0)
sd.putNumber('ropesensor.cx', 1) # suggest a movement to the right
sd.putNumber('ropesensor.cz', 1) # suggest a movement to the front



print( "Go, Dreadbots, Go! Exiting." )
