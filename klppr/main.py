#!/usr/bin/python
#
# klppr app
# 

import kivy
kivy.require('1.8.0') # replace with your current kivy version !

from kivy.app import App
from kivy.lib import osc
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen

from gps import GpsScreen
from calib import CalibScreen

rx_port = 3002
tx_port = 3000

def send(msg):
    osc.sendMsg(msg, port=tx_port)

class KlpprApp(App):

    def build(self):
        self.gps_screen = GpsScreen(name='gps')
        self.calib_screen = CalibScreen(name='calib')

        # create the screen manager
        sm = ScreenManager()
        sm.add_widget(self.gps_screen)
        sm.add_widget(self.calib_screen)

        # interprocess comms
        osc.init()
        oscid = osc.listen(port=rx_port)
        osc.bind(oscid, self.calib_screen.receive_jpg, '/jpg')
        osc.bind(oscid, self.calib_screen.receive_ptz, '/ptz')
        osc.bind(oscid, self.gps_screen.receive_location, '/location')
        Clock.schedule_interval(lambda *x: osc.readQueue(oscid), 0)

        # start service (Android only)
        self.service = None
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
        send('/start_preview')
        send('/get_ptz')
        pass

    def on_pause(self):
        # avoid unnecessary traffic (image download)
        send('/stop_preview')
        return True # avoid on_stop being called

    def on_resume(self):
        send('/start_preview')
        pass
    
    def on_stop(self):
        send('/logout')
        osc.dontListen()
        return

if __name__ == '__main__':
    KlpprApp().run()
