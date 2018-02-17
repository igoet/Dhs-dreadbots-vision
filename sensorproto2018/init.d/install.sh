#!/bin/bash

cp vision-start.sh $HOME
cp vision-stop.sh $HOME
cp vision-run.sh $HOME

cp dreadbots-vision /etc/init.d/
update-rc.d dreadbots-vision defaults
