
import time

from klppr.driver.camera.jvc import JVC
from klppr.driver.location.fake import FakeLocationProvider
from klppr.camera import Camera
from klppr.subject import Subject
from klppr.tracker import Tracker


if __name__ == '__main__':

    # change camera location via editing camera.json
    camera_location = FakeLocationProvider('camera-location.json')
    driver = JVC()
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
        time.sleep(0.5)
