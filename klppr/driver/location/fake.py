
import time
import logging

import jsonpickle
from pydispatch import dispatcher

from klppr.location import Location

logger = logging.getLogger(__name__)


class FakeLocationProvider(object):
    """
    Read fake location from file, in JSON format
    """

    def __init__(self, filename='location.json'):
        self._filename = filename
        self.location = Location()

    def process(self):
        text = ''
        try:
            with open(self._filename, 'rb') as f:
                text = f.read()
                self.location = jsonpickle.decode(text)
                dispatcher.send(signal='location-update',
                                location=self.location,
                                sender=self)
        except IOError:

            logger.error("Can't open {file}".
                          format(file=self._filename))
        except ValueError:
            logger.error("Not valid JSON: '{data}'".
                          format(data=text))
            time.sleep(5)
