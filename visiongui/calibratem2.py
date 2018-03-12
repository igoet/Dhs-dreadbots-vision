#!/usr/bin/env python

from __future__ import print_function

import os.path
import datetime
import json
import numpy

import remi.gui as gui
from remi.gui import *
from remi import start, App

from calibrateutils import CalibrateTool
#from plotlywidget import PlotlyWidget

# Read in config values
from nt3656 import Nt3656
nt3656 = Nt3656()

hsvValuesRead=False

userhome = os.path.expanduser( "~" )
exec(open(os.path.join( userhome, "dreadbots_config.py")).read())

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)


class PlotlyWidget(gui.Widget):
    def __init__(self, data=None, update=None, updateRate=1,
                 **kwargs):
        super(PlotlyWidget, self).__init__(**kwargs)
        self.updateRate = updateRate
        self.data = data
        self.update = update

        javascript_code = gui.Tag()
        javascript_code.type = 'script'
        javascript_code.attributes['type'] = 'text/javascript'
        code = """
        var PLOT = document.getElementById('plot');
        var url = "plot/get_refresh";
        var plotOptions = {
                           title: 'HSV'
                          ,xaxis: {title: 'value'}
                          ,yaxis: {title: '# pixels',type: 'linear'}
                          };
        plotOptions['margin'] = {t:50, l:50, r:30};
        data=[{x: [1,2,3,4,5],
               y: [1,4,9,16,25]},
             {x: [1,2,3,4,5],
              y: [1,2,3,4,5]},
             {x: [1,2,3,4,5],
               y: [1,4,6,8,10]} ];

        Plotly.newPlot(PLOT, data, plotOptions);

        Plotly.d3.json(url,
            function(error, data) {
                Plotly.plot(PLOT, data, plotOptions);
            });
        """
        javascript_code.add_child('code',   # Add to Tag
                                  code % {'id': id(self), })
        self.add_child('javascript_code', javascript_code)   # Add to widget

    def get_refresh(self):
        if self.data is None:
            return None, None

        txt = json.dumps(self.data, cls=MyEncoder)
        headers = {'Content-type': 'text/plain'}
        return [txt, headers]
#| 

class dreadbotVisionCalibrateUI(App):
    def __init__(self, *args, **kwargs):
        #html_head = '<script src="https://cdn.plot.ly/plotly-latest.min.js">'
        html_head = '<script src="res/plotly-latest.min.js">'
        html_head += '</script>'
        self.data = []
        self.colormap = {
            0: "H",
            1: "S",
            2: "V"
        }
        for idx in range(3):
            self.data.extend([{'x': [], 'y': [], 'type': 'scatter', 'mode':
                               'markers+lines', 'name': self.colormap.get(idx)}])
        
        if not 'editing_mode' in kwargs.keys():
            super(dreadbotVisionCalibrateUI, self).__init__(*args, static_file_path='./res/', html_head=html_head)

        
        self.calibrateTool = None
        self.histmap = None
        self.roiP1 = None
        self.roiP2 = None
        self.histogramType = "hue"
        

        

    def idle(self):
        global hsvValuesRead
        #idle function called every update cycle
        if not(hsvValuesRead):
            hsvValuesRead=self.getHsvValues()
            
        pass
    
    def main(self):
        return dreadbotVisionCalibrateUI.construct_ui(self)

    def styleInput(self, w):
        w.attributes['rows'] = "1"
        w.style['border-width'] = "1px"
        w.style['font-size'] = "20px"
        w.style['height'] = "30px"
        w.style['width'] = "100px"
        w.style['border-style'] = "solid"
        w.style['resize'] = "none"
        w.style['order'] = "1"

    def container1_key_down_listener(self):
        print("key_down")

    def image1_mouse_down(self, w, x, y):
        print("mouse_down x=%s y=%s" % (x,y) )
        self.roiP1 = ( int(x),int(y) )
        
    def image1_mouse_up(self, w, x, y):
        print("mouse_up x=%s y=%s" % (x,y) )
        self.roiP2 = ( int(x),int(y) )
        self.calibrateRegion()

    

    def calibrateRegion(self ):
        print( "calibrateRegion(%s, %s)" % (self.roiP1,self.roiP2) )
        self.calibrateTool = CalibrateTool("res/calibrationImage.jpg", self.roiP1, self.roiP2 )
        self.histmap = self.calibrateTool.analyze()
        print( "calibrateRegion(%s, %s)" % (self.roiP1,self.roiP2) )

        colormap = {
            0 : "h",
            1:  "s",
            2:  "v"
        }

        # Show one histogram at a time.
        #for hidx in xrange(len(colormap.keys())):
        hidx=None
        if self.histogramType and self.roiSelected():
            rangemax=256
            if self.histogramType == "hue":
                hidx = 0
                rangemax=180
            if self.histogramType == "sat":
                hidx = 1
            if self.histogramType == "value":
                hidx = 2
            print("histgramType=%s and hidx=%s" % (self.histogramType , hidx ) )
        
            hkey = colormap.get( hidx )
            hist = self.histmap.get( hkey, [] )
            self.data[0]['x'] = []
            self.data[0]['y'] = []            
            for x in xrange( 0, rangemax-1 ):
                self.data[0]['x'].append( x )
                v =hist[x][0]
                #v = hist[x][0]
                self.data[0]['y'].append( v )

        # trigger plotly to replot the graph
        jarray = []
        #for idx in range(len(self.data)):
        if hidx != None:
            idx=hidx
            varray = { 'x': self.data[0]['x'], 
                       'y': self.data[0]['y'],
                       'type': 'scatter',
                       'mode':'markers+lines',
                       'name': self.colormap.get(idx)
            }
            jarray.append( varray );
            
            print("jarray=%s"%jarray)
            print("type(jarray)=%s"%type(jarray[0]['y']))
        
            indices = repr(list(range(len(self.data))))

            cmd = """
        var PLOT = document.getElementById('plot');
        var url = "plot/get_refresh";
        var plotOptions = {
                           title: 'HSV'
                          ,xaxis: {title: '%(histogramType)s'}
                          ,yaxis: {title: '# pixels',type: 'linear'}
                          };
        plotOptions['margin'] = {t:50, l:50, r:30};

        data = %(data)s;
        Plotly.newPlot(PLOT, data, plotOptions);


        //Plotly.d3.json(url,
        //    function(error, data) {
        //        Plotly.plot(PLOT, data, plotOptions);
        //    });
            """ % { 'data': json.dumps( jarray, cls=MyEncoder ),
                    'histogramType': self.histogramType
                  }
        
            #cmd = \
            """
                var update = {x:%(x)s, y:%(y)s};
                Plotly.extendTraces(PLOT, update, %(indices)s,%(history)s);
            """ #% {'x': xarray, 'y': yarray, 'indices': indices,
            #       'history': 256}
            print( cmd )
            self.execute_javascript( cmd )
        
    

    def getImage(self, imagefile = None):

        mtime=0
        if imagefile:
            mtime = os.path.getmtime( imagefile )
        image1 = Image('/res/calibrationImage.jpg')
        image1.attributes['src'] = "/res/calibrationImage.jpg?mtime=%s" % mtime
        image1.attributes['editor_newclass'] = "False"
        image1.attributes['editor_baseclass'] = "Image"
        image1.attributes['editor_constructor'] = "('/res/calibrationImage.jpg')"
        image1.attributes['class'] = "Image"
        image1.attributes['editor_tag_type'] = "widget"
        image1.attributes['editor_varname'] = "image1"
        image1.style['top'] = "70px"
        image1.style['height'] = "300px"
        image1.style['width'] = "400px"
        image1.style['position'] = "absolute"
        image1.style['overflow'] = "auto"
        image1.style['margin'] = "0px"
        image1.style['display'] = "block"
        image1.style['left'] = "20px"
        self.image1 = image1
        self.container1.append(image1,'image1')

        self.image1.set_on_mouseup_listener( self.image1_mouse_up )
        self.image1.set_on_mousedown_listener( self.image1_mouse_down )        
        
        return self.image1
        
    def loadImage(self, imagefile):
        import shutil
        shutil.copy( imagefile, "res/calibrationImage.jpg" )
        self.getImage( imagefile )
        pass

    def loadImageFromFields(self):
        yyyy = self.yearText.get_text()
        mm = self.monthText.get_text()
        dd = self.dayText.get_text()
        suggest = self.suggestNoText.get_text()

        filename = os.path.join( imagedir, yyyy, mm, dd, suggest, "raw.jpg" )

        self.loadImage( filename )

    def suggest_on_blur(self, w):
        print("suggest_on_blur")
        self.loadImageFromFields()

    def roiSelected(self):
        return self.roiP1 and self.roiP2
        
        
    def hueButton_on_click(self, w):
        print("hueButton_on_click")
        if self.roiSelected():
            self.histogramType = "hue"
            self.calibrateRegion()
        #|

    def satButton_on_click(self, w):
        print("satButton_on_click")
        if self.roiSelected():
            self.histogramType = "sat"
            self.calibrateRegion()                          
        #|        

    def valueButton_on_click(self, w):
        print("valueButton_on_click")
        if self.roiSelected():
            self.histogramType = "value"
            self.calibrateRegion()
        #|

    def applyButton_on_click(self, w):
        print("applyButton_on_click")

        self.setHsvValues()

    def usecamButton_on_click(self, w):
        print("usecamButton_on_click")

        self.loadImage( "res/raw.jpg" )
        

    def setHsvValues(self):
        if not(nt3656.isConnected()):
            self.notification_message( "Error", "Cannot connect to roborio network tables. Check the pi's connection to robot's network!" )
            return

        def _getGuiVal( label, control ):
            val = control.get_text()
            print( "%s = %s" % (label, val) )
            return val
            
        nt3656.hsv_h_lo = float(  _getGuiVal( "hueLowText", self.hueLowText ) )
        nt3656.hsv_h_hi = float(  _getGuiVal( "hueHighText", self.hueHighText ) )
        nt3656.hsv_s_lo = float(  _getGuiVal( "satLowText", self.satLowText ) )
        nt3656.hsv_s_hi = float(  _getGuiVal( "satHighText", self.satHighText ) )
        nt3656.hsv_v_lo = float(  _getGuiVal( "valLowText", self.valLowText ) )
        nt3656.hsv_v_hi = float(  _getGuiVal( "valHighText", self.valHighText ) )
        nt3656.vis_cam_brightness = int( float(  _getGuiVal( "brightText", self.brightText ) ) )

        print( "Applied vals to roborio" )

        self.notification_message( "Info", "Applied values to roborio network tables." )        


    def getHsvValues(self):
        self.hueLowText.set_text( "%s" % nt3656.hsv_h_lo )
        self.hueHighText.set_text( "%s" % nt3656.hsv_h_hi )
        self.satLowText.set_text( "%s" % nt3656.hsv_s_lo )
        self.satHighText.set_text( "%s" % nt3656.hsv_s_hi )
        self.valLowText.set_text( "%s" % nt3656.hsv_v_lo )
        self.valHighText.set_text( "%s" % nt3656.hsv_v_hi )
        self.brightText.set_text( "%s" % nt3656.vis_cam_brightness )

        return nt3656.isConnected()
        
        
    @staticmethod
    def construct_ui(self):
        hsvCol1Left = "175px"
        hsvCol2Left = "295px"
        container1 = Widget()
        container1.attributes['editor_newclass'] = "False"
        container1.attributes['editor_baseclass'] = "Widget"
        container1.attributes['editor_constructor'] = "()"
        container1.attributes['class'] = "Widget"
        container1.attributes['editor_tag_type'] = "widget"
        container1.attributes['editor_varname'] = "container1"
        container1.style['font-weight'] = "bold"
        container1.style['top'] = "1px"
        container1.style['font-size'] = "24px"
        container1.style['height'] = "820px"
        container1.style['width'] = "1200px"
        container1.style['position'] = "absolute"
        container1.style['overflow'] = "auto"
        container1.style['order'] = "-1"
        container1.style['margin'] = "0px"
        container1.style['display'] = "block"
        container1.style['left'] = "1px"
        hueLowText = TextInput(True,'( low )')
        hueLowText.attributes['rows'] = "1"
        hueLowText.attributes['title'] = "Hue"
        hueLowText.attributes['editor_baseclass'] = "TextInput"
        hueLowText.attributes['editor_constructor'] = "(True,'( low )')"
        hueLowText.attributes['class'] = "TextInput"
        hueLowText.attributes['autocomplete'] = "off"
        hueLowText.attributes['editor_tag_type'] = "widget"
        hueLowText.attributes['editor_newclass'] = "False"
        hueLowText.attributes['editor_varname'] = "hueLowText"
        hueLowText.attributes['placeholder'] = "( low )"
        hueLowText.style['border-width'] = "1px"
        hueLowText.style['top'] = "412px"
        hueLowText.style['font-size'] = "20px"
        hueLowText.style['height'] = "30px"
        hueLowText.style['width'] = "100px"
        hueLowText.style['border-style'] = "solid"
        hueLowText.style['position'] = "absolute"
        hueLowText.style['overflow'] = "auto"
        hueLowText.style['margin'] = "0px"
        hueLowText.style['display'] = "block"
        hueLowText.style['resize'] = "none"
        hueLowText.style['left'] = hsvCol1Left 
        hueHighText = TextInput(True,'( high )')
        hueHighText.attributes['rows'] = "1"
        hueHighText.attributes['editor_baseclass'] = "TextInput"
        hueHighText.attributes['editor_constructor'] = "(True,'( high )')"
        hueHighText.attributes['class'] = "TextInput"
        hueHighText.attributes['autocomplete'] = "off"
        hueHighText.attributes['editor_tag_type'] = "widget"
        hueHighText.attributes['editor_newclass'] = "False"
        hueHighText.attributes['editor_varname'] = "hueHighText"
        hueHighText.attributes['placeholder'] = "( high )"
        hueHighText.style['right'] = "0px"
        hueHighText.style['border-width'] = "1px"
        hueHighText.style['top'] = "412px"
        hueHighText.style['font-size'] = "20px"
        hueHighText.style['height'] = "30px"
        hueHighText.style['width'] = "100px"
        hueHighText.style['border-style'] = "solid"
        hueHighText.style['position'] = "absolute"
        hueHighText.style['overflow'] = "auto"
        hueHighText.style['margin'] = "0px"
        hueHighText.style['display'] = "block"
        hueHighText.style['resize'] = "none"
        hueHighText.style['left'] = hsvCol2Left
        satLowText = TextInput(True,'( low )')
        satLowText.attributes['rows'] = "1"
        satLowText.attributes['editor_baseclass'] = "TextInput"
        satLowText.attributes['editor_constructor'] = "(True,'( low )')"
        satLowText.attributes['class'] = "TextInput"
        satLowText.attributes['autocomplete'] = "off"
        satLowText.attributes['editor_tag_type'] = "widget"
        satLowText.attributes['editor_newclass'] = "False"
        satLowText.attributes['editor_varname'] = "satLowText"
        satLowText.attributes['placeholder'] = "( low )"
        satLowText.style['top'] = "461px"
        satLowText.style['border-width'] = "1px"
        satLowText.style['height'] = "30px"
        satLowText.style['width'] = "100px"
        satLowText.style['border-style'] = "solid"
        satLowText.style['font-size'] = "20px"
        satLowText.style['position'] = "absolute"
        satLowText.style['overflow'] = "auto"
        satLowText.style['margin'] = "0px"
        satLowText.style['display'] = "block"
        satLowText.style['resize'] = "none"
        satLowText.style['left'] = hsvCol1Left
        satHighText = TextInput(True,'( high )')
        satHighText.attributes['rows'] = "1"
        satHighText.attributes['editor_baseclass'] = "TextInput"
        satHighText.attributes['editor_constructor'] = "(True,'( high )')"
        satHighText.attributes['class'] = "TextInput"
        satHighText.attributes['autocomplete'] = "off"
        satHighText.attributes['editor_tag_type'] = "widget"
        satHighText.attributes['editor_newclass'] = "False"
        satHighText.attributes['editor_varname'] = "satHighText"
        satHighText.attributes['placeholder'] = "( high )"
        satHighText.style['border-width'] = "1px"
        satHighText.style['top'] = "461px"
        satHighText.style['font-size'] = "20px"
        satHighText.style['height'] = "30px"
        satHighText.style['width'] = "100px"
        satHighText.style['border-style'] = "solid"
        satHighText.style['position'] = "absolute"
        satHighText.style['overflow'] = "auto"
        satHighText.style['margin'] = "0px"
        satHighText.style['display'] = "block"
        satHighText.style['resize'] = "none"
        satHighText.style['left'] = hsvCol2Left
        valLowText = TextInput(True,'( low )')
        valLowText.attributes['rows'] = "1"
        valLowText.attributes['editor_baseclass'] = "TextInput"
        valLowText.attributes['editor_constructor'] = "(True,'( low )')"
        valLowText.attributes['class'] = "TextInput"
        valLowText.attributes['autocomplete'] = "off"
        valLowText.attributes['editor_tag_type'] = "widget"
        valLowText.attributes['editor_newclass'] = "False"
        valLowText.attributes['editor_varname'] = "valLowText"
        valLowText.attributes['placeholder'] = "( low )"
        valLowText.style['top'] = "510px"
        valLowText.style['border-width'] = "1px"
        valLowText.style['height'] = "30px"
        valLowText.style['width'] = "100px"
        valLowText.style['border-style'] = "solid"
        valLowText.style['font-size'] = "20px"
        valLowText.style['position'] = "absolute"
        valLowText.style['overflow'] = "auto"
        valLowText.style['margin'] = "0px"
        valLowText.style['display'] = "block"
        valLowText.style['resize'] = "none"
        valLowText.style['left'] = hsvCol1Left
        valHighText = TextInput(True,'( high )')
        valHighText.attributes['rows'] = "1"
        valHighText.attributes['editor_baseclass'] = "TextInput"
        valHighText.attributes['editor_constructor'] = "(True,'( high )')"
        valHighText.attributes['class'] = "TextInput"
        valHighText.attributes['autocomplete'] = "off"
        valHighText.attributes['editor_tag_type'] = "widget"
        valHighText.attributes['editor_newclass'] = "False"
        valHighText.attributes['editor_varname'] = "valHighText"
        valHighText.attributes['placeholder'] = "( high )"
        valHighText.style['top'] = "510px"
        valHighText.style['border-width'] = "1px"
        valHighText.style['height'] = "30px"
        valHighText.style['width'] = "100px"
        valHighText.style['border-style'] = "solid"
        valHighText.style['font-size'] = "20px"
        valHighText.style['position'] = "absolute"
        valHighText.style['overflow'] = "auto"
        valHighText.style['margin'] = "0px"
        valHighText.style['display'] = "block"
        valHighText.style['resize'] = "none"
        valHighText.style['left'] = hsvCol2Left

        imageLabel = Label('Image :')
        imageLabel.attributes['editor_newclass'] = "False"
        imageLabel.attributes['editor_baseclass'] = "Label"
        imageLabel.attributes['editor_constructor'] = "('Image :')"
        imageLabel.attributes['class'] = "Label"
        imageLabel.attributes['editor_tag_type'] = "widget"
        imageLabel.attributes['editor_varname'] = "imageLabel"
        imageLabel.style['top'] = "657px"
        imageLabel.style['font-size'] = "26px"
        imageLabel.style['height'] = "30px"
        imageLabel.style['width'] = "100px"
        imageLabel.style['position'] = "absolute"
        imageLabel.style['overflow'] = "auto"
        imageLabel.style['font-weight'] = "bold"
        imageLabel.style['margin'] = "0px"
        imageLabel.style['display'] = "block"
        imageLabel.style['left'] = "21px"
        
        brightLabel = Label('Bright :')
        brightLabel.attributes['editor_newclass'] = "False"
        brightLabel.attributes['editor_baseclass'] = "Label"
        brightLabel.attributes['editor_constructor'] = "('Brightness :')"
        brightLabel.attributes['class'] = "Label"
        brightLabel.attributes['editor_tag_type'] = "widget"
        brightLabel.attributes['editor_varname'] = "brightLabel"
        brightLabel.style['top'] = "559px"
        brightLabel.style['font-size'] = "26px"
        brightLabel.style['height'] = "30px"
        brightLabel.style['width'] = "100px"
        brightLabel.style['position'] = "absolute"
        brightLabel.style['overflow'] = "auto"
        brightLabel.style['font-weight'] = "bold"
        brightLabel.style['margin'] = "0px"
        brightLabel.style['display'] = "block"
        brightLabel.style['left'] = "21px"

        brightText = TextInput(True,'( low )')
        brightText.attributes['rows'] = "1"
        brightText.attributes['title'] = "Bright"
        brightText.attributes['editor_baseclass'] = "TextInput"
        brightText.attributes['editor_constructor'] = "(True,'( low )')"
        brightText.attributes['class'] = "TextInput"
        brightText.attributes['autocomplete'] = "off"
        brightText.attributes['editor_tag_type'] = "widget"
        brightText.attributes['editor_newclass'] = "False"
        brightText.attributes['editor_varname'] = "brightText"
        brightText.attributes['placeholder'] = "( low )"
        brightText.style['border-width'] = "1px"
        brightText.style['top'] = "559px"
        brightText.style['font-size'] = "20px"
        brightText.style['height'] = "30px"
        brightText.style['width'] = "100px"
        brightText.style['border-style'] = "solid"
        brightText.style['position'] = "absolute"
        brightText.style['overflow'] = "auto"
        brightText.style['margin'] = "0px"
        brightText.style['display'] = "block"
        brightText.style['resize'] = "none"
        brightText.style['left'] = hsvCol1Left
        
        yearText = TextInput(True,'yyyy')
        yearText.attributes['rows'] = "1"
        yearText.attributes['editor_baseclass'] = "TextInput"
        yearText.attributes['editor_constructor'] = "(True,'yyyy')"
        yearText.attributes['class'] = "TextInput"
        yearText.attributes['autocomplete'] = "off"
        yearText.attributes['editor_tag_type'] = "widget"
        yearText.attributes['editor_newclass'] = "False"
        yearText.attributes['editor_varname'] = "yearText"
        yearText.attributes['placeholder'] = "yyyy"
        yearText.style['top'] = "657px"
        yearText.style['border-width'] = "1px"
        yearText.style['height'] = "30px"
        yearText.style['width'] = "100px"
        yearText.style['border-style'] = "solid"
        yearText.style['font-size'] = "20px"
        yearText.style['position'] = "absolute"
        yearText.style['overflow'] = "auto"
        yearText.style['margin'] = "0px"
        yearText.style['display'] = "block"
        yearText.style['resize'] = "none"
        yearText.style['left'] = "120px"
        
        monthText = TextInput(True,'mm')
        monthText.attributes['rows'] = "1"
        monthText.attributes['editor_baseclass'] = "TextInput"
        monthText.attributes['editor_constructor'] = "(True,'mm')"
        monthText.attributes['class'] = "TextInput"
        monthText.attributes['autocomplete'] = "off"
        monthText.attributes['editor_tag_type'] = "widget"
        monthText.attributes['editor_newclass'] = "False"
        monthText.attributes['editor_varname'] = "monthText"
        monthText.attributes['placeholder'] = "mm"
        monthText.style['top'] = "657px"
        monthText.style['border-width'] = "1px"
        monthText.style['height'] = "30px"
        monthText.style['width'] = "100px"
        monthText.style['border-style'] = "solid"
        monthText.style['font-size'] = "20px"
        monthText.style['position'] = "absolute"
        monthText.style['overflow'] = "auto"
        monthText.style['margin'] = "0px"
        monthText.style['display'] = "block"
        monthText.style['resize'] = "none"
        monthText.style['left'] = "230px"
        
        dayText = TextInput(True,'dd')
        dayText.attributes['rows'] = "1"
        dayText.attributes['editor_baseclass'] = "TextInput"
        dayText.attributes['editor_constructor'] = "(True,'dd')"
        dayText.attributes['class'] = "TextInput"
        dayText.attributes['autocomplete'] = "off"
        dayText.attributes['editor_tag_type'] = "widget"
        dayText.attributes['editor_newclass'] = "False"
        dayText.attributes['editor_varname'] = "dayText"
        dayText.attributes['placeholder'] = "dd"
        dayText.style['top'] = "657px"
        dayText.style['border-width'] = "1px"
        dayText.style['height'] = "30px"
        dayText.style['width'] = "100px"
        dayText.style['border-style'] = "solid"
        dayText.style['font-size'] = "20px"
        dayText.style['position'] = "absolute"
        dayText.style['overflow'] = "auto"
        dayText.style['margin'] = "0px"
        dayText.style['display'] = "block"
        dayText.style['resize'] = "none"
        dayText.style['left'] = "340px"
        
        suggestNoText = TextInput(True,'nnnnn')
        suggestNoText.attributes['rows'] = "1"
        suggestNoText.attributes['editor_baseclass'] = "TextInput"
        suggestNoText.attributes['editor_constructor'] = "(True,'nnnnn')"
        suggestNoText.attributes['class'] = "TextInput"
        suggestNoText.attributes['autocomplete'] = "off"
        suggestNoText.attributes['editor_tag_type'] = "widget"
        suggestNoText.attributes['editor_newclass'] = "False"
        suggestNoText.attributes['editor_varname'] = "suggestNoText"
        suggestNoText.attributes['placeholder'] = "nnnnn"
        suggestNoText.style['top'] = "657px"
        suggestNoText.style['border-width'] = "1px"
        suggestNoText.style['height'] = "30px"
        suggestNoText.style['width'] = "100px"
        suggestNoText.style['border-style'] = "solid"
        suggestNoText.style['font-size'] = "20px"
        suggestNoText.style['position'] = "absolute"
        suggestNoText.style['overflow'] = "auto"
        suggestNoText.style['margin'] = "0px"
        suggestNoText.style['display'] = "block"
        suggestNoText.style['resize'] = "none"
        suggestNoText.style['left'] = "450px"


        container1.append(imageLabel,'imageLabel')
        container1.append(brightLabel,'brightLabel')        
        
        container1.append(hueLowText,'hueLowText')        
        container1.append(hueHighText,'hueHighText')
        container1.append(satLowText,'satLowText')        
        container1.append(satHighText,'satHighText')        
        container1.append(valLowText,'valLowText')
        container1.append(valHighText,'valHighText')
        container1.append(brightText,'brightText')        

        container1.append(yearText,'yearText')        
        container1.append(monthText,'monthText')
        container1.append(dayText,'dayText')
        container1.append(suggestNoText,'suggestNoText')
        
        
        histogramContainer = Widget()
        histogramContainer.attributes['editor_newclass'] = "False"
        histogramContainer.attributes['editor_baseclass'] = "Widget"
        histogramContainer.attributes['editor_constructor'] = "()"
        histogramContainer.attributes['class'] = "Widget"
        histogramContainer.attributes['editor_tag_type'] = "widget"
        histogramContainer.attributes['editor_varname'] = "histogramContainer"
        histogramContainer.style['top'] = "70px"
        histogramContainer.style['height'] = "500px"
        histogramContainer.style['width'] = "600px"
        histogramContainer.style['border-style'] = "solid"
        histogramContainer.style['position'] = "absolute"
        histogramContainer.style['overflow'] = "auto"
        histogramContainer.style['margin'] = "0px"
        histogramContainer.style['display'] = "block"
        histogramContainer.style['left'] = "451px"
        histogramTitle = Label('Histogram Title')
        histogramTitle.attributes['editor_newclass'] = "False"
        histogramTitle.attributes['editor_baseclass'] = "Label"
        histogramTitle.attributes['editor_constructor'] = "('Histogram Title')"
        histogramTitle.attributes['class'] = "Label"
        histogramTitle.attributes['editor_tag_type'] = "widget"
        histogramTitle.attributes['editor_varname'] = "histogramTitle"
        histogramTitle.style['top'] = "-39px"
        histogramTitle.style['height'] = "30px"
        histogramTitle.style['width'] = "100px"
        histogramTitle.style['position'] = "absolute"
        histogramTitle.style['overflow'] = "auto"
        histogramTitle.style['order'] = "2"
        histogramTitle.style['margin'] = "0px"
        histogramTitle.style['display'] = "block"
        histogramTitle.style['left'] = "11px"
        container1.append(histogramTitle,'histogramTitle')
        container1.append(histogramContainer,'histogramContainer')
        

        hueButton = Button('Hue')
        hueButton.attributes['editor_newclass'] = "False"
        hueButton.attributes['editor_baseclass'] = "Button"
        hueButton.attributes['editor_constructor'] = "('Hue')"
        hueButton.attributes['class'] = "Button"
        hueButton.attributes['editor_tag_type'] = "widget"
        hueButton.attributes['editor_varname'] = "hueButton"
        hueButton.style['top'] = "13px"
        hueButton.style['height'] = "30px"
        hueButton.style['width'] = "100px"
        hueButton.style['position'] = "absolute"
        hueButton.style['overflow'] = "auto"
        hueButton.style['margin'] = "0px"
        hueButton.style['display'] = "block"
        hueButton.style['left'] = "490px"
        container1.append(hueButton,'hueButton')
        sat2Label = Label('Saturation :')
        sat2Label.attributes['editor_newclass'] = "False"
        sat2Label.attributes['editor_baseclass'] = "Label"
        sat2Label.attributes['editor_constructor'] = "('Saturation :')"
        sat2Label.attributes['class'] = "Label"
        sat2Label.attributes['editor_tag_type'] = "widget"
        sat2Label.attributes['editor_varname'] = "sat2Label"
        sat2Label.style['top'] = "461px"
        sat2Label.style['font-size'] = "24px"
        sat2Label.style['height'] = "38px"
        sat2Label.style['width'] = "152px"
        sat2Label.style['position'] = "absolute"
        sat2Label.style['overflow'] = "auto"
        sat2Label.style['font-weight'] = "bold"
        sat2Label.style['margin'] = "0px"
        sat2Label.style['display'] = "block"
        sat2Label.style['left'] = "21px"

        container1.append(sat2Label,'sat2Label')
        image1 = Image('/res/calibrationImage.jpg')
        image1.attributes['src'] = "/res/calibrationImage.jpg"
        image1.attributes['editor_newclass'] = "False"
        image1.attributes['editor_baseclass'] = "Image"
        image1.attributes['editor_constructor'] = "('/res/calibrationImage.jpg')"
        image1.attributes['class'] = "Image"
        image1.attributes['editor_tag_type'] = "widget"
        image1.attributes['editor_varname'] = "image1"
        image1.style['top'] = "70px"
        image1.style['height'] = "300px"
        image1.style['width'] = "400px"
        image1.style['position'] = "absolute"
        image1.style['overflow'] = "auto"
        image1.style['margin'] = "0px"
        image1.style['display'] = "block"
        image1.style['left'] = "20px"
        container1.append(image1,'image1')
        
        applyButton = Button('Apply')
        applyButton.attributes['editor_newclass'] = "False"
        applyButton.attributes['editor_baseclass'] = "Button"
        applyButton.attributes['editor_constructor'] = "('Apply')"
        applyButton.attributes['class'] = "Button"
        applyButton.attributes['editor_tag_type'] = "widget"
        applyButton.attributes['editor_varname'] = "applyButton"
        applyButton.style['top'] = "608px"
        applyButton.style['height'] = "30px"
        applyButton.style['width'] = "100px"
        applyButton.style['position'] = "absolute"
        applyButton.style['overflow'] = "auto"
        applyButton.style['margin'] = "0px"
        applyButton.style['display'] = "block"
        applyButton.style['left'] = "19px"
        container1.append(applyButton,'applyButton')
        
        usecamButton = Button('Use Camera Image')
        usecamButton.attributes['editor_newclass'] = "False"
        usecamButton.attributes['editor_baseclass'] = "Button"
        usecamButton.attributes['editor_constructor'] = "('Use Camera Images')"
        usecamButton.attributes['class'] = "Button"
        usecamButton.attributes['editor_tag_type'] = "widget"
        usecamButton.attributes['editor_varname'] = "usecamButton"
        usecamButton.style['top'] = "608px"
        usecamButton.style['height'] = "30px"
        usecamButton.style['width'] = "150px"
        usecamButton.style['position'] = "absolute"
        usecamButton.style['overflow'] = "auto"
        usecamButton.style['margin'] = "0px"
        usecamButton.style['display'] = "block"
        usecamButton.style['left'] = "139px"
        container1.append(usecamButton,'usecamButton')
        
        val2Label = Label('Value :')
        val2Label.attributes['editor_newclass'] = "False"
        val2Label.attributes['editor_baseclass'] = "Label"
        val2Label.attributes['editor_constructor'] = "('Value :')"
        val2Label.attributes['class'] = "Label"
        val2Label.attributes['editor_tag_type'] = "widget"
        val2Label.attributes['editor_varname'] = "val2Label"
        val2Label.style['top'] = "510px"
        val2Label.style['font-size'] = "24px"
        val2Label.style['height'] = "30px"
        val2Label.style['width'] = "100px"
        val2Label.style['position'] = "absolute"
        val2Label.style['overflow'] = "auto"
        val2Label.style['font-weight'] = "bold"
        val2Label.style['margin'] = "0px"
        val2Label.style['display'] = "block"
        val2Label.style['left'] = "21px"
        container1.append(val2Label,'val2Label')
        satButton = Button('Saturation')
        satButton.attributes['editor_newclass'] = "False"
        satButton.attributes['editor_baseclass'] = "Button"
        satButton.attributes['editor_constructor'] = "('Saturation')"
        satButton.attributes['class'] = "Button"
        satButton.attributes['editor_tag_type'] = "widget"
        satButton.attributes['editor_varname'] = "satButton"
        satButton.style['top'] = "14px"
        satButton.style['height'] = "30px"
        satButton.style['width'] = "100px"
        satButton.style['position'] = "absolute"
        satButton.style['overflow'] = "auto"
        satButton.style['margin'] = "0px"
        satButton.style['display'] = "block"
        satButton.style['left'] = "616px"
        container1.append(satButton,'satButton')
        titleLabel = Label('Calibrate')
        titleLabel.attributes['editor_newclass'] = "False"
        titleLabel.attributes['editor_baseclass'] = "Label"
        titleLabel.attributes['editor_constructor'] = "('Calibrate')"
        titleLabel.attributes['class'] = "Label"
        titleLabel.attributes['editor_tag_type'] = "widget"
        titleLabel.attributes['editor_varname'] = "titleLabel"
        titleLabel.style['right'] = "5px"
        titleLabel.style['top'] = "5px"
        titleLabel.style['font-size'] = "28px"
        titleLabel.style['height'] = "31px"
        titleLabel.style['width'] = "134px"
        titleLabel.style['position'] = "absolute"
        titleLabel.style['overflow'] = "auto"
        titleLabel.style['font-weight'] = "bold"
        titleLabel.style['margin'] = "0px"
        titleLabel.style['display'] = "block"
        titleLabel.style['left'] = "8px"
        container1.append(titleLabel,'titleLabel')
        hue2Label = Label('Hue :')
        hue2Label.attributes['editor_newclass'] = "False"
        hue2Label.attributes['editor_baseclass'] = "Label"
        hue2Label.attributes['editor_constructor'] = "('Hue:')"
        hue2Label.attributes['class'] = "Label"
        hue2Label.attributes['editor_tag_type'] = "widget"
        hue2Label.attributes['editor_varname'] = "hue2Label"
        hue2Label.style['top'] = "412px"
        hue2Label.style['font-size'] = "24px"
        hue2Label.style['height'] = "30px"
        hue2Label.style['width'] = "132px"
        hue2Label.style['position'] = "absolute"
        hue2Label.style['overflow'] = "auto"
        hue2Label.style['font-weight'] = "bold"
        hue2Label.style['margin'] = "0px"
        hue2Label.style['display'] = "block"
        hue2Label.style['left'] = "21px"
        container1.append(hue2Label,'hue2Label')
        valueButton = Button('Value')
        valueButton.attributes['editor_newclass'] = "False"
        valueButton.attributes['editor_baseclass'] = "Button"
        valueButton.attributes['editor_constructor'] = "('Value')"
        valueButton.attributes['class'] = "Button"
        valueButton.attributes['editor_tag_type'] = "widget"
        valueButton.attributes['editor_varname'] = "valueButton"
        valueButton.style['top'] = "15px"
        valueButton.style['height'] = "30px"
        valueButton.style['width'] = "100px"
        valueButton.style['position'] = "absolute"
        valueButton.style['overflow'] = "auto"
        valueButton.style['margin'] = "0px"
        valueButton.style['display'] = "block"
        valueButton.style['left'] = "747px"
        container1.append(valueButton,'valueButton')

        self.brightText = brightText
        self.hueLowText = hueLowText
        self.hueHighText = hueHighText
        self.satLowText = satLowText
        self.satHighText = satHighText
        self.valLowText = valLowText
        self.valHighText = valHighText
        self.yearText = yearText
        self.monthText = monthText
        self.dayText = dayText
        self.suggestNoText = suggestNoText
        self.histogramContainer = histogramContainer
        self.hueButton = hueButton
        self.satButton = satButton
        self.valueButton = valueButton
        self.applyButton = applyButton
        self.usecamButton = usecamButton

        self.styleInput( self.hueLowText )
        self.styleInput( self.hueHighText )
        self.styleInput( self.satLowText )
        self.styleInput( self.satHighText )
        self.styleInput( self.valLowText )
        self.styleInput( self.valHighText )

        self.styleInput( self.yearText )
        self.styleInput( self.monthText )
        self.styleInput( self.dayText )
        self.styleInput( self.suggestNoText )

        self.hueLowText.set_text( "25.0" )
        self.hueHighText.set_text( "35.0" )
        self.satLowText.set_text( "100.0" )
        self.satHighText.set_text( "170.0" )
        self.valLowText.set_text( "100.0" )
        self.valHighText.set_text( "255.0" )
        self.brightText.set_text( "30" )

        now = datetime.datetime.now()
        self.yearText.set_text( "%04d" % now.year )
        self.monthText.set_text( "%02d" % now.month )
        self.dayText.set_text( "%02d" % now.day )
        self.suggestNoText.set_text( "00001" )
        
        self.container1 = container1
        self.image1 = image1

        self.image1.set_on_mouseup_listener( self.image1_mouse_up )
        self.image1.set_on_mousedown_listener( self.image1_mouse_down )
        self.suggestNoText.set_on_blur_listener( self.suggest_on_blur )
        self.hueButton.set_on_click_listener( self.hueButton_on_click )
        self.satButton.set_on_click_listener( self.satButton_on_click )
        self.valueButton.set_on_click_listener( self.valueButton_on_click )
        self.applyButton.set_on_click_listener( self.applyButton_on_click )
        self.usecamButton.set_on_click_listener( self.usecamButton_on_click )
        

        plt = PlotlyWidget(data=self.data, id='plot')
        self.plt = plt
        histogramContainer.append(self.plt)
        self.getHsvValues()
        

        #self.container1.set_on_key_down_listener( self.container1_key_down_listener )
        return self.container1
    


#Configuration
configuration = {'config_multiple_instance': False, 'config_address': '0.0.0.0', 'config_start_browser': False, 'config_enable_file_cache': True, 'config_project_name': 'dreadbotVisionCalibrateUI', 'config_resourcepath': './res/', 'config_port': 9001}

if __name__ == "__main__":
    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    scriptdir = os.path.dirname(os.path.realpath(__file__))
    os.chdir( scriptdir )
    
    start(dreadbotVisionCalibrateUI, address=configuration['config_address'], port=configuration['config_port'], 
                        multiple_instance=configuration['config_multiple_instance'], 
                        enable_file_cache=configuration['config_enable_file_cache'],
                        start_browser=configuration['config_start_browser'])
