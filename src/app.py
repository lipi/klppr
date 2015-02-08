import kivy
kivy.require('1.8.0') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image

import jvc

class TestApp(App):

    def left(self, instance):
        print 'left...',
        self.jvc.pantilt(0,0)
        print 'done'

    def right(self, instance):
        print 'right...'
        self.jvc.pantilt(100,0)
        print 'done.'

    def reload(self, instance):
        img = self.jvc.getjpg()
        self.jvc.savejpg(img, 'x.jpg')
        self.image.reload()

    def on_start(self):
        self.jvc = jvc.JVC('192.168.3.106')
        self.jvc.login()
    
    def build(self):
        layout = GridLayout(cols=3)
        left_button = Button(size_hint=(None, None),
                             text='left', on_press=self.left)
        right_button = Button(size_hint=(None, None),
                              text='right', on_press=self.right)
        reload_button = Button(size_hint=(None, None),
                               text='reload', on_press=self.reload)
        layout.add_widget(left_button, )
        layout.add_widget(right_button)
        layout.add_widget(reload_button)

        image = Image(source='x.jpg')
        self.image = image
        layout.add_widget(image)

        return layout

    def on_stop(self):
        self.jvc.logout()

if __name__ == '__main__':
    TestApp().run()
