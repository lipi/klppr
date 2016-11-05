
import json

from kivy.event import EventDispatcher
from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty, NumericProperty

from kivy.clock import Clock


class LocationService(EventDispatcher):
    """
    Receive location updates from GPS.
    Store location tuple as property, to allow registering callbacks.
    """

    location = ObjectProperty()
    accuracy = NumericProperty()
    status = StringProperty()

    def __init__(self):
        try:
            from plyer import gps
            # initialize GPS
            self.gps = gps
            self.gps.configure(on_location=self.update_location,
                               on_status=self.update_status)
            self.gps.start()
        except ImportError:
            print 'GPS module is not available'
        except NotImplementedError:
            self.status = 'GPS is not implemented for your platform'
            Logger.debug(self.status)
            # fake GPS
            Clock.schedule_interval(self.check_location, 1.0)

    def check_location(self, dt):
        print('Checking location...')
        with open('location.json', 'rb') as loc_file:
            loc = json.load(loc_file)
            self.update_location(loc)

    def update_location(self, **kwargs):
        # TODO: use Location class
        self.location = (kwargs['lat'], kwargs['lon'], kwargs['altitude'])
        try:
            self.accuracy = kwargs['accuracy']
        except KeyError:
            # pre-kivy-1.9
            self.accuracy = 0
        Logger.info('location: %s %s' % (self.__class__.__name__,
                                         str(self.location)))

    def update_status(self, stype, status):
        self.status = 'type={}\n{}'.format(stype, status)
        Logger.debug(self.status)

