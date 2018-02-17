#!/usr/bin/env python

from __future__ import print_function

import remi.gui as gui
from remi.gui import *
from remi import start, App

import os.path

import subprocess
import datetime

userhome = os.path.expanduser( "~" )
exec(open(os.path.join( userhome,"dreadbots_config.py")).read())

class dreadbotVisionUI(App):
    def __init__(self, *args, **kwargs):
        if not 'editing_mode' in kwargs.keys():
            super(dreadbotVisionUI, self).__init__(*args, static_file_path='./res/')
        self.last_update=None
        self.last_status_update=None

    def idle(self):
        #idle function called every update cycle
        now = datetime.datetime.now()
        if not(self.last_status_update) or (now - self.last_status_update).seconds>1:
            self.updateStatus()
            # reload the image
            self.getImage()
            self.last_status_update = now

    
    def main(self):
        import subprocess
        rescurimg=os.path.join( "res", "currentImage.jpg" )
        if not(os.path.exists( rescurimg) ):
            curimg = os.path.join( tmpimagedir, "currentImage.jpg" )
            # Create a soft link to the currentImage in /var/tmp/
            #  for fast updates of the current image being seen by the robot.
            #  sensor.py should be writing this image to a ram disk
            subprocess.call( "ln -s %s %s" % ( curimg, rescurimg ), shell=True )
        
        return dreadbotVisionUI.construct_ui(self)

    def updateStatus(self):
        retcode = subprocess.call( "screen -ls | grep vision" , shell=True )
        status = "running" if retcode == 0 else "stopped"
        self.statusText.set_text( status )    

    def on_click_startButton(self, widget):
        print( "start .." )
        subprocess.call( "/usr/bin/screen -A -m -d -S vision %s" \
                         % (os.path.join(userhome, "vision-start.sh")), \
                         shell=True )
        self.updateStatus()

    def on_click_stopButton(self, widget):
        print( "stop .." )
        subprocess.call( (os.path.join(userhome,"vision-stop.sh")), \
                            shell=True )
        self.updateStatus()

    def on_click_calibrateButton(self, widget):
        print( "calibrate .." )
        self.getImage() # reload the image.
        #self.currentImage.attributes[ "src" ] = "/res/currentImage.jpg"
        self.execute_javascript( "console.log('Calibrate good times...'); window.location.href='http://%s:9001/';" % ipaddress )

    def getImage(self):

        currentImage = self.currentImage
        mtime = os.path.getmtime( os.path.join( tmpimagedir, "currentImage.jpg") )
        if not(self.last_update) or mtime>self.last_update:
            # Refresh the image
            self.last_update=mtime
        
            currentImage = Image('/res/currentImage.jpg' )
            currentImage.attributes['src'] = '/res/currentImage.jpg?foo=%s' % self.last_update 
            currentImage.attributes['editor_newclass'] = "False"
            currentImage.attributes['editor_baseclass'] = "Image"
            currentImage.attributes['editor_constructor'] = "('/res/currentImage.jpg')"
            currentImage.attributes['class'] = "Image"
            currentImage.attributes['editor_tag_type'] = "widget"
            currentImage.attributes['editor_varname'] = "currentImage"
            currentImage.style['top'] = "187px"
            currentImage.style['height'] = "600px"
            currentImage.style['width'] = "800px"
            currentImage.style['position'] = "absolute"
            currentImage.style['overflow'] = "auto"
            currentImage.style['margin'] = "0px"
            currentImage.style['display'] = "block"
            currentImage.style['left'] = "110px"
            self.currentImage = currentImage
            self.mainwin.append( currentImage, 'currentImage' )

        return currentImage
        
        
    @staticmethod
    def construct_ui(self):
        self.last_update=None
        self.currentImage=None
        
        container1 = Widget()
        container1.attributes['editor_newclass'] = "False"
        container1.attributes['editor_baseclass'] = "Widget"
        container1.attributes['editor_constructor'] = "()"
        container1.attributes['class'] = "Widget"
        container1.attributes['editor_tag_type'] = "widget"
        container1.attributes['editor_varname'] = "container1"
        container1.style['top'] = "43.765625px"
        container1.style['border-width'] = "28px"
        container1.style['height'] = "820px"
        container1.style['width'] = "1000px"
        container1.style['position'] = "absolute"
        container1.style['overflow'] = "auto"
        container1.style['font-weight'] = "bold"
        container1.style['margin'] = "0px"
        container1.style['display'] = "block"
        container1.style['left'] = "89.609375px"
        self.mainwin = container1
        
        currentImage = self.getImage()
        container1.append(currentImage,'currentImage')
        sensorNameText = Label(sensor)
        sensorNameText.attributes['editor_newclass'] = "False"
        sensorNameText.attributes['editor_baseclass'] = "Label"
        sensorNameText.attributes['editor_constructor'] = "('Sensor')"
        sensorNameText.attributes['class'] = "Label"
        sensorNameText.attributes['editor_tag_type'] = "widget"
        sensorNameText.attributes['editor_varname'] = "sensorNameText"
        sensorNameText.style['top'] = "76px"
        sensorNameText.style['font-size'] = "24px"
        sensorNameText.style['height'] = "30px"
        sensorNameText.style['width'] = "100px"
        sensorNameText.style['position'] = "absolute"
        sensorNameText.style['overflow'] = "auto"
        sensorNameText.style['margin'] = "0px"
        sensorNameText.style['display'] = "block"
        sensorNameText.style['left'] = "48px"
        container1.append(sensorNameText,'sensorNameText')
        statusLbl = Label('Status :')
        statusLbl.attributes['editor_newclass'] = "False"
        statusLbl.attributes['editor_baseclass'] = "Label"
        statusLbl.attributes['editor_constructor'] = "('Status :')"
        statusLbl.attributes['class'] = "Label"
        statusLbl.attributes['editor_tag_type'] = "widget"
        statusLbl.attributes['editor_varname'] = "statusLbl"
        statusLbl.style['top'] = "27px"
        statusLbl.style['font-size'] = "28px"
        statusLbl.style['height'] = "30px"
        statusLbl.style['width'] = "100px"
        statusLbl.style['position'] = "absolute"
        statusLbl.style['overflow'] = "auto"
        statusLbl.style['font-weight'] = "bold"
        statusLbl.style['margin'] = "0px"
        statusLbl.style['display'] = "block"
        statusLbl.style['left'] = "432px"
        container1.append(statusLbl,'statusLbl')
        startButton = Button('Start')
        startButton.attributes['editor_newclass'] = "False"
        startButton.attributes['editor_baseclass'] = "Button"
        startButton.attributes['editor_constructor'] = "('Start')"
        startButton.attributes['class'] = "Button"
        startButton.attributes['editor_tag_type'] = "widget"
        startButton.attributes['editor_varname'] = "startButton"
        startButton.style['top'] = "25px"
        startButton.style['height'] = "30px"
        startButton.style['width'] = "100px"
        startButton.style['position'] = "absolute"
        startButton.style['overflow'] = "auto"
        startButton.style['margin'] = "0px"
        startButton.style['display'] = "block"
        startButton.style['left'] = "275px"
        container1.append(startButton,'startButton')
        calibrateButton = Button('Calibrate')
        calibrateButton.attributes['editor_newclass'] = "False"
        calibrateButton.attributes['editor_baseclass'] = "Button"
        calibrateButton.attributes['editor_constructor'] = "('Calibrate')"
        calibrateButton.attributes['class'] = "Button"
        calibrateButton.attributes['editor_tag_type'] = "widget"
        calibrateButton.attributes['editor_varname'] = "calibrateButton"
        calibrateButton.style['top'] = "114px"
        calibrateButton.style['height'] = "30px"
        calibrateButton.style['width'] = "100px"
        calibrateButton.style['position'] = "absolute"
        calibrateButton.style['overflow'] = "auto"
        calibrateButton.style['margin'] = "0px"
        calibrateButton.style['display'] = "block"
        calibrateButton.style['left'] = "275px"
        container1.append(calibrateButton,'calibrateButton')
        statusText = TextInput(False,'< status >')
        statusText.attributes['editor_newclass'] = "False"
        statusText.attributes['editor_baseclass'] = "TextInput"
        statusText.attributes['editor_constructor'] = "(False,'< status >')"
        statusText.attributes['class'] = "TextInput"
        statusText.attributes['autocomplete'] = "off"
        statusText.attributes['editor_tag_type'] = "widget"
        statusText.attributes['editor_varname'] = "statusText"
        statusText.attributes['placeholder'] = "< status >"
        statusText.style['top'] = "24px"
        statusText.style['font-size'] = "28px"
        statusText.style['height'] = "32px"
        statusText.style['width'] = "220px"
        statusText.style['position'] = "absolute"
        statusText.style['overflow'] = "auto"
        statusText.style['margin'] = "0px"
        statusText.style['display'] = "block"
        statusText.style['left'] = "560px"
        container1.append(statusText,'statusText')
        stopButton = Button('Stop')
        stopButton.attributes['editor_newclass'] = "False"
        stopButton.attributes['editor_baseclass'] = "Button"
        stopButton.attributes['editor_constructor'] = "('Stop')"
        stopButton.attributes['class'] = "Button"
        stopButton.attributes['editor_tag_type'] = "widget"
        stopButton.attributes['editor_varname'] = "stopButton"
        stopButton.style['top'] = "68px"
        stopButton.style['height'] = "30px"
        stopButton.style['width'] = "100px"
        stopButton.style['position'] = "absolute"
        stopButton.style['overflow'] = "auto"
        stopButton.style['margin'] = "0px"
        stopButton.style['display'] = "block"
        stopButton.style['left'] = "276px"
        container1.append(stopButton,'stopButton')
        label1 = Label('Dreadbots Vision :')
        label1.attributes['editor_newclass'] = "False"
        label1.attributes['editor_baseclass'] = "Label"
        label1.attributes['editor_constructor'] = "('Dreadbots Vision :')"
        label1.attributes['class'] = "Label"
        label1.attributes['editor_tag_type'] = "widget"
        label1.attributes['editor_varname'] = "label1"
        label1.style['top'] = "28px"
        label1.style['font-size'] = "28px"
        label1.style['height'] = "33px"
        label1.style['width'] = "266px"
        label1.style['position'] = "absolute"
        label1.style['overflow'] = "auto"
        label1.style['font-weight'] = "bold"
        label1.style['margin'] = "0px"
        label1.style['display'] = "block"
        label1.style['left'] = "8px"
        container1.append(label1,'label1')


        self.statusText = statusText
        self.currentImage = currentImage
        startButton.set_on_click_listener(self.on_click_startButton)
        stopButton.set_on_click_listener(self.on_click_stopButton)
        calibrateButton.set_on_click_listener(self.on_click_calibrateButton)

        
        
        

        self.container1 = container1
        return self.container1
    


#Configuration
configuration = {'config_multiple_instance': True, 'config_address': '0.0.0.0', 'config_start_browser': False, 'config_enable_file_cache': False, 'config_project_name': 'dreadbotVisionUI', 'config_resourcepath': './res/', 'config_port': 9000}

if __name__ == "__main__":
    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    start(dreadbotVisionUI, address=configuration['config_address'], port=configuration['config_port'], 
                        multiple_instance=configuration['config_multiple_instance'], 
                        enable_file_cache=configuration['config_enable_file_cache'],
                        start_browser=configuration['config_start_browser'])
