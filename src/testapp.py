import kivy
kivy.require('1.8.0') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock

import jvc

class TestApp(App):

    #
    # Camera control
    #

    def up(self, instance):
        print 'up...',
        self.tilt += self.tilt_speed
        self.pantilt()
        print 'done'

    def down(self, instance):
        print 'down...'
        self.tilt -= self.tilt_speed
        self.pantilt()
        print 'done'

    def left(self, instance):
        print 'left...',
        self.pan -= self.pan_speed
        self.pantilt()
        print 'done'

    def right(self, instance):
        print 'right...'
        self.pan += self.pan_speed
        self.pantilt()
        print 'done.'

    def pantilt(self):
        self.jvc.pantilt(self.pan, self.tilt)

    def clock_callback(self, dt):
        img = self.jvc.getjpg()
        self.jvc.savejpg(img, self.filename)
        self.image.reload()

    #
    # Kivy
    #

    def on_start(self):
        self.jvc = jvc.JVC('192.168.3.114')
        self.jvc.login()

        self.pan = 0
        self.tilt = 0
        self.pan_speed = 1
        self.tilt_speed = 1
    
    def build(self):

        control_layout = GridLayout(cols=3, rows=3)
        left_button = Button(size_hint=(None, None),
                             text='left', on_press=self.left)
        right_button = Button(size_hint=(None, None),
                              text='right', on_press=self.right)
        up_button = Button(size_hint=(None, None),
                               text='up', on_press=self.up)
        down_button = Button(size_hint=(None, None),
                               text='down', on_press=self.down)

        # first row
        control_layout.add_widget(Label()) # dummy
        control_layout.add_widget(up_button)
        control_layout.add_widget(Label()) # dummy
        # second row
        control_layout.add_widget(left_button)
        control_layout.add_widget(Label()) # dummy
        control_layout.add_widget(right_button)
        # third row
        control_layout.add_widget(Label()) # dummy
        control_layout.add_widget(down_button)
        control_layout.add_widget(Label()) # dummy

        status_layout = BoxLayout(orientation='vertical')
        self.filename = 'current.jpg'
        image = Image(source=self.filename)
        self.image = image
        status_layout.add_widget(image)

        top_layout = BoxLayout(orientation='vertical')
        top_layout.add_widget(control_layout)
        top_layout.add_widget(status_layout)

        Clock.schedule_interval(self.clock_callback, 0.5)

        return top_layout

    def on_stop(self):
        self.jvc.logout()

if __name__ == '__main__':
    TestApp().run()
