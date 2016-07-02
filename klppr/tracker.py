

"""
Subject tracker

Receives location updates from camera and subject.
Calculates distance/bearing/elevation (camera-->subject)
and controls camera pan/tilt/zoom
to keep subject centered and fitting the frame.

It uses calibrated camera (which knows true North).
"""

import logging
from math import atan, degrees
from pydispatch import dispatcher
from klppr import location

logger = logging.getLogger(__name__)


def field_of_view(size, distance):
    """
    :param size: size of subject (same unit as distance)
    :param distance: distance from subject (same unit as size)
    :return: field-of-view in degrees
    """
    if distance == 0.0:
        return 180
    else:
        return 2 * degrees(atan(size/2.0 / distance))


class Tracker(object):

    def __init__(self, camera, subject):
        self._camera = camera
        self._subject = subject
        dispatcher.connect(receiver=self.on_location_update,
                           signal='location-update',
                           sender=camera)
        dispatcher.connect(receiver=self.on_location_update,
                           signal='location-update',
                           sender=subject)

        # avoid duplicate entries
        logger.propagate = False

    def on_location_update(self):
        """
        Called on either camera or subject location update

        Re-calculates camera orientation and controls camera
        """
        bearing, elevation, fov = self.track()
        self._camera.orientation = bearing, elevation, fov

    def track(self):
        """
        Tracking function

        re-calculates camera orientation on either camera or
        subject location updates.

        :return: bearing,elevation,field-of-view tuple, in degrees
        """
        camera = self._camera.location
        subject = self._subject.location

        bearing = location.bearing(camera, subject)
        elevation = location.elevation(camera, subject)
        distance = location.distance3d(camera, subject)
        fov = field_of_view(self._subject.size, distance)

        msg = 'distance:{0:.3f} bearing:{1:.3f} elevation:{2:.3f} FOV:{3:.3f}'
        logger.debug(msg.format(distance, bearing, elevation, fov))

        return bearing, elevation, fov
