#!/usr/bin/python

"""
klppr service

Sends location updates via UDP (Beacon) to the camera
Sends location updates via OSC (LocationOsc) to the app
"""

import time

from location import LocationService
from location_osc import LocationOsc
from beacon import Beacon


if __name__ == '__main__':

    location_service = LocationService()
    beacon = Beacon(location_service, '100.101.113.164', 2222)
    location_osc = LocationOsc(location_service)

    # let Beacon and LocationOsc do their thing
    while True:
        time.sleep(1)
