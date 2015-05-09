#!/usr/bin/python
#
# JVC GV-LS2 camera control
#

import sys
import json
import time

import requests
from requests.auth import HTTPDigestAuth
from requests.adapters import HTTPAdapter

from PIL import Image
from StringIO import StringIO

def timestamp():
    return int(time.time() * 1000)

def add_timestamp(url):
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
        self.session.mount(self.url, HTTPAdapter(max_retries=5))
        self.cookies = self.session.cookies
        self.debug = True
        # maybe auto-login?

    def get(self, uri='/'):
        url = self.url + uri
        url = add_timestamp(url)
        # new session for every GET
        session = requests.session()
        session.auth = self.session.auth
        session.cookies = self.cookies
        response = session.get(url)
        return response

    def post(self, uri, data):
        url = self.url + uri
        url = add_timestamp(url)
        if self.debug:
            print 'POST', url, data
        # new session for every POST
        session = requests.session()
        session.auth = self.session.auth
        session.cookies = self.cookies
        response = session.post(url, data=data)
        return response

    def login(self):
        r = self.get('/php/session_start.php')
        if r.ok:
            if self.debug:
                print 'login OK'
            self.get('/php/monitor.php')
            self.get('/cgi-bin/hello.cgi') # must have for get_jpg
            self.get('/cgi-bin/resource_release.cgi?param=mjpeg') # needed?
        else:
            print 'login failed'
        return r.ok

    def kick(self):
        '''Keep opening new sessions same as the web app as does'''
        r1 = self.get('/php/session_continue.php')
        r2 = self.get('/php/get_error_code.php')
        r3 = self.get('/cgi-bin/camera_status.cgi')
        if r1.ok and r2.ok and r3.ok:
            if self.debug:
                print 'kick OK'
        else:
            print 'kick failed', r1, r2, r3

    def logout(self):
        self.get('/php/session_finish.php')
        if self.debug:
            print 'logout'

    def pantilt(self, pan=0, tilt=0):
        cmd = {"Cmd":0,"Pan":pan,"Tilt":tilt}
        payload = {"Command":"SetPTCtrl",
                              "Params": cmd}
        r = self.post('/cgi-bin/cmd.cgi',
                      data = json.dumps(payload))
        if self.debug:
            print r.reason
        return self.getptz()

    def zoom(self, zoom=10, speed=1):
        cmd = {"DeciZoomPosition":zoom, "Speed":speed}
        payload = {"Command": "SetZoomPosition", "Params":cmd }
        r = self.post('/cgi-bin/cmd.cgi', 
                      data = json.dumps(payload))
        if self.debug:
            print r.reason
        return self.getptz()

    def getptz(self):
        r = self.get('/cgi-bin/ptz_position.cgi')
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
        r = self.get('/cgi-bin/camera_status.cgi')
        j = r.json()
        if self.debug:
            print j['Data']['SdcardRemains']
        return

    def getjpg(self):
        response = self.get('/cgi-bin/get_jpg.cgi')
        img = Image.open(StringIO(response.content))
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

