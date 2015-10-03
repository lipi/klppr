

"""
Subject tracker

- Receive subject location updates.
- Receive calibration updates.
- Calculate camera pan/tilt/zoom values based on
  camera calibration and subject location.
- Send PTZ values to camera.
"""


class Tracker(object):

    def __init__(self, location_service, calib_service, camera_service):
        self.camera_service = camera_service
        #camera_service.bind(ptz=self.on_ptz) # just testing
        # subscribe to location updates

        # subscribe to calibration changes
        pass

    def _on_location_update(self):
        # calculate PTZ values
        # send PTZ values to camera
        pass

    def _on_calibration_update(self):
        # update copy of calibration values
        pass

    def on_ptz(self, instance, value):  # just testing
        print 'tracker on_ptz', value


