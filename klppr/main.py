#!/usr/bin/python
#
# klppr app
# 

import pickle

import kivy
kivy.require('1.8.0') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty, StringProperty
from kivy.properties import NumericProperty, BoundedNumericProperty
from kivy.logger import Logger
from kivy.lib import osc
from kivy.utils import platform
from kivy.clock import Clock

class CalibScreen(BoxLayout):

    image = ObjectProperty()

    # TODO: get initial values from camera, see initialize()
    # TODO: use camera-specific values instead of hardcoded ones
    # (query camera?)
    pan = BoundedNumericProperty(0, min=-150, max=150,
                                 errorhandler=lambda x: 150 if x > 150 else -150)
    tilt = BoundedNumericProperty(0, min=-40, max=40,
                                  errorhandler=lambda x: 40 if x > 40 else -40)
    zoom = BoundedNumericProperty(10, min=10, max=100, 
                                  errorhandler=lambda x: 100 if x > 100 else 10)

    pan_speed = NumericProperty(1) # TODO: increase speed while button is held
    tilt_speed = NumericProperty(1)# TODO: increase speed while button is held
    zoom_speed = NumericProperty(1)# TODO: increase speed while button is held

    def __init__(self, **kwargs):
        super(CalibScreen, self).__init__(**kwargs)

    def initialize(self):
        # TODO: update pan/tilt/zoom as soon as
        # camera responds
        # self.pan,self.tilt,self.zoom =
        # self.camera.getptz()
        pass

    #
    # Camera control
    #

    def on_pan(self, instance, pos):
        Logger.info('pan: %d' % self.pan)
        data = pickle.dumps((self.pan, self.tilt))
        osc.sendMsg('/pantilt', [data,], port=3000)

    def on_tilt(self, instance, pos):
        Logger.info('tilt: %d' % self.tilt)
        data = pickle.dumps((self.pan, self.tilt))
        osc.sendMsg('/pantilt', [data,], port=3000)

    def on_zoom(self, instance, pos):
        Logger.info('zoom: %d' % self.zoom)
        data = pickle.dumps((self.zoom, self.zoom_speed))
        osc.sendMsg('/zoom', [data,], port=3000)
        

    #
    # OSC cllback
    #
    def process_image(self, message, *args):
        return
        print 'message:', message
        return

        buf = None
        try:
            buf = message[2]
        except Exception as ex:
            #print ex
            pass

        if buf is not None:
            img = Image.open(StringIO(buf))
            # img is RGB, convert it to RGBA (Nexus 4 can't blit RGB),
            # see https://github.com/kivy/kivy/issues/1600
            img.putalpha(255)
            buf = img.tostring()
            tex = Texture.create(size=img.size, colorfmt='rgba')
            tex.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
            self.image.texture = tex

class KlpprApp(App):

    def build(self):
        self.calib_screen = CalibScreen()

        self.service = None
        self.start_service()
        osc.init()
        oscid = osc.listen(port=3002)
        osc.bind(oscid, self.calib_screen.process_image, '/image')
        Clock.schedule_interval(lambda *x: osc.readQueue(oscid), 0)
        return self.calib_screen

    def start_service(self):
        if platform() == 'android':
            from android import AndroidService
            service = AndroidService('camera service', 'running')
            service.start('service started')
            self.service = service

    def stop_service(self):
        if self.service:
            self.service.stop()
            self.service = None

    def on_start(self):
        pass

    def on_pause(self):
        return True # avoid on_stop being called

    def on_resume(self):
        pass
    
    def on_stop(self):
        osc.sendMsg('/logout', port=3000)
        osc.dontListen()
        return

if __name__ == '__main__':
    KlpprApp().run()
