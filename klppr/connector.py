
import pickle

from kivy.clock import Clock
from kivy.lib import osc
from kivy.logger import Logger


class OscConnector(object):
    """
    OSC connector

    Helps connecting to a 'remote' process via OSC messages.
    It provides callback interface.
    """
    # TODO: RemoteProperty class?

    def __init__(self, rx_port, tx_port):
        self._rx_port, self._tx_port = rx_port, tx_port
        osc.init()
        self.oscid = osc.listen(port=rx_port)
        Clock.schedule_interval(lambda *x: osc.readQueue(self.oscid), 0)

    def send(self, address, data=None, typehint=None):
        Logger.info(address)
        if data is not None:
            if typehint == 'b':
                osc.sendMsg(address, [data, ], port=self._tx_port, typehint='b')
            else:
                serialized_data = pickle.dumps(data)
                osc.sendMsg(address, [serialized_data, ], port=self._tx_port)
        else:
            osc.sendMsg(address, port=self._tx_port)

    def connect(self, callback, address):
        osc.bind(self.oscid, callback, address)

    def stop(self):
        osc.dontListen()