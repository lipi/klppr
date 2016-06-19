import ConfigParser
from ConfigParser import NoOptionError, NoSectionError

from kivy.logger import Logger
from klppr.location import *
from ptz import PTZ

CALIBRATION_FILE = 'calib.cfg'


class CalibrationService(object):

    def __init__(self, location_service, camera_service, **kwargs):
        super(CalibrationService, self).__init__(**kwargs)
        self.location_service = location_service
        self.camera_service = camera_service
        self.calibrator = Calibrator()

    def at_camera(self, *args):
        self.calibrator.location = self.location_service.gps_location

    def at_subject(self, *args):
        subject_location = self.location_service.gps_location
        camera_location = self.calibrator.location
        camera_ptz = self.camera_service.ptz()  # TODO: change it to property, too
        correction = self.calibrator.calibrate(camera_location,
                                               subject_location,
                                               camera_ptz)
        Logger.info('correction:{}'.format(correction))
        # TODO: notify tracker when calibration changes


class CalibrationServiceOsc(CalibrationService):

    def __init__(self, connector, *args, **kwargs):
        super(CalibrationServiceOsc, self).__init__(*args, **kwargs)
        self.connector = connector
        self.connector.connect(self.at_camera, '/at_camera')
        self.connector.connect(self.at_subject, '/at_subject')


class Calibrator(object):
    """
    Camera calibrator

    Calculate calibration values based on:
    - subject location (lat,lon,alt)
    - camera location (lat,lon,alt)
    - camera orientation (pan,tilt,zoom)

    Provide calibration values (camera location and correction).
    Store calibration values for subsequent sessions.

    >>> Calibrator()
    ((0, 0, 0), (0, 0, 1))
    """

    def __init__(self):
        # attributes
        self._location = None
        self._correction = None
        self._config = None
        # load calibration values from file
        try:
            self._load_calibration()
        except (NoSectionError, NoOptionError):
            self.location = Location(0, 0, 0)
            self.correction = PTZ()

    def __repr__(self):
        return str((self.location, self.correction))

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, x):
        self._location = x
        config = self._config
        if not config.has_section('location'):
            config.add_section('location')
        try:
            config.set('location', 'latitude', str(x.latitude))
            config.set('location', 'longitude', str(x.longitude))
            config.set('location', 'altitude', str(x.altitude))
        except AttributeError as err:
            Logger.error('Invalid location: {}'.format(err))
        self._save_calibration()

    @property
    def correction(self):
        return self._correction

    @correction.setter
    def correction(self, x):
        self._correction = x
        config = self._config
        if not config.has_section('correction'):
            config.add_section('correction')
        config.set('correction', 'pan', str(x.pan))
        config.set('correction', 'tilt', str(x.tilt))
        config.set('correction', 'zoom', str(x.zoom))
        self._save_calibration()

    def _load_calibration(self):
        """
        Load calibration values from file
        :return: location and ptz tuples
        """
        config = ConfigParser.SafeConfigParser()
        config.read(CALIBRATION_FILE)
        self._config = config

        # TODO: use defaults
        latitude = config.getfloat('location', 'latitude')
        longitude = config.getfloat('location', 'longitude')
        altitude = config.getfloat('location', 'altitude')

        pan = config.getfloat('correction', 'pan')
        tilt = config.getfloat('correction', 'tilt')
        zoom = config.getfloat('correction', 'zoom')

        self.location = Location(latitude, longitude, altitude)
        self.correction = PTZ(pan, tilt, zoom)

        return

    def _save_calibration(self):
        """
        Save calibration data to file
        """
        with open(CALIBRATION_FILE, 'wb') as configfile:
            self._config.write(configfile)

    def calibrate(self, camera, subject, ptz):
        """
        Calculate correction values based on camera and subject location,
        and camera PTZ values.

        :param camera: camera location
        :param subject: subject location
        :param ptz: pan/tilt/zoom settings

        >>> camera = Location(0, 0)
        >>> subject = Location(1, 1)
        >>> ptz = PTZ(10, 0, 1)
        >>> c = Calibrator()
        >>> c.calibrate(camera, subject, ptz)
        (35.0, 0.0, 1)
        """
        try:
            pan = bearing(camera, subject) - ptz.pan
            tilt = elevation(camera, subject) - ptz.tilt
            zoom = ptz.zoom / distance(camera, subject)
            pan = round(pan, 2)
            tilt = round(tilt, 2)
            zoom = round(zoom, 2)
            self.correction = PTZ(pan, tilt, zoom)
        except AttributeError as err:
            Logger.error('Invalid parameter: {}'.format(err))
            self.correction = PTZ(0,0,1)
        return self.correction

if __name__ == "__main__":
    import doctest
    import os
    # remove output of previous tests
    os.remove(CALIBRATION_FILE)
    doctest.testmod()