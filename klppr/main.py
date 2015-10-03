#!/usr/bin/python
#
# klppr app
# 

import kivy
kivy.require('1.8.0') # replace with your current kivy version !

from kivy.app import App
from screen import CameraScreen, GpsScreen, RecordScreen
from kivy.lib import osc
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager

from connector import OscConnector

rx_port = 3002
tx_port = 3000


class KlpprApp(App):

    connector = None
    gps_screen = None
    calib_screen = None
    record_screen = None
    service = None

    def build(self):
        # interprocess comms
        self.connector = OscConnector(rx_port, tx_port)

        self.gps_screen = GpsScreen(self.connector, name='gps')
        self.calib_screen = CameraScreen(self.connector, name='calib')
        self.record_screen = RecordScreen(self.connector, name='record')

        # create the screen manager
        sm = ScreenManager()
        sm.add_widget(self.gps_screen)
        sm.add_widget(self.calib_screen)
        sm.add_widget(self.record_screen)

        # start service (Android only)
        self.start_service()

        return sm

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
        self.connector.send('/start_preview')
        self.connector.send('/get_ptz')
        pass

    def on_pause(self):
        # avoid unnecessary traffic (image download)
        self.connector.send('/stop_preview')
        return True # avoid on_stop being called

    def on_resume(self):
        self.connector.send('/start_preview')
        pass
    
    def on_stop(self):
        self.connector.send('/logout')
        self.connector.stop()
        return

if __name__ == '__main__':
    KlpprApp().run()
