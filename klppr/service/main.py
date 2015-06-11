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

    def run(self):
        while True:
            # process incoming commands
            osc.readQueue(self._oscid)

            # send preview update
            img = camera.getimg()
            if img is not None:
                osc.sendMsg('/imagesize', [pickle.dumps(img.size),], port=3002)
                buf = img.tostring()
                chunk_size = 60000 # UDP limitation: 64K
                # TODO: some chunks seem to get lost, use some other form of IPC
                # (OSC uses UDP)
                for offset in range(0, len(buf), chunk_size):
                    data = buf[offset:offset+chunk_size]
                    osc.sendMsg('/image', [data,], port=3002, typehint='b')

if __name__ == '__main__':
    
    # initialze camera
    config = ConfigParser.RawConfigParser()
    config.read('camera.cfg')

    driver = jvc.JVC(host = config.get('access', 'hostname'),
                     user = config.get('access', 'user'),
                     password = config.get('access', 'password'))
    camera = AsyncCamera(driver) 

    # start listening 
    service = CameraService(camera)
    service.run()


