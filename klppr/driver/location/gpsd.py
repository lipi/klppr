
import logging

# NOTE: gps3 uses Thread(daemon=True) which does not work in Python 2.7
# FIX: modify gps3 source or use Python 3
from gps3.agps3threaded import AGPS3mechanism, GPSD_PORT
from pydispatch import dispatcher

from klppr.location import Location, distance

logger = logging.getLogger(__name__)

DISTANCE_THRESHOLD = .5  # meters

class GpsdLocationProvider(object):
    """
    Read location from GPSD

    Listen to GPSD data and send a location-update when location changes.
    TODO: use notification instead of polling
    """

    def __init__(self, host='localhost', port=GPSD_PORT):
        self.location = Location()

        self._agps_thread = AGPS3mechanism()
        self._agps_thread.stream_data(host=host, port=port)
        self._agps_thread.run_thread()

    def process(self):
        """
        Poll GPSD data and send update
        """
        data = self._agps_thread.data_stream
        current_location = Location(data.lat, data.lon, data.alt)
        logger.info("GPSD location: %s" % current_location)
        if (not self.location.valid() or
            distance(current_location, self.location) > DISTANCE_THRESHOLD):
            self.location = current_location
            dispatcher.send(signal='location-update',
                            location=self.location,
                            sender=self)
