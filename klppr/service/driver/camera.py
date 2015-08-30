#!/usr/bin/python

from Queue import Queue, Empty
from threading import Thread
from time import sleep
import logging

'''Asynchronous camera controller

It queues up camera control commands and executes them in separate
thread.

This allows control methods return immediately, without waiting
for the response from the camera, which may take several hundred
milliseconds.

On creation it connects to the camera, logs in and:
 - keeps kicking it to maintain the session,
 - fetches images periodically (if required),
 - queues up control commands and executes them in order.
'''


class AsyncCamera:

    def __init__(self, driver):
        self._driver = driver

        # NOTE: command queue is not necessary anymore, PTZ commands
        # create a new thread, login/out could do the same
        self._cmd_queue = Queue() 
        self._cmd_thread = Thread(target=self._control_fn)
        self._cmd_thread.daemon = True
        self._cmd_thread.start()

        self._cmd_queue.put((self._driver.login, None))
        self._cmd_queue.join() # will block creator
        try:
            self._pan,self._tilt,self._zoom = self._driver.getptz()
        except:
            self._pan,self._tilt,self._zoom = 0,0,0
 
        self._kick_thread = Thread(target=self._kick_fn)
        self._kick_thread.daemon = True
        self._kick_thread.start()

        self._jpg_queue = Queue()
        self._is_previewing = False
        self._preview_thread = Thread(target=self._preview_fn)
        self._preview_thread.daemon = True
        self._preview_thread.start()


    def _control_fn(self):
        '''Receives commands through queue and executes them in sequence'''
        while True:
            # TODO: use variable number of arguments
            fn,args = self._cmd_queue.get()
            if args is None:
                fn()
            else:
                fn(args[0], args[1])
            self._cmd_queue.task_done()

    def _kick_fn(self):
        '''Keeps kicking the camera to keep session alive'''
        while True:
            sleep(10)
            if True != self._driver.kick():
                self._driver.logout()
                self._driver.login()                

    def _preview_fn(self):
        '''Keeps fetching preview images.

        Fetches JPEG images one-by-one, as fast as possible.'''
        while True:
            if not self._is_previewing:
                # reduce CPU load by avoiding busy looping
                sleep(.5)
                continue

            jpg = self._driver.getjpg()
            if bool(jpg):
                logging.info('preview: {0} bytes'.format(len(jpg)))
                self._jpg_queue.put(jpg)

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

    def getjpg(self):
        '''
        Return the most recent image received by the preview thread.
        '''
        jpg = None
        while not self._jpg_queue.empty():
            jpg = self._jpg_queue.get()
        return jpg

    def ptz(self):
        return self._pan,self._tilt,self._zoom

    def start_preview(self):
        self._is_previewing = True

    def stop_preview(self):
        self._is_previewing = False

    # TODO: use decorator
    def start_recording(self):
        Thread(target=self._driver.start_recording).start()

    def stop_recording(self):
        Thread(target=self._driver.stop_recording).start()
