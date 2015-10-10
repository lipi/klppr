
from PIL import Image as PilImage
from StringIO import StringIO
import pickle

import kivy
kivy.require('1.8.0')  # replace with your current kivy version !
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.properties import StringProperty
from kivy.logger import Logger
from kivy.uix.screenmanager import Screen

class GpsScreen(Screen):
    """
    GPS calibration screen

    - monitor GPS quality
    - save camera location
    """

    current_location = StringProperty('--')
    current_accuracy = StringProperty('--')
    subject_location = StringProperty('--')
    camera_location = StringProperty('--')

    def __init__(self, connector, **kwargs):
        super(GpsScreen, self).__init__(**kwargs)
        self.connector = connector
        self.connector.connect(self.receive_location, '/location')
        self.connector.connect(self.receive_accuracy, '/accuracy')

    def receive_location(self, message, *args):
        """
        Update our pan/tilt/zoom values based on camera's
        """
        location = pickle.loads(message[2])
        Logger.info('location: %d,%d,%d' % location)
        self.current_location = "%f\n%f\n%.1f" % location

    def receive_accuracy(self, message, *args):
        accuracy = pickle.loads(message[2])
        self.current_accuracy = "%.1f" % accuracy

    def on_camera_button(self):
        self.camera_location = self.current_location
        self.connector.send('/at_camera')
        Logger.debug('camera')

    def on_subject_button(self):
        self.subject_location = self.current_location
        self.connector.send('/at_subject')
        Logger.debug('subject')


class CameraScreen(Screen):
    """
    PTZ calibration screen

    - preview camera image
    - adjust pan/tilt/zoom
    """

    image = ObjectProperty()
    ptz = StringProperty()

    previewing = BooleanProperty(True)
    connected = BooleanProperty(False)

    def __init__(self, connector, **kwargs):
        super(CameraScreen, self).__init__(**kwargs)
        self.connector = connector
        self.connector.connect(self.receive_jpg, '/jpg')
        self.connector.connect(self.receive_ptz, '/ptz')

    #
    # Camera control
    #

    def on_touch_down(self, touch):
        pos = self.image.to_widget(touch.x, touch.y)
        if self.image.collide_point(*pos):
            touch.grab(self)

            if self.previewing:
                self.connector.send('/stop_preview')
                self.previewing = False
            else:
                self.connector.send('/start_preview')
                self.previewing = True
            self.update_status_label(self.connected, self.previewing)
            # touch is handled, discard it
            return True

        # touch doesn't belong to us, bubble it up
        return super(CameraScreen, self).on_touch_down(touch)

    def update_status_label(self, connected,  previewing):
        text = ''
        if not connected:
            text += 'Waiting for camera...\n'
        if not previewing:
            text += 'Preview paused, touch to continue'
        self.status_label.text = text

    # not used at moment, left here for reference
    def update_pos_label(self, pos=None):
        """
        Display touch position over preview image
        """
        if self.image.collide_point(*pos):
            label = self.pos_label
            center = self.image.center
            centered_pos = (pos[0] - center[0], pos[1] - center[1])  # touch.pos
            label.text = '(%d, %d)' % centered_pos
            label.texture_update()
            label.pos = centered_pos
        else:
            self.pos_label.text = ''

    #
    # OSC callbacks
    #
    def receive_jpg(self, message, *args):
        """
        Receive preview image and blit it to the preview surface.
        """
        try:
            jpg = message[2]
        except Exception as ex:
            Logger.debug('receive_jpg: {0}'. format(ex))
            return

        self.connected = True
        self.update_status_label(self.connected, self.previewing)

        img = PilImage.open(StringIO(jpg))
        # not clear why (standard?), but the image is upside down
        img = img.transpose(PilImage.FLIP_TOP_BOTTOM)

        # image buffer is RGB, convert it to RGBA (Nexus 4 can't blit RGB),
        # see https://github.com/kivy/kivy/issues/1600
        # img = PilImage.fromstring('RGB', self.imgsize, self.imgbuf)
        img.putalpha(255)
        buf = img.tostring()
        tex = Texture.create(size=img.size, colorfmt='rgba')
        tex.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        self.image.texture = tex
        self.image.allow_stretch = True

    def receive_ptz(self, message, *args):
        """
        Update our pan/tilt/zoom values based on camera's
        """
        pan, tilt, zoom = pickle.loads(message[2])
        self.ptz = '%d,%d,%d' % (pan, tilt, zoom)
        Logger.info('ptz: %s' % self.ptz)


class RecordScreen(Screen):
    """
    Video recording screen

    - monitor GPS signal and network connection.
    - start/stop recording video
    """

    gps_accuracy = StringProperty("0.0 m")
    network_latency = StringProperty("0.0 sec")
    recording_time = StringProperty("0:00:00")

    def __init__(self, connector, **kwargs):
        super(RecordScreen, self).__init__(**kwargs)
        self.connector = connector
        self.connector.connect(self.receive_accuracy, '/accuracy')

    def on_stop(self):
        self.connector.send('/stop_recording')
        Logger.info('stop recording')

    def on_start(self):
        self.connector.send('/start_recording')
        Logger.info('start recording')

    def receive_recording_time(self, message, *args):
        # TODO: display recording time
        pass

    def receive_network_latency(self, message, *args):
        # TODO: display network latency
        pass

    def receive_accuracy(self, message, *args):
        accuracy = pickle.loads(message[2])
        self.gps_accuracy = "%.1f m" % accuracy
