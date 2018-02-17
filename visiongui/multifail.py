#!/usr/bin/env python

from __future__ import print_function

import remi.gui as gui
from remi.gui import *
from remi import start, App
import remi.server as server

import os.path
import time

import subprocess
import datetime

userhome = os.path.expanduser( "~" )
exec(open(os.path.join( userhome,"dreadbots_config.py")).read())

from main import  dreadbotVisionUI
from calibrate import dreadbotVisionCalibrateUI


#Configuration
configuration = {'config_multiple_instance': True, 'config_address': '0.0.0.0', 'config_start_browser': False, 'config_enable_file_cache': False, 'config_project_name': 'dreadbotVisionUI', 'config_resourcepath': './res/', 'config_port': 9000}

if __name__ == "__main__":
    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    """
    start(dreadbotVisionUI, address=configuration['config_address'], port=configuration['config_port'], 
                        multiple_instance=configuration['config_multiple_instance'], 
                        enable_file_cache=configuration['config_enable_file_cache'],
                        start_browser=configuration['config_start_browser'])
    """

    # Main = 9000
    s1 = server.Server(dreadbotVisionUI,
                       address=configuration['config_address'],
                       port=9000, 
                        multiple_instance=configuration['config_multiple_instance'], 
                        enable_file_cache=configuration['config_enable_file_cache'],
                        start_browser=configuration['config_start_browser'])
    s2 = server.Server(dreadbotVisionCalibrateUI,
                       address=configuration['config_address'],
                       port=9001, 
                        multiple_instance=configuration['config_multiple_instance'], 
                        enable_file_cache=configuration['config_enable_file_cache'],
                        start_browser=configuration['config_start_browser'])
    while 1:
        time.sleep(1)
