#!/usr/bin/python
#
# klppr service
#

import ConfigParser

from driver import jvc
from driver.camera  import AsyncCamera
from camera import CameraService
from location import LocationService


if __name__ == '__main__':
    
    # keep sending locatin updates to UI
    loc = LocationService(tx_port=3002)

    # initialze camera
    config = ConfigParser.RawConfigParser()
    config.read('camera.cfg')

    driver = jvc.JVC(host = config.get('access', 'hostname'),
                     user = config.get('access', 'user'),
                     password = config.get('access', 'password'))
    camera = AsyncCamera(driver) 

    # start listening for commands from UI or tracker
    service = CameraService(camera, rx_port=3000, tx_port=3002)
    service.run()

