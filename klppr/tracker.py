

"""
Subject tracker

Receives location updates from camera and subject.
Calculates distance/bearing/elevation (camera-->subject)
and controls camera pan/tilt/zoom
to keep subject centered and fit into the frame.

It uses calibrated camera (which knows true North).
"""

from math import atan, degrees
from klppr import location


def field_of_view(size, distance):
    if distance == 0.0:
        return 180
    else:
        return 2 * degrees(atan(size/2.0 / distance))


class Tracker(object):

    def __init__(self, camera, subject):
        self._camera = camera
        self._subject = subject

        # TODO: subscribe to location updates
        # camera...
        # subject...

    def on_location_update(self):
        bearing, elevation, fov = self.track()
        self._camera.orentation(bearing, elevation, fov)

    def track(self):
        camera = self._camera.location()
        subject = self._subject.location()
        bearing = location.bearing(camera, subject)
        elevation = location.elevation(camera, subject)
        distance = location.distance(camera, subject)
        fov = field_of_view(self._subject.size, distance)
        return bearing, elevation, fov

