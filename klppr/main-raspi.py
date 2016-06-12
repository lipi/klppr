
import json
import time

from klppr.driver.camera.jvc import JVC
from klppr.driver.camera.asynccam import AsyncCamera

from klppr.camera import Camera
from klppr.subject import Subject
from klppr.tracker import Tracker


class FakeLocation(object):
    """
    Read fake location from file, in JSON format
    """

    def __init__(self, filename='location.json'):
        self.filename = filename

    def process(self):
        with open(self.filename, 'rb') as f:
            data = json.load(f)
            print data


if __name__ == '__main__':
    driver = JVC()
    async_cam = AsyncCamera(driver)
    location_provider = FakeLocation()
    camera = Camera(ptz_camera=async_cam,
                    location_provider=location_provider)
    subject = Subject()
    tracker = Tracker(camera=camera,
                      subject=subject)

    # start processing events
    while True:
        location_provider.process()
        time.sleep(0.5)
