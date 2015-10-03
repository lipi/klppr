
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, BoundedNumericProperty


class CameraService(EventDispatcher):
    """
    Receives camera control commands.
    Sends preview images.
    Works over OSC.
    """

    # TODO: use camera-specific values instead of hardcoded ones
    pan = BoundedNumericProperty(0, min=-150, max=150,
                                 errorhandler=lambda x: 150 if x > 150 else -150)
    tilt = BoundedNumericProperty(0, min=-40, max=40,
                                  errorhandler=lambda x: 40 if x > 40 else -40)
    zoom = BoundedNumericProperty(10, min=10, max=100,
                                  errorhandler=lambda x: 100 if x > 100 else 10)

    pan_speed = NumericProperty(1)  # TODO: increase speed while button is held
    tilt_speed = NumericProperty(1)  # TODO: increase speed while button is held
    zoom_speed = NumericProperty(1)  # TODO: increase speed while button is held

    def __init__(self, camera, **kwargs):
        super(CameraService, self).__init__(**kwargs)
        # initialize camera
        self._camera = camera

    #
    # property handlers
    #
    def on_pan(self, instance, pos):
        self._camera.pantilt(self.pan, self.tilt)

    def on_tilt(self, instance, pos):
        self._camera.pantilt(self.pan, self.tilt)

    def on_zoom(self, instance, pos):
        self._camera.zoom(self.tilt)

    def ptz(self, pan=None, tilt=None, zoom=None):
        """
        Get/set camera PTZ values
        """
        if (pan, tilt, zoom) == (None,None, None):
            return self.pan, self.tilt, self.zoom
        else:
            self.pan, self.tilt, self.zoom = pan, tilt, zoom

    def up(self, *args):
        self.tilt += self.tilt_speed

    def down(self, *args):
        self.tilt -= self.tilt_speed

    def left(self, *args):
        self.pan -= self.pan_speed

    def right(self, *args):
        self.pan += self.pan_speed

    def zoom_in(self, *args):
        self.zoom += self.zoom_speed

    def zoom_out(self, *args):
        self.zoom -= self.zoom_speed

    #  TODO: use decorator for the following methods
    def stop_preview(self, *args):
        self._camera.stop_preview()

    def start_preview(self, *args):
        self._camera.start_preview()

    def stop_recording(self, *args):
        self._camera.stop_recording()

    def start_recording(self, *args):
        self._camera.start_recording()

    def logout(self, *args):
        self._camera.close()


class CameraServiceOsc(CameraService):

    def __init__(self, connector, **kwargs):
        super(CameraServiceOsc, self).__init__(**kwargs)
        self.connector = connector
        self._osc_init()

    def _osc_init(self):

        self.connector.connect(self.up, '/up')
        self.connector.connect(self.down, '/down')
        self.connector.connect(self.left, '/left')
        self.connector.connect(self.right, '/right')
        self.connector.connect(self.zoom_in, '/zoom_in')
        self.connector.connect(self.zoom_out, '/zoom_out')

        self.connector.connect(self.stop_preview, '/stop_preview')
        self.connector.connect(self.start_preview, '/start_preview')
        self.connector.connect(self.stop_recording, '/stop_recording')
        self.connector.connect(self.start_recording, '/start_recording')
        self.connector.connect(self.logout, '/logout')
        self.connector.connect(self.get_ptz, '/get_ptz')

        # notify UI of current PTZ state
        self.connector.send('/ptz', self._camera.ptz())
        # note: if service is already running when UI starts this
        # won't happen -- remove?

    def logout(self, *args):
        super(CameraServiceOsc, self).logout(*args)
        self.connector.stop()

    def get_ptz(self, *args):
        ptz = super(CameraServiceOsc, self).ptz()
        self.connector.send('/ptz', ptz)

    # TODO: eliminate this function by using events instead of polling
    def process(self):
        # send preview update
        jpg = self._camera.getjpg()
        if jpg is not None:
            # NOTE: OSC is UDP based, therefore jpg must be 64k or less
            # (otherwise it must be split to multiple transfers)
            # Also note that the OS might drop UDP packets if its
            # receive buffers are small (can be increased in OSCServer by
            # using setsockopt).
            assert(len(jpg) < 64000)
            self.connector.send('/jpg', jpg, typehint='b')
