
import socket
import json
import sched
import time

import requests
from kivy.logger import Logger


class Beacon(object):
    """
    Receives location updates
    Sends datagrams
    """

    def __init__(self, location_service, dst_host='localhost', dst_port=2222):

        self.location = (None, None, None)
        self.service = location_service
        self.host = dst_host
        self.port = dst_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.service.bind(location=self.on_location)

        # TODO: update host periodically (asynchronously, using UrlRequest)
        self.update_host()

        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.periodic_send_location()
        self.scheduler.run()

    def on_location(self, instance, location):
        Logger.info('beacon location: %s' % str(location))
        self.location = location
        self.send_location(location)

    def update_host(self):
        self.host = requests.get('http://klppr.com/ip/').text

    def send_location(self, location):
        data = dict(zip(['latitude', 'longitude', 'altitude'], location))
        json_data = json.dumps(data)
        self.sock.sendto(json_data, (self.host, self.port))
        Logger.info('update sent to {}:{}'.format(self.host, self.port))

    def periodic_send_location(self):
        """
        Repeat last location in case send_location's datagram was lost
        """
        # TODO: configurable update interval
        interval = 2.0
        self.scheduler.enter(interval, 1, self.periodic_send_location, ())
        self.send_location(self.location)

