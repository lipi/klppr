import SocketServer
import threading
import logging
import json

from pydispatch import dispatcher
from hexdump import hexdump

from klppr.location import Location

logger = logging.getLogger(__name__)


class UdpHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        print('data:{0}'.format(data))
        try:
            json_location = json.loads(data)
            logger.debug('{0} sent {1}'.format(self.client_address[0],
                                               data))
            location = Location(**json_location)
            print 'location:', location
            dispatcher.send(signal='location-update',
                            location=location,
                            sender=self)
        except ValueError:
            logger.debug('{0} sent incorrect JSON: {1}'.
                         format(self.client_address[0],
                         hexdump(data)))


class UdpLocationProvider(object):
    """
    Sends location updates based on JSON data received on UDP
    """

    def __init__(self, host, port):

        # avoid duplicate entries
        logger.propagate = False

        self.location = Location()
        self.host = host
        self.port = port
        server = SocketServer.UDPServer((self.host, self.port), UdpHandler)

        dispatcher.connect(receiver=self.on_location_update,
                           signal='location-update',
                           sender=server)

        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        logger.info('creating UDP location thread')
        server_thread.start()

    def on_location_update(self, location):
        self.location = location
        dispatcher.send(signal='location-update',
                        location=self.location,
                        sender=self)

