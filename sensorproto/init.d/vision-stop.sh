#!/bin/bash

#killall -v -r '.*sensor.*'
#killall -v -u pi python
pkill -u pi -f  '.*python.*sensor.*'
sleep 2
#killall -v -9 -r '.*sensor.*'
#killall -v -9 -u pi python
pkill -9 -u pi -f  '.*python.*sensor.*'
