#!/bin/bash

# Copy this to /home/pi to facilate the easier starting of the vision component

# Start the sensor. Also note you can pass --debug manually to the python script
#  with an HDMI monitor connected to view what opencv sees on the camera.
# ./start-vision.sh --debug
# or ./sensor.py --debug when you are in the sensorproto directory.
cd $HOME
mkdir -p /var/tmp/images/
/usr/bin/python $HOME/rseward/bitbucket/dreadbots/sensorproto/sensor.py $* 2>&1 | tee $HOME/vision-run.log


