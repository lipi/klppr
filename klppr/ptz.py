
"""
Pan-Tilt-Zoom value handling
"""

from klppr.limit import *


def limit_zoom(x):
    """"
    Limit zoom to 1.0 .. 10.0 range
    """
    # TODO: limit to camera's actual range?
    return clamp(x, 1, 10)


class PTZ(object):
    """
    Pan-Tilt-Zoom

    Holds values in degrees.
    Values are sanitized when set:
    - pan in the -180..180 range
    - tilt in the -90..90 range
    - zoom in the 1..10 range

    >>> PTZ()
    (0, 0, 1)
    >>> PTZ(181, -91, 11)
    (-179, -90, 10)
    """

    def __init__(self, pan=0, tilt=0, zoom=0):
        # attributes
        self._pan = 0
        self._tilt = 0
        self._zoom = 0
        # properties
        self.pan = pan
        self.tilt = tilt
        self.zoom = zoom

    def __repr__(self):
        return str((self.pan, self.tilt, self.zoom))

    @property
    def pan(self):
        return self._pan

    @pan.setter
    def pan(self, x):
        # forcing float point arithmetic when used later on
        self._pan = limit_pan(x)

    @property
    def tilt(self):
        return self._tilt

    @tilt.setter
    def tilt(self, x):
        # forcing float point arithmetic when used later on
        self._tilt = limit_tilt(x)

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, x):
        self._zoom = limit_zoom(x)

if __name__ == "__main__":
    import doctest
    doctest.testmod()