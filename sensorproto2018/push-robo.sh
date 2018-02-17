#!/bin/bash

rsync -aPv *.py pi@10.36.56.101:$( pwd )/
