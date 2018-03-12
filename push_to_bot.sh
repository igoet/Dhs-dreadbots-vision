#!/bin/bash

TARGET=10.36.56.101
if [ ! "x$1" = "x" ] ; then
    TARGET="$1"
fi;

destdir=$( pwd | sed s/rseward/pi/g )
destdir=/home/pi/dreadbots

echo rsync -aPzv --exclude 'ansible/' * pi@$TARGET:${destdir}/
rsync -aPzv --exclude 'ansible/' * pi@$TARGET:${destdir}/
