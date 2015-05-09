#!/usr/bin/python

import Queue
import threading
from time import sleep

'''Asynchronous camera controller

It queues up camera control commands and executes them in separate
thread.

This allows control methods return immediately, without waiting
for the response from the camera, which may take several hundred
milliseconds.

On creation it connects to the camera, logs in and starts kicking it
to maintain session. It also fetches images periodically. Queues up
contol commands and executes them in order.
'''

def control_thread(queue, init_cmd=None):
    '''Receives commands through queue and executes them'''

    while True:
        # TODO: use variable number of arguments
        fn,args = queue.get()
        if args is None:
            fn()
        else:
            fn(args[0], args[1])
        queue.task_done()

def kick_thread(driver,dummy):
    '''Keeps kicking the camera to keep session alive'''
    while True:
        sleep(10)
        driver.kick()

def preview_thread(driver,dummy):
    '''Keeps fetching preview images'''
    while True:
        try:
            img = driver.getjpg()
            driver.savejpg(img, 'current.jpg')
            sleep(0.5)
        except IOError:
            # e.g. no connection yet
            # TODO: use default image?
            pass 

class AsyncCamera:

    def __init__(self, driver=None):
        self.driver = driver

        self.c_queue = Queue.Queue() 
        self.c_thread = threading.Thread(target=control_thread,
                                         args=(self.c_queue,None))
        self.c_thread.daemon = True
        self.c_thread.start()

        self.c_queue.put((self.driver.login, None))
        #self.c_queue.join() -- would block creator

        self.k_thread = threading.Thread(target=kick_thread,
                                         args=(self.driver,None))
        self.k_thread.daemon = True
        self.k_thread.start()

        self.p_thread = threading.Thread(target=preview_thread,
                                         args=(self.driver,None))
        self.p_thread.daemon = True
        self.p_thread.start()

    def close(self):
        self.c_queue.put((self.driver.logout, None))
        self.c_queue.join()

    def pantilt(self, pan=0, tilt=0):
        '''Pan and tilt camera to the given angles (degrees)'''
        self.c_queue.put((self.driver.pantilt, (pan, tilt)))

    def zoom(self, zoom=10, speed=1):
        '''Set zoom level using given speed'''
        self.c_queue.put((self.driver.zoom, (zoom, speed)))


        

