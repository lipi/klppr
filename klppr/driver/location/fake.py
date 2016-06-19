
import time
import logging

import jsonpickle
from pydispatch import dispatcher

from klppr.location import Location

logging.basicConfig(level=logging.DEBUG)


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

            logging.error("Can't open {file}".
                          format(file=self._filename))
        except ValueError:
            logging.error("Not valid JSON: '{data}'".
                          format(data=text))
            time.sleep(5)
