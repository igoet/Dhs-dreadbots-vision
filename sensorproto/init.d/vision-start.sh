#!/bin/bash

# Copy this to /home/pi to facilate the easier starting of the vision component

# Start the sensor. Also note you can pass --debug manually to the python script
#  with an HDMI monitor connected to view what opencv sees on the camera.
# ./start-vision.sh --debug
# or ./sensor.py --debug when you are in the sensorproto directory.

scriptdir=$( dirname $0 )
echo screen -A -m -d -S vision $scriptdir/vision-run.sh
screen -A -m -d -S vision $scriptdir/vision-run.sh
screen -ls

# Start the UI, connect to http://10.36.56.101:9000/ to use it.
screen -ls | grep gui
if [ "$?" != "0" ] ; then
  screen -A -m -d -S gui $HOME/rseward/bitbucket/dreadbots/visiongui/start.sh
fi;
  
echo "Attach to the screen to see the output or run $scriptdir/vision-run.sh directly"
echo "screen -dR vision"

echo "Use the following urls to manage the Dreadbot vision."
echo " - http://10.36.56.101:9000/"
echo " - http://10.36.56.101:9001/"

#$HOME/rseward/bitbucket/dreadbots/sensorproto/sensor.py $*

