"""
Ideal camera

It can look in the required direction with the required field-of-view,
based on its true heading (relative to North).

True heading can be set by calibration.

It controls a PTZ camera (Pan-Tilt-Zoom). Receives location updates.
"""

from limit import limit_pan


class Camera(object):

    def __init__(self, ptz_camera, location_provider=None):
        """
        :param ptz_camera: pan-tilt-zoom camera
        :param location_provider: service with callbacks
        """
        self._camera = ptz_camera
        self._location_provider = location_provider
        if location_provider:
            pass  # TODO: subscribe to location updates
        self._true_heading = None
        self._orientation = None
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

    def on_location_update(self):
        # TODO: update location property
        pass

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, bearing, elevation, field_of_view):
        """
        Set the actual camera pan/tilt/zoom values based on
        the required bearing/elevation/field-of-view

        :param bearing: bearing to the subject, degrees
        :param elevation: elevation to the subject, degrees
        :param field_of_view: required field-of-view, degrees
        """
        self._orientation = bearing, elevation, field_of_view

        pan = bearing - self.true_heading
        tilt = elevation
        zoom = self._camera.field_of_view / field_of_view

        self._camera.ptz(pan, tilt, zoom)
