
import kivy
kivy.require('1.8.0') # replace with your current kivy version !

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

class GpsScreen(Screen):

    def __init__(self, **kwargs):
        super(GpsScreen, self).__init__(**kwargs)

