
import pickle

from kivy.lib import osc


class CameraService(object):
    """
    Recieves camera control commands.
    Sends preview images.
    Works over OSC.
    """

    def __init__(self, camera, rx_port, tx_port):

        # initialize camera
        self.camera = camera

        self.rx_port = rx_port
        self.tx_port = tx_port

        # using OSC as Android doesn't support POSIX-style IPC
        osc.init()
        self._oscid = osc.listen(port=rx_port)
        osc.bind(self._oscid, self._pantilt, '/pantilt')
        osc.bind(self._oscid, self._zoom, '/zoom')
        osc.bind(self._oscid, self._logout, '/logout')
        osc.bind(self._oscid, self._stop_preview, '/stop_preview')
        osc.bind(self._oscid, self._start_preview, '/start_preview')
        osc.bind(self._oscid, self._get_ptz, '/get_ptz')
        osc.bind(self._oscid, self._stop_recording, '/stop_recording')
        osc.bind(self._oscid, self._start_recording, '/start_recording')

        # notify UI of current PTZ state
        osc.sendMsg('/ptz', [pickle.dumps(camera.ptz()), ],
                    port=self.tx_port)
        # note: if service is already running when UI starts this
        # won't happen -- remove?

    def _pantilt(self, message, *args):
        pan,tilt = pickle.loads(message[2]) 
        self.camera.pantilt(pan,tilt)

    def _zoom(self, message, *args):
        level,speed = pickle.loads(message[2])
        self.camera.zoom(level,speed)

    def _logout(self, *args):
        self.camera.close()
        osc.dontListen()
        exit()

    def _stop_preview(self, *args):
        self.camera.stop_preview()

    def _start_preview(self, *args):
        self.camera.start_preview()

    def _get_ptz(self, *args):
        osc.sendMsg('/ptz', [pickle.dumps(self.camera.ptz()), ],
                    port=self.tx_port)

    #  TODO: use decorator
    def _stop_recording(self, *args):
        self.camera.stop_recording()

    def _start_recording(self, *args):
        self.camera.start_recording()

    def run(self):
        while True:
            # process incoming commands
            try:
                osc.readQueue(self._oscid)
            except KeyError:
                return

            # send preview update
            jpg = self.camera.getjpg()
            if jpg is not None:
                # NOTE: OSC is UDP based, therefore jpg must be 64k or less
                # (otherwise it must be split to multiple transfers)
                # Also note that the OS might drop UDP packets if its
                # receive buffers are small (can be increased in OSCServer by 
                # using setsockopt).
                assert(len(jpg) < 64000)
                osc.sendMsg('/jpg', [jpg,], port=self.tx_port, typehint='b')
