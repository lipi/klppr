#!/usr/bin/python
#
# klppr service
#

import ConfigParser

from driver import jvc
from driver.camera  import AsyncCamera
from camera import CameraService

if __name__ == '__main__':
    
    # initialze camera
    config = ConfigParser.RawConfigParser()
    config.read('camera.cfg')
    print config.get('access', 'hostname')

    driver = jvc.JVC(host = config.get('access', 'hostname'),
                     user = config.get('access', 'user'),
                     password = config.get('access', 'password'))
    camera = AsyncCamera(driver) 

    # start listening for commands from UI or tracker
    service = CameraService(camera)
    service.run()

