import pickle

import kivy
kivy.require('1.8.0') # replace with your current kivy version !

from kivy.lib import osc
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.logger import Logger
from kivy.properties import StringProperty


class GpsScreen(Screen):

    latlon = StringProperty()
    accuracy = StringProperty()

    def __init__(self, **kwargs):
        super(GpsScreen, self).__init__(**kwargs)

    def receive_location(self, message, *args):
        """
        Update our pan/tilt/zoom values based on camera's
        """
        loc = pickle.loads(message[2])
        Logger.info('location: %s' % loc)
        self.latlon = "%f\n%f\n%.1f" % (loc['lat'],loc['lon'],loc['altitude'])
        try:
            self.accuracy = "%.1f" % loc['accuracy']
        except:
            Logger.error("accuracy not available")
    
