import ConfigParser
import time

from klppr.driver.camera.jvc import JVC
from klppr.driver.location.fake import FakeLocationProvider
from klppr.driver.location.gpsd import GpsdLocationProvider
from klppr.driver.location.udp import UdpLocationProvider
from klppr.camera import Camera
from klppr.subject import Subject
from klppr.tracker import Tracker


def run():

    import logging.config
    logging.config.fileConfig('logging.conf',
                              disable_existing_loggers=False)

    # change camera location via editing camera.json
    # camera_location = FakeLocationProvider('camera-location.json')
    # camera_location = UdpLocationProvider()
    camera_location = GpsdLocationProvider(host='127.0.0.1')
    config = ConfigParser.RawConfigParser()
    config.read('camera.cfg')
    driver = JVC(host=config.get('access', 'hostname'),
                 user=config.get('access', 'username'),
                 password=config.get('access', 'password'))
    # TODO: stub camera driver
    camera = Camera(driver=driver,
                    location_provider=camera_location)

    # change subject location via editing subject.json
    subject_location = FakeLocationProvider('subject-location.json')
    subject = Subject(location_provider=subject_location)

    tracker = Tracker(camera=camera,
                      subject=subject)

    # start processing events
    while True:
        camera_location.process()
        subject_location.process()
        time.sleep(1.0)

if __name__ == '__main__':
    run()