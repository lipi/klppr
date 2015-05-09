import kivy
kivy.require('1.8.0') # replace with your current kivy version !

import ConfigParser

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.properties import NumericProperty, BoundedNumericProperty
from kivy.logger import Logger

import jvc
from camera import AsyncCamera

class CalibScreen(BoxLayout):

    camera = ObjectProperty()
    filename = StringProperty('current.jpg')
    image = ObjectProperty()

    # will get initial values from camera, see initialize()
    # TODO: use camera-specific values instead of hardcoded ones
    # (query camera?)
    pan = BoundedNumericProperty(0, min=-150, max=150,
                                 errorhandler=lambda x: 150 if x > 150 else -150)
    tilt = BoundedNumericProperty(0, min=-40, max=40,
                                  errorhandler=lambda x: 40 if x > 40 else -40)
    zoom = BoundedNumericProperty(10, min=10, max=100, 
                                  errorhandler=lambda x: 100 if x > 100 else 10)

    pan_speed = NumericProperty(1)
    tilt_speed = NumericProperty(1)
    zoom_speed = NumericProperty(1)

    def __init__(self, **kwargs):
        super(CalibScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.clock_callback, 0.5)

    def initialize(self):
        Logger.info('Initialize...')
        # TODO: update pan/tilt/zoom as soon as camera responds
        #self.pan,self.tilt,self.zoom = self.camera.getptz()
        Logger.info('Done.')

    #
    # Camera control
    #

    def on_pan(self, instance, pos):
        Logger.info('pan: %d' % self.pan)
        self.camera.pantilt(self.pan, self.tilt)       
        Logger.info('done')

    def on_tilt(self, instance, pos):
        Logger.info('tilt: %d' % self.tilt)
        self.camera.pantilt(self.pan, self.tilt)
        Logger.info('done')

    def on_zoom(self, instance, pos):
        Logger.info('zoom: %d' % self.zoom)
        self.camera.zoom(self.zoom, self.zoom_speed)
        Logger.info('done')
        
    def clock_callback(self, dt):
        try:
            # TODO: update widget directly, instead of via file
            self.image.reload()
        except Exception as ex:
            print ex

class TestApp(App):

    def build(self):
        self.calib_screen = CalibScreen()
        return self.calib_screen

    def on_start(self):
        config = ConfigParser.RawConfigParser()
        config.read('camera.cfg')

        driver = jvc.JVC(host = config.get('access', 'hostname'),
                         user = config.get('access', 'user'),
                         password = config.get('access', 'password'))
        self.camera = AsyncCamera(driver) 

        self.calib_screen.camera = self.camera
        self.calib_screen.initialize()

    def on_stop(self):
        Logger.info('Logging out...')
        self.camera.close()
        Logger.info('Logout done.')
        return

if __name__ == '__main__':
    TestApp().run()
