#!/usr/bin/python
#
# JVC GV-LS2 camera control
#

# standard libraries
import sys
import json
import time
import logging

# 3rd party libraries
import requests
from requests.auth import HTTPDigestAuth
from requests.adapters import HTTPAdapter
from PIL import Image
from StringIO import StringIO

logger = logging.getLogger(__name__)


def timestamp():
    """Return number of milliseconds since Epoch"""
    return int(time.time() * 1000)


def add_timestamp(url):
    """Append timestamp to URL

    Could be used to determine latency"""
    if 'cgi' in url:
        if '?' in url:
            url += '&{}'.format(timestamp())
        else:
            url += '?{}'.format(timestamp())
    return url


class JVC:
    
    def __init__(self, host='192.168.1.1', user='root', password='password'):
        self.host = host
        self.session = requests.session()
        self.session.auth = HTTPDigestAuth(user, password)
        self.url = 'http://%s' % self.host
        self.session.mount(self.url, HTTPAdapter(max_retries=0,
                                                 pool_connections=100, 
                                                 pool_maxsize=100))
        self.cookies = self.session.cookies

        # initialized here to silence PyCharm warnings
        self.control_timeout = None
        self.get_timeout = None
        self.kick_timeout = None
        self.init_timeouts()

        # avoid duplicate entries
        logger.propagate = False

    def init_timeouts(self):
        """
        Initialize connection and read timeout values for HTTP requests

        Timeouts are a result of trial-and-error on a wifi network and
        GSM-to-ADSL connection.
        """

        # For further reading see
        # http://www.stevesouders.com/blog/2011/09/21/making-a-mobile-connection/
        # control commands seem to have 100-300 msec response time
        # normally (both GSM and wifi) but jump up to 2-3 secs of
        # response time after some inactivity, so choosing 5
        # seconds for connection timeout
        self.control_timeout = (5, 3)
        self.get_timeout = (3, 1)
        self.kick_timeout = (10, 5)

    def _get(self, uri='/', **kwargs):

        """
        GET the relative path (URI) and return the response.
        May throw exception.
        """
        url = self.url + uri
        url = add_timestamp(url)
        response = self.session.get(url, **kwargs)
        logger.info('elapsed: {0} reason: {1}'.format(response.elapsed,
                                                      response.reason))
        return response

    def _post(self, uri, data, **kwargs):
        """
        POST data to the relative path (URI) and return the response.
        May throw exception.
        """
        url = self.url + uri
        url = add_timestamp(url)
        logger.debug('POST {0} {1}'.format(url, data))
        response = self.session.post(url, data=data, **kwargs)
        logger.info('elapsed: {0} reason: {1}'.format(response.elapsed,
                                                      response.reason))
        return response
                     
    def login(self):
        timeout = self.get_timeout
        success = False
        try:
            r = self._get('/php/session_start.php', timeout=timeout)
            if r.reason == 'OK':
                r = self._get('/php/monitor.php', timeout=timeout)
            if r.reason == 'OK':
                # must have for get_jpg
                r = self._get('/cgi-bin/hello.cgi', timeout=timeout)
            if r.reason == 'OK':
                # not sure if needed
                r = self._get('/cgi-bin/resource_release.cgi?param=mjpeg',
                              timeout=timeout)
            if r.reason == 'OK':
                success = True
        except Exception as ex:
            logger.debug('{0}'.format(ex))
            logger.info('login failed')
        return success

    def kick(self):
        """Keep opening new sessions same as the web app does"""
        timeout = self.kick_timeout
        try:
            r1 = self._get('/php/session_continue.php', timeout=timeout)
            r2 = self._get('/php/get_error_code.php', timeout=timeout)
            r3 = self._get('/cgi-bin/camera_status.cgi', timeout=timeout)
        except Exception as ex:
            logger.debug('kick: {0}'.format(ex))
            return False

        if r1.reason == 'OK' and r2.reason == 'OK' and r3.reason == 'OK':
            logger.info('kick OK')
            return True
        else:
            logger.warning('kick failed')
            return False

    def logout(self):
        try:
            self._get('/php/session_finish.php')
        except Exception as ex:
            logger.info('logout: {0}'.format(ex))
        logger.info('logout')

    def pantilt(self, pan=0, tilt=0):
        cmd = {"Cmd": 0, "Pan": pan, "Tilt": tilt}
        payload = {"Command": "SetPTCtrl", "Params": cmd}
        try:
            self._post('/cgi-bin/cmd.cgi',
                       data=json.dumps(payload),
                       timeout=self.control_timeout)
        except Exception as ex:
            logger.debug('pantilt: {0}'.format(ex))

    def zoom(self, zoom=10, speed=1):
        cmd = {"DeciZoomPosition": zoom, "Speed": speed}
        payload = {"Command": "SetZoomPosition", "Params": cmd}
        try:
            self._post('/cgi-bin/cmd.cgi',
                       data=json.dumps(payload),
                       timeout=self.control_timeout)
        except Exception as ex:
            logger.debug('zoom: {0}'.format(ex))

    @property
    def getptz(self):
        result = None
        try:
            response = self._get('/cgi-bin/ptz_position.cgi',
                                 timeout=self.get_timeout)
            j = response.json()
            data = j['Data']
            pan = data['PanPosition']
            tilt = data['TiltPosition']
            zoom = data['DeciZoomPosition']
            result = (pan, tilt, zoom)
        except requests.exceptions.ConnectTimeout:
            pass

        return result

    def getstatus(self):
        try:
            r = self._get('/cgi-bin/camera_status.cgi')
            j = r.json()
            logger.debug('{0}'.format(j['Data']['SdcardRemains']))
        except Exception as ex:
            logger.debug('getstatus: {0}'.format(ex))

        return

    def getjpg(self):
        """Return JPEG image data received from camera or None."""
        jpg = None
        try:
            response = self._get('/cgi-bin/get_jpg.cgi',
                                 timeout=self.get_timeout)
            jpg = response.content
        except Exception as ex:
            logger.debug('getjpg: {0}'.format(ex))

        return jpg

    def getimg(self):
        """Fetch JPEG data from camera and convert it to PIL image.
        Flip image vertically. Return None if no data."""
        jpg = self.getjpg()
        img = None
        if jpg is not None:
            img = Image.open(StringIO(jpg))
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        return img

    def _recording(self, ctrl):
        payload = {"Command": "SetCamCtrl", "Params": {"Ctrl": ctrl}}
        try:
            self._post('/cgi-bin/cmd.cgi',
                       data=json.dumps(payload),
                       timeout=self.control_timeout)
        except Exception as ex:
            logger.debug('recording: {0}'.format(ex))

    def start_recording(self):
        """
        Start recording video to SD card
        """
        self._recording("RecStart")

    def stop_recording(self):
        """
        Stop recording video
        """
        self._recording("RecStop")

    def test(self, tries=60):
        self.login()
        self.zoom(100)
        for i in range(tries):
            print i, self.getptz
            sys.stdout.flush()
            self.pantilt((i % 100) - 50, 10)
            img = self.getjpg()
            if img:
                img.save('x.jpg')
            time.sleep(1)

if __name__ == '__main__':

    hostname = '192.168.3.103'
    if len(sys.argv) > 1:
        hostname = sys.argv[1]

    jvc = JVC(hostname)

    try:
        jvc.test(3600 * 10)
    except KeyboardInterrupt:
        jvc.logout()
