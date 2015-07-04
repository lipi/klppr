#!/usr/bin/python
#
# klppr service
#

from time import sleep
import ConfigParser
import pickle

from kivy.lib import osc

import jvc
from camera  import AsyncCamera

class CameraService(object):

    def __init__(self, camera):
        self.camera = camera

        osc.init()
        self._oscid = osc.listen(port=3000)
        osc.bind(self._oscid, self._pantilt, '/pantilt')
        osc.bind(self._oscid, self._zoom, '/zoom')
        osc.bind(self._oscid, self._logout, '/logout')
        osc.bind(self._oscid, self._stop_preview, '/stop_preview')
        osc.bind(self._oscid, self._start_preview, '/start_preview')

        # notify UI of current PTZ state
        osc.sendMsg('/ptz', [pickle.dumps(camera.ptz()),], port=3002)

    def _pantilt(self, message, *args):
        pan,tilt = pickle.loads(message[2]) 
        self.camera.pantilt(pan,tilt)

    def _zoom(self, message, *args):
        level,speed = pickle.loads(message[2])
        self.camera.zoom(level,speed)

    def _logout(self, *args):
        self.camera.close()
        osc.dontListen()
        exit()

    def _stop_preview(self, *args):
        self.camera.stop_preview()

    def _start_preview(self, *args):
        self.camera.start_preview()

    def run(self):
        while True:
            # process incoming commands
            try:
                osc.readQueue(self._oscid)
            except KeyError:
                return

            # send preview update
            jpg = camera.getjpg()
            if jpg is not None:
                # NOTE: OSC is UDP based, therefore jpg must be 64k or less
                # (otherwise it must be split to multiple transfers)
                # Also note that the OS might drop UDP packets if its
                # receive buffers are small (can be increased in OSCServer by 
                # using setsockopt).
                osc.sendMsg('/jpg', [jpg,], port=3002, typehint='b')

if __name__ == '__main__':
    
    # initialze camera
    config = ConfigParser.RawConfigParser()
    config.read('camera.cfg')

    driver = jvc.JVC(host = config.get('access', 'hostname'),
                     user = config.get('access', 'user'),
                     password = config.get('access', 'password'))
    camera = AsyncCamera(driver) 

    # start listening for commands from UI or tracker
    service = CameraService(camera)
    service.run()


