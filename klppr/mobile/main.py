
import socket
import json

from kivy.lang import Builder
from kivy.app import App
from kivy.properties import StringProperty
from kivy.clock import mainthread
from kivy.logger import Logger

from plyer import gps


kv = '''
BoxLayout:
    orientation: 'vertical'

    Label:
        text: app.gps_location

    Label:
        text: app.gps_status
'''

HOST, PORT = '192.168.3.15', 9999


def translate(kwargs):
    mapping = {'alt': 'altitude',
               'lat': 'latitude',
               'lon': 'longitude'}
    for short, long in mapping.iteritems():
        if short in kwargs.keys():
            value = kwargs.pop(short)
            kwargs[long] = value
    return kwargs


class GpsTest(App):

    gps_location = StringProperty('No location')
    gps_status = StringProperty()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def build(self):
        self.gps = gps
        try:
            self.gps.configure(on_location=self.on_location,
                               on_status=self.on_status)
            self.gps.start()
        except NotImplementedError:
            import traceback; traceback.print_exc()
            self.gps_status = 'GPS is not implemented for your platform'

        return Builder.load_string(kv)

    @mainthread
    def on_location(self, **kwargs):
        self.gps_location = '\n'.join([
            '{}={}'.format(k, v) for k, v in kwargs.items()])
        self.send_update(**kwargs)

    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)

    def on_pause(self):
        Logger.info('pause')
        return True  # avoid on_stop being called

    def on_resume(self):
        Logger.info('resume')
        self.connector.send('/start_preview')
        pass

    def on_stop(self):
        Logger.info('stop')
        return

    def send_update(self, latitude=0.0, longitude=0.0, altitude=0.0, **kwargs):
        location = {'latitude': latitude, 'longitude': longitude, 'altitude': altitude}
        data = json.dumps(location)
        print('data:' + data)
        self.sock.sendto(data + "\n", (HOST, PORT))

if __name__ == '__main__':
    GpsTest().run()