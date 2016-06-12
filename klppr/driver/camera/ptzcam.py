
"""
Pan-Tilt-Zoom Camera

It knows the camera's field-of-view (at zoom=1).
Pan/tilt/zoom values can be set.
"""


class PtzCamera(object):

    def __init__(self, field_of_view):
        """
        :param field_of_view: field-of-view at zoom=1, in degrees
        """
        self._field_of_view = field_of_view
        self._pan = None
        self._tilt = None
        self._zoom = None

    @property
    def field_of_view(self):
        return self._field_of_view

    @field_of_view.setter
    def field_of_view(self, fov):
        assert fov <= 180  # sanity check
        self._field_of_view = fov

    def ptz(self, pan, tilt, zoom):
        """
        Set Pan-Tilt-Zoom of camera. To be overridden.
        :param pan: in degrees
        :param tilt: in degrees
        :param zoom: from 1.0 upward
        :return:
        """
        self._pan = pan
        self._tilt = tilt
        self._zoom = zoom

