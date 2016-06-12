

"""
Camera subject

The subject of the tracking/recording.
It has a location (later trajectory as well)
and a size (which the camera can fit in the frame).
"""


class Subject(object):

    def __init__(self, location_provider=None, size=2.0):
        """
        :param location_provider: service with callbacks
        :param size: subject size in meters
        """
        self._location_provider = location_provider
        if location_provider:
            pass  # TODO: register to location updates

        self._size = size
        self._location = None

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, x):
        self._size = x

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, x):
        self._location = x

    def on_location_update(self):
        # TODO: update location property
        pass

