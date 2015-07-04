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
            img = camera.getimg()
            if img is not None:
                osc.sendMsg('/imagesize', [pickle.dumps(img.size),], port=3002)
                buf = img.tostring()
                chunk_size = 60000 # UDP limitation: 64K
                # TODO: increase UDP buffer sizes in OSC to avoid chunk loss
                chunk_id = 0
                for offset in range(0, len(buf), chunk_size):
                    data = chr(chunk_id) + buf[offset:offset+chunk_size]
                    #data = chr(chunk_id) * chunk_size
                    chunk_id += 1
                    osc.sendMsg('/image', [data,], port=3002, typehint='b')

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


