#!/usr/bin/python
#
# klppr service
#

import ConfigParser
import time

from kivy.lib import osc

from connector import OscConnector
from driver import jvc
from driver.camera import AsyncCamera
from camera import CameraServiceOsc
from location import LocationServiceOsc
from calib import CalibrationServiceOsc
from tracker import Tracker


if __name__ == '__main__':

    # using OSC as POSIX-style IPC is not supported on Android
    connector = OscConnector(rx_port=3000, tx_port=3002)

    # keep sending location updates to UI and tracker
    loc_service = LocationServiceOsc(connector)

    # initialize camera
    config = ConfigParser.RawConfigParser()
    config.read('camera.cfg')
    driver = jvc.JVC(host=config.get('access', 'hostname'),
                     user=config.get('access', 'user'),
                     password=config.get('access', 'password'))
    camera_driver = AsyncCamera(driver)

    # receive camera commands from UI or tracker
    cam_service = CameraServiceOsc(camera=camera_driver, connector=connector)

    cal_service = CalibrationServiceOsc(connector, loc_service, cam_service)

    # receive location and calibration updates, send camera commands
    tracker = Tracker(loc_service, None, cam_service)

    while True:
        try:
            osc.readQueue(connector.oscid)
        except KeyError:
            # got here due to osc.dontListen() in CameraService.logout()
            # exit the service
            exit()

        cam_service.process()
        # TODO: periodic callback
        time.sleep(.001)  # avoid 100% CPU load


