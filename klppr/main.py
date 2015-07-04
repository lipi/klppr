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
from PIL import Image as PilImage
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty, StringProperty
from kivy.properties import NumericProperty, BoundedNumericProperty
from kivy.logger import Logger
from kivy.lib import osc
from kivy.utils import platform
from kivy.clock import Clock

def numbytes(imgsize):
    return imgsize[0] * imgsize[1] * 3

class CalibScreen(BoxLayout):

    image = ObjectProperty()

    # TODO: use camera-specific values instead of hardcoded ones
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
        self.imgbuf = ''

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
    # OSC callbacks
    #
    def receive_image(self, message, *args):
        '''
        Receive preview image chunks and update image once all chunks have
        been received.
        '''
        try:
            data = message[2]
            chunk_id = ord(data[0])
            self.imgbuf += data[1:]
        except Exception as ex:
            #print ex
            return

        if numbytes(self.imgsize) == len(self.imgbuf):
            # image buffer is RGB, convert it to RGBA (Nexus 4 can't blit RGB),
            # see https://github.com/kivy/kivy/issues/1600
            img = PilImage.fromstring('RGB', self.imgsize, self.imgbuf)
            img.putalpha(255)
            buf = img.tostring()
            tex = Texture.create(size=self.imgsize, colorfmt='rgba')
            tex.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
            self.image.texture = tex
            

    def receive_imagesize(self, message, *args):
        '''
        CameraService sends /imagesize before each frame.
        Use it to reset image buffer content.
        '''
        self.imgsize = pickle.loads(message[2])
        if numbytes(self.imgsize) != len(self.imgbuf):
            Logger.warning('image buffer size: %d' % len(self.imgbuf))
            pass
        self.imgbuf = ''

    def receive_ptz(self, message, *args):
        '''
        Update our pan/tilt/zoom values based on camera's
        '''
        self.pan,self.tilt,self.zoom = pickle.loads(message[2])

class KlpprApp(App):

    def build(self):
        self.calib_screen = CalibScreen()

        self.service = None
        self.start_service()
        osc.init()
        oscid = osc.listen(port=3002)
        osc.bind(oscid, self.calib_screen.receive_image, '/image')
        osc.bind(oscid, self.calib_screen.receive_imagesize, '/imagesize')
        osc.bind(oscid, self.calib_screen.receive_ptz, '/ptz')
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
        osc.sendMsg('/start_preview', port=3000)
        pass

    def on_pause(self):
        # avoid unnecessary traffic (image download)
        osc.sendMsg('/stop_preview', port=3000)
        return True # avoid on_stop being called

    def on_resume(self):
        osc.sendMsg('/start_preview', port=3000)
        pass
    
    def on_stop(self):
        osc.sendMsg('/logout', port=3000)
        osc.dontListen()
        return

if __name__ == '__main__':
    KlpprApp().run()
