import kivy
kivy.require('1.8.0') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, NumericProperty

import jvc

class CalibScreen(BoxLayout):

    camera = ObjectProperty()
    filename = StringProperty('current.jpg')
    image = ObjectProperty()

    # TODO: get initial values from camera
    pan = NumericProperty(0)
    tilt = NumericProperty(0)
    zoom = NumericProperty(10)

    pan_speed = NumericProperty(1)
    tilt_speed = NumericProperty(1)
    zoom_speed = NumericProperty(1)

    def __init__(self, **kwargs):
        super(CalibScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.clock_callback, 0.5)

    #
    # Camera control
    #

    def up(self):
        print 'up...',
        self.tilt += self.tilt_speed
        self.pantilt()
        print 'done'

    def down(self):
        print 'down...'
        self.tilt -= self.tilt_speed
        self.pantilt()
        print 'done'

    def left(self):
        print 'left...',
        self.pan -= self.pan_speed
        self.pantilt()
        print 'done'

    def right(self):
        print 'right...'
        self.pan += self.pan_speed
        self.pantilt()
        print 'done.'

    def zoom_in(self):
        print 'zoom in...'
        self.zoom += self.zoom_speed
        self.camera.zoom(self.zoom, self.zoom_speed)
        print 'done'

    def zoom_out(self):
        print 'zoom out...'
        self.zoom -= self.zoom_speed
        self.camera.zoom(self.zoom, self.zoom_speed)
        print 'done'

    def pantilt(self):
        self.camera.pantilt(self.pan, self.tilt)
        return

    def clock_callback(self, dt):
        try:
            img = self.camera.getjpg()
            self.camera.savejpg(img, self.filename)
            self.image.reload()
        except Exception as ex:
            print ex          

class TestApp(App):

    #
    # Kivy
    #

    def on_start(self):
        print 'start...'
        self.jvc = jvc.JVC('192.168.3.114')
        self.jvc.login()
        self.calib_screen.camera = self.jvc
        print 'started.'

    
    def build(self):
        print 'building...'
        self.calib_screen = CalibScreen()
        return self.calib_screen


    def on_stop(self):
        self.jvc.logout()
        return

if __name__ == '__main__':
    TestApp().run()
