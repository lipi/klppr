#!/usr/bin/python
#
# JVC GV-LS2 camera control
#

import sys
import json
import time

import requests
from requests import Response
from requests.auth import HTTPDigestAuth
from requests.adapters import HTTPAdapter

from PIL import Image
from StringIO import StringIO

def timestamp():
    '''Return number of milliseconds since Epoch'''
    return int(time.time() * 1000)

def add_timestamp(url):
    '''Append timestamp to URL

    Could be used to determine latency'''
    if ('cgi' in url):
        if '?' in url:
            url += '&{}'.format(timestamp())
        else:
            url += '?{}'.format(timestamp())
    return url

class JVC:
    
    def __init__(self, host='192.168.1.1', user='root', password='password'):
        self.host=host
        self.session = requests.session()
        self.session.auth = HTTPDigestAuth(user, password)
        self.url = 'http://%s' % self.host
        self.session.mount(self.url, HTTPAdapter(max_retries=0,
                                                 pool_connections=100, 
                                                 pool_maxsize=100))
        self.cookies = self.session.cookies
        self.debug = True

    def _get(self, uri='/', **kwargs):
        url = self.url + uri
        url = add_timestamp(url)
        response = Response()
        try:
            response = self.session.get(url, **kwargs)
        except Exception as ex:
            print ex
        return response

    def _post(self, uri, data, **kwargs):
        url = self.url + uri
        url = add_timestamp(url)
        if self.debug:
            print 'POST', url, data
        response = Response()
        try:
            response = self.session.post(url, data=data, **kwargs)
        except Exception as ex:
            print ex
        return response

    def login(self):
        timeout = (3,1) 
        r = self._get('/php/session_start.php', timeout=timeout)
        success = False
        if r.ok:
            success = True
            if self.debug:
                print 'login OK'
            self._get('/php/monitor.php', timeout=timeout)
            # must have for get_jpg
            self._get('/cgi-bin/hello.cgi', timeout=timeout)
            # not sure if needed
            self._get('/cgi-bin/resource_release.cgi?param=mjpeg',
                      timeout=timeout)
        else:
            print 'login failed'
        return success

    def kick(self):
        '''Keep opening new sessions same as the web app does'''
        timeout = (10,5)
        try:
            r1 = self._get('/php/session_continue.php', timeout=timeout)
            r2 = self._get('/php/get_error_code.php', timeout=timeout)
            r3 = self._get('/cgi-bin/camera_status.cgi', timeout=timeout)
        except Exception as ex:
            print ex

        if r1.ok and r2.ok and r3.ok:
            if self.debug:
                print 'kick OK'
        else:
            print 'kick failed', r1, r2, r3

    def logout(self):
        self._get('/php/session_finish.php')
        if self.debug:
            print 'logout'

    def pantilt(self, pan=0, tilt=0):
        cmd = {"Cmd":0,"Pan":pan,"Tilt":tilt}
        payload = {"Command":"SetPTCtrl",
                              "Params": cmd}
        r = self._post('/cgi-bin/cmd.cgi',
                       data = json.dumps(payload),
                       timeout = (3,1))
        if self.debug:
            print r.reason

    def zoom(self, zoom=10, speed=1):
        cmd = {"DeciZoomPosition":zoom, "Speed":speed}
        payload = {"Command": "SetZoomPosition", "Params":cmd }
        r = self._post('/cgi-bin/cmd.cgi', 
                       data = json.dumps(payload),
                       timeout = (3,1))
        if self.debug:
            print r.reason

    def getptz(self):
        r = self._get('/cgi-bin/ptz_position.cgi', timeout = (3,1))
        if r.ok:
            j = r.json()
            data = j['Data']
            pan = data['PanPosition']
            tilt = data['TiltPosition']
            zoom = data['DeciZoomPosition']
            result = (pan,tilt,zoom)
        else:
            result = r
        return result

    def getstatus(self):
        r = self._get('/cgi-bin/camera_status.cgi')
        j = r.json()
        if self.debug:
            print j['Data']['SdcardRemains']
        return

    def getjpg(self):
        response = self._get('/cgi-bin/get_jpg.cgi', timeout=(3,1))
        img = None
        if response.content:
            img = Image.open(StringIO(response.content))
        return img

    def getimg(self):
        img = self.getjpg()
        if img is not None:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        return img

    def savejpg(self, img, filename='x.jpg'):
        try:
            img.save(filename)
        except IOError as ex:
            print ex

    def test(self, tries=60):
        self.login()
        self.zoom(100)
        for i in range(tries):
            print i, self.getptz()
            sys.stdout.flush()
            self.pantilt((i % 100) - 50, 10)
            img = self.getjpg()
            self.savejpg(img)
            time.sleep(1)

if __name__ == '__main__':

    host = '192.168.3.103'
    if len(sys.argv) > 1:
        host = sys.argv[1]

    j = JVC(host)

    try:
        j.test(3600 * 10)
    except KeyboardInterrupt:
        j.logout()

