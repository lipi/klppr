"""
Ideal camera

It can look in the required direction with the required field-of-view,
based on its true heading (relative to North).

True heading can be set by calibration.

It controls a PTZ camera (Pan-Tilt-Zoom). Receives location updates.
"""

import logging
from pydispatch import dispatcher
from limit import limit_pan
from klppr.driver.camera.asynccam import AsyncCamera


class Camera(AsyncCamera):

    def __init__(self, location_provider=None, **kwargs):
        """
        :param ptz_camera: pan-tilt-zoom camera
        :param location_provider: service with callbacks
        """
        super(Camera, self).__init__(**kwargs)
        self._location_provider = location_provider
        if location_provider:
            dispatcher.connect(receiver=self.on_location_update,
                               signal='location-update',
                               sender=location_provider)
        self._true_heading = .0
        self._orientation = (.0, .0, 180.)
        self._location = None

    @property
    def true_heading(self):
        return self._true_heading

    @true_heading.setter
    def true_heading(self, heading):
        self._true_heading = limit_pan(heading)

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, x):
        self._location = x

    def on_location_update(self, location):
        self.location = location
        logging.debug('camera location: {loc}'.format(loc=location))
        dispatcher.send(signal='location-update',
                        location=self.location,
                        sender=self)

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, x):
        """
        Set the actual camera pan/tilt/zoom values based on
        the required bearing/elevation/field-of-view

        :param bearing: bearing to the subject, degrees
        :param elevation: elevation to the subject, degrees
        :param field_of_view: required field-of-view, degrees
        """
        bearing, elevation, field_of_view = x
        self._orientation = bearing, elevation, field_of_view

        pan = bearing - self.true_heading
        tilt = elevation
        zoom = self.field_of_view / field_of_view

        self.ptz(pan, tilt, zoom)
