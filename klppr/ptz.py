
def limit_pan(x):
    """
    Limit pan to -180..180 range, with wrap-around

    >>> limit_pan(181)
    -179
    >>> limit_pan(180)
    180
    >>> limit_pan(-181)
    179
    >>> limit_pan(360)
    0
    >>> limit_pan(540)
    180
    """

    # TODO: limit to camera's actual range?
    if (x % 360) == 180:
        return 180
    return ((x + 180) % 360) - 180


def limit_tilt(x):
    """
    Limit tilt to -90..90 range, without wrap-around

    >>> limit_tilt(91)
    90
    >>> limit_tilt(90)
    90
    >>> limit_tilt(-91)
    -90
    >>> limit_tilt(360)
    90
    >>> limit_tilt(-540)
    -90
    """

    # TODO: limit to camera's actual range?
    # TODO: consider using numpy.clip() instead
    return clamp(x, -90, 90)


def limit_zoom(x):
    """"
    Limit zoom to 1.0 .. 10.0 range
    """
    # TODO: limit to camera's actual range?
    return clamp(x, 1, 10)


def clamp(x, x_min, x_max):
    return min(x_max, max(x, x_min))


class PTZ(object):
    """
    Pan-Tilt-Zoom

    Holds values in degrees.
    Values are sanitized when set:
    - pan in the -180..180 range
    - tilt in the -90..90 range
    - zoom in the 1..10 range

    >>> PTZ()
    (0.0, 0.0, 1.0)
    >>> PTZ(181, -91, 11)
    (-179.0, -90.0, 10.0)
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
        x = limit_pan(x)
        # forcing float point arithmetic when used later on
        self._pan = float(x)

    @property
    def tilt(self):
        return self._tilt

    @tilt.setter
    def tilt(self, x):
        x = limit_tilt(x)
        # forcing float point arithmetic when used later on
        self._tilt = float(x)

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, x):
        x = limit_zoom(x)
        self._zoom = float(x)

if __name__ == "__main__":
    import doctest
    doctest.testmod()