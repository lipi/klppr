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
    return clamp(x, -90, 90)

def limit_latitude(x):
    """
    Limit latitude
    :param x:
    :return:
    """
    return limit_tilt(x)

def clamp(x, x_min, x_max):
    """
    Clamp x to the x_min..x_max range.
    :param x:
    :param x_min:
    :param x_max:
    :return:
    """
    return min(x_max, max(x, x_min))


if __name__ == "__main__":
    import doctest
    doctest.testmod()

