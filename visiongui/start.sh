#!/bin/bash

. $HOME/pyve/bin/activate

# We are using the python lunch utility to start and stop the Dreadbot GUI
#  interface programs. Unfortunately lunch doesn't play nice with the
#  python openssl implementation found in Ubuntu

# $HOME/.lunchrc specifies the programs to be started by lunch

rm -f /tmp/lunch-*
lunch --verbose


