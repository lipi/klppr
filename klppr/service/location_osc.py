
from connector import OscConnector


class LocationOsc(object):
    """
    Location updates via OSC

    To be run as a service, updates consumed by the app
    """
    def __init__(self, location_service):
        """
        :param location_service: has location ObjectProperty
        """
        self.connector = OscConnector(rx_port=3000, tx_port=3002)
        location_service.bind(location=self.on_location)

    def on_location(self, instance, location):
        self.connector.send('/location', location)

    def on_accuracy(self, instance, accuracy):
        self.connector.send('/accuracy', accuracy)
