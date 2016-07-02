from math import sqrt, sin, cos, asin, atan, atan2, radians, degrees

from klppr.limit import limit_latitude, limit_longitude


'''
Calculations for geodetic locations (latitude,longitude,altitude)
'''


AVG_EARTH_RADIUS_KM = 6371.0


def distance(a, b):
    """
    Return distance in meters between Locations a and b
    """
    if not a or not b:
        return 0.0
    if not (a.valid() and b.valid()):
        return 0.0
    latlons = [a.latitude, a.longitude, b.latitude, b.longitude]
    lat1, lon1, lat2, lon2 = [radians(float(x)) for x in latlons]
    # calculate Haversine
    lat = lat2 - lat1
    lon = lon2 - lon1
    alpha = sin(lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(lon / 2) ** 2
    dist = 2 * AVG_EARTH_RADIUS_KM * 1000 * asin(sqrt(alpha))
    return dist


def distance3d(a, b):
    if not a or not b:
        return 0.0
    if not (a.valid() and b.valid()):
        return 0.0
    d = distance(a, b)
    h = b.altitude - a.altitude
    return sqrt(d*d + h*h)


def bearing(a, b):
    """
    Return bearing in degrees between Locations a and b (from a to b)
    """
    if not a or not b:
        return 0.0
    if not (a.valid() and b.valid()):
        return 0.0
    latlons = [a.latitude, a.longitude, b.latitude, b.longitude]
    lat1, lon1, lat2, lon2 = [radians(float(x)) for x in latlons]

    alpha = atan2(sin(lon2-lon1)*cos(lat2),
                  cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(lon2-lon1))
    alpha = degrees(alpha)
    alpha = (alpha + 360) % 360
    return alpha


def elevation(a, b):
    """
    Return elevation in degrees between Locations a and b (from a to b)
    """
    if not a or not b:
        return 0.0
    if not (a.valid() and b.valid()):
        return 0.0
    d = distance(a, b)
    if d == 0:
        return 0.0
    elev = atan((b.altitude - a.altitude) / d)
    return round(degrees(elev), 3)


class Location(object):

    """
    Location with geo location in degrees and altitude in meters.
    """

    def __init__(self, latitude=None, longitude=None, altitude=0):
        """
        Location object
        :param latitude: latitude in degrees
        :param longitude: longitude in degrees
        :param altitude: altitude above sea level in meters
        """
        # TODO: accuracy
        # TODO: time
        # TODO: (speed, heading, trajectory)

        # attributes
        self._latitude = None
        self._longitude = None
        self._altitude = 0.0
        # properties
        if latitude is not None:
            self.latitude = latitude
        if longitude is not None:
            self.longitude = longitude
        self.altitude = altitude

    def valid(self):
        """
        :return: True if location is valid
        """
        v = ((self.latitude is not None) and
             (self.longitude is not None) and
             (self.altitude is not None))
        return v

    def __repr__(self):
        return str((self.latitude, self.longitude, self.altitude))

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, x):
        self._latitude = limit_latitude(x)

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, x):
        self._longitude = limit_longitude(x)

    @property
    def altitude(self):
        return self._altitude

    @altitude.setter
    def altitude(self, x):
        self._altitude = x
