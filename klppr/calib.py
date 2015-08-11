import pickle
import logging
from PIL import Image as PilImage
from StringIO import StringIO

import kivy
kivy.require('1.8.0') # replace with your current kivy version !

from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.properties import NumericProperty, BoundedNumericProperty
from kivy.logger import Logger
from kivy.lib import osc
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen


class CalibScreen(Screen):

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

    preview = BooleanProperty(True)
    connected = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(CalibScreen, self).__init__(**kwargs)

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
        
    def on_touch_down(self, touch):
        pos = self.image.to_widget(touch.x, touch.y)
        #self.update_pos_label(pos)
        if self.image.collide_point(*pos):
            touch.grab(self)

            if self.preview:
                osc.sendMsg('/stop_preview', port=3000)
                self.preview = False
            else:
                osc.sendMsg('/start_preview', port=3000)
                self.preview = True
            self.update_status_label(self.connected, self.preview)
            # touch is handled, discard it
            return True
        
        # touch doesn't belong to us, bubble it up
        return super(CalibScreen, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        #self.remove_widget(self.label)
        pass

    def update_status_label(self, connected,  preview):
        text = ''
        if not connected:
            text += 'Waiting for camera...\n'
        if not preview:
            text += 'Preview paused, touch to continue'
        self.status_label.text = text

    def update_pos_label(self, pos = None):
        if self.image.collide_point(*pos):
            label = self.pos_label
            center = self.image.center
            centered_pos = (pos[0] - center[0], pos[1] - center[1])  #touch.pos
            label.text =  '(%d, %d)' % centered_pos
            label.texture_update()
            label.pos = centered_pos
        else:
            self.pos_label.text = ''
            
            

    #
    # OSC callbacks
    #
    def receive_jpg(self, message, *args):
        '''
        Receive preview image and blit it to the preview surface.
        '''
        try:
            jpg = message[2]
        except Exception as ex:
            logging.debug('receive_jpg: {0}'. format(ex))
            return

        self.connected = True
        self.update_status_label(self.connected, self.preview)

        img = PilImage.open(StringIO(jpg))
        # not clear why (standard?), but the image is upside down
        img = img.transpose(PilImage.FLIP_TOP_BOTTOM)

        # image buffer is RGB, convert it to RGBA (Nexus 4 can't blit RGB),
        # see https://github.com/kivy/kivy/issues/1600
        #img = PilImage.fromstring('RGB', self.imgsize, self.imgbuf)
        img.putalpha(255)
        buf = img.tostring()
        tex = Texture.create(size=img.size, colorfmt='rgba')
        tex.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        self.image.texture = tex
        self.image.allow_stretch = True
            
    def receive_ptz(self, message, *args):
        '''
        Update our pan/tilt/zoom values based on camera's
        '''
        self.pan,self.tilt,self.zoom = pickle.loads(message[2])
        Logger.info('ptz: %d,%d,%d' % (self.pan,self.tilt,self.zoom))