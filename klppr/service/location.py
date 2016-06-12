
from kivy.event import EventDispatcher
from kivy.logger import Logger
from kivy.properties import ObjectProperty,StringProperty,NumericProperty


# needs gps_improvements branch to get location accuracy reports
# see https://github.com/lipi/plyer/tree/gps_improvements
try:
    from plyer import gps
except ImportError:
    print 'GPS module is not available'

from klppr.location import Location


class LocationService(EventDispatcher):
    """
    Receive location updates.
    Store location as property, to allow registering callbacks.
    """

    gps_location = ObjectProperty()
    gps_accuracy = NumericProperty()
    gps_status = StringProperty()

    def __init__(self):
        try:
            # initialize GPS
            self.gps = gps
            self.gps.configure(on_location=self.on_location,
                               on_status=self.on_status)
            self.gps.start()
        except NotImplementedError:
            self.gps_status = 'GPS is not implemented for your platform'
            Logger.debug(self.gps_status)

    def on_location(self, **kwargs):
        # TODO: duplicate calls -- check providers in plyer/android/gps
        self.gps_location = Location(kwargs['lat'],
                                     kwargs['lon'],
                                     kwargs['altitude'])
        try:
            self.gps_accuracy = kwargs['accuracy']
        except KeyError:
            self.gps_accuracy = 0
        Logger.debug('location: %s' % self.gps_location)

    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)
        Logger.debug(self.gps_status)


class LocationServiceOsc(LocationService):
    """
    LocationService with OSC interface
    """
    def __init__(self, connector, **kwargs):
        super(LocationServiceOsc, self).__init__(**kwargs)
        self.connector = connector

    def on_location(self, **kwargs):
        super(LocationServiceOsc, self).on_location(**kwargs)
        loc = self.gps_location
        self.connector.send('/location', (loc.lat, loc.lon, loc.alt))
        self.connector.send('/accuracy', self.gps_accuracy)
