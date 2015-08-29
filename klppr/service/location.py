
import pickle

from kivy.lib import osc
from kivy.clock import Clock

# needs gps_improvements branch to get location accuracy reports
from plyer import gps

class LocationService(object):
    """
    Send location updates 
    Works over OSC.
    """

    def __init__(self, tx_port):

        # initialize GPS
        self.gps = gps
        
        try:
            self.gps.configure(on_location=self.on_location,
                    on_status=self.on_status)
            self.gps.start()
            
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            self.gps_status = 'GPS is not implemented for your platform'
            print self.gps_status

        # using OSC as Android doesn't support POSIX-style IPC
        osc.init()
        self.tx_port = tx_port

    def on_location(self, **kwargs):
        # TODO: duplicate calls -- check providers in plyer/android/gps
        osc.sendMsg('/location', [pickle.dumps(kwargs), ],
                    port=self.tx_port)

    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)
        print self.gps_status
