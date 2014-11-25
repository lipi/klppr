#!/usr/bin/python
#
# JVC GV-LS2 camera control
#

import sys
import json
import time
from threading import Timer

import requests
from requests.auth import HTTPDigestAuth
from requests.adapters import HTTPAdapter

class JVC:
    
    def __init__(self, host='192.168.1.1', user='root', password='password'):
        self.host=host
        self.session = requests.session()
        self.session.auth = HTTPDigestAuth(user, password)
        self.url = 'http://%s' % self.host
        self.session.mount(self.url, HTTPAdapter(max_retries=5))
        # maybe auto-login?

    def get(self, uri='/'):
        url = self.url + uri
        try:
            r = self.session.get(url)
        except requests.exceptions.ConnectionError as err:
            print err
            self.session = requests.session()
            r = self.session.get(url)
        return r

    def post(self, uri='/'):
        url = self.host + uri
        try:
            r = self.session.post(url)
        except requests.exceptions.ConnectionError as err:
            print err
            self.session = requests.session()
            r = self.session.post(url)
        return r

    def login(self):
        r = self.get('/php/session_start.php')
        if r.ok:
            self.start_kicking()
        else:
            print 'login failed'
        return r.ok

    def start_kicking(self):
        self.cont = True
        self.kick()        

    def stop_kicking(self):
        self.cont = False

    def kick(self):
        '''Keep kicking the camera to avoid disconnecting us (after 30 sec)'''
        if self.cont:
            r1 = self.get('/php/session_continue.php')
            r2 = self.get('/php/get_error_code.php')
            r3 = self.get('/cgi-bin/camera_status.cgi')
            if r1.ok and r2.ok and r3.ok:
                pass
                #print 'kick OK'
            else:
                print 'kick failed' 
            Timer(5, self.kick).start()

    def logout(self):
        self.stop_kicking()
        self.get('/php/session_finish.php')

    def pantilt(self, pan=0, tilt=0):
        cmd = {"Cmd":0,"Pan":pan,"Tilt":tilt}
        payload = {"Command":"SetPTCtrl",
                              "Params": cmd}
        r = self.post('/cgi-bin/cmd.cgi',
                      data = json.dumps(payload))
        print r.reason
        return self.getptz()

    'POST /cgi-bin/cmd.cgi HTTP/1.1\r\nHost: 192.168.3.103\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\nContent-Type: application/json; charset=UTF-8\r\nReferer: http://192.168.3.103/php/monitor.php\r\nContent-Length: 72\r\nCookie: EverioServer=b190035a65812a0ab6e45964e54aa164\r\nConnection: keep-alive\r\nPragma: no-cache\r\nCache-Control: no-cache\r\n\r\n{"Command":"SetZoomPosition","Params":{"DeciZoomPosition":13,"Speed":3}}'

    def zoom(self, zoom=10, speed=1):
        cmd = {"DeciZoomPosition":zoom, "Speed":speed}
        payload = {"Command": "SetZoomPosition", "Params":cmd }
        r = self.post('/cgi-bin/cmd.cgi', 
                      data = json.dumps(payload))
        print r.reason
        return self.getptz()

    def getptz(self):
        r = self.get('/cgi-bin/ptz_position.cgi')
        j = r.json()
        data = j['Data']
        pan = data['PanPosition']
        tilt = data['TiltPosition']
        zoom = data['DeciZoomPosition']
        return pan,tilt,zoom

    def getstatus(self):
        r = self.get('/cgi-bin/camera_status.cgi')
        j = r.json()
        print j['Data']['SdcardRemains']
        return


    def getjpg(self):
        r = self.get('/cgi-bin/get_jpg.cgi')
        return r


    def test(self, tries=60):
        self.login()
        for i in range(tries):
            print i, self.getptz()
            self.getjpg()
            time.sleep(1)

if __name__ == '__main__':

    host = '192.168.3.103'
    if len(sys.argv) > 1:
        host = sys.argv[1]

    j = JVC(host)

    j.test(3600 * 10)
