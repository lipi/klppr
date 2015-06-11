#!/usr/bin/python

from Queue import Queue, Empty
from threading import Thread
from time import sleep

'''Asynchronous camera controller

It queues up camera control commands and executes them in separate
thread.

This allows control methods return immediately, without waiting
for the response from the camera, which may take several hundred
milliseconds.

On creation it connects to the camera, logs in and:
 - keeps kicking it to maintain the session,
 - fetches images periodically,
 - queues upcontrol commands and executes them in order.
'''

def _control_fn(queue, init_cmd=None):
    '''Receives commands through queue and executes them in sequence'''
    while True:
        # TODO: use variable number of arguments
        fn,args = queue.get()
        if args is None:
            fn()
        else:
            fn(args[0], args[1])
        queue.task_done()

def _kick_fn(_driver,dummy):
    '''Keeps kicking the camera to keep session alive'''
    while True:
        sleep(10)
        _driver.kick()

def _preview_fn(_driver,image_queue):
    '''Keeps fetching preview images'''
    while True:
        _img = _driver.getimg()
        if bool(_img):
            #print 'preview:', _img
            image_queue.put(_img)

class AsyncCamera:

    def __init__(self, driver):
        self._driver = driver
        self._img_queue = Queue()

        self._cmd_queue = Queue() 
        self._cmd_thread = Thread(target=_control_fn, args=(self._cmd_queue,None))
        self._cmd_thread.daemon = True
        self._cmd_thread.start()

        self._cmd_queue.put((self._driver.login, None))
        self._cmd_queue.join() # will block creator
        self._pan,self._tilt,self._zoom = self._driver.getptz()
 
        self._kick_thread = Thread(target=_kick_fn, args=(self._driver,None))
        self._kick_thread.daemon = True
        self._kick_thread.start()

        self._preview_thread = Thread(target=_preview_fn,
                               args=(self._driver,self._img_queue))
        self._preview_thread.daemon = True
        self._preview_thread.start()

    def close(self):
        self._cmd_queue.put((self._driver.logout, None))
        self._cmd_queue.join()

    def pantilt(self, pan=0, tilt=0):
        '''Pan and tilt camera to the given angles (degrees)'''
        self._pan,self._tilt = pan,tilt
        # Create a thread for the potentially long-running command.
        # This means commands can run parallel (out-of-order).
        # If this is not desirable (not sure?) use the command queue.
        Thread(target=self._driver.pantilt, args=(pan,tilt)).start()
        
    def zoom(self, zoom=10, speed=1):
        '''Set zoom level using given speed'''
        self._zoom = zoom
        # Create a thread for the potentially long-running command.
        # This means commands can run parallel (out-of-order).
        # If this is not desirable (not sure?) use the command queue.
        Thread(target=self._driver.zoom, args=(zoom,speed)).start()

    def getimg(self):
        '''
        Return the most recent image received by the preview thread.
        '''
        img = None
        while not self._img_queue.empty():
            img = self._img_queue.get()
        return img

    def ptz(self):
        return self._pan,self._tilt,self._zoom
