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

def preview_thread(driver,image_queue):
    '''Keeps fetching preview images'''
    while True:
        try:
            img = driver.getimg()
            print 'preview:', img
            image_queue.put(img)
        except IOError:
            # e.g. no connection yet
            # TODO: use default image?
            pass 

class AsyncCamera:

    def __init__(self, driver=None):
        self.driver = driver
        self.i_queue = Queue()
        self.img = None

        self.c_queue = Queue() 
        self.c_thread = Thread(target=control_thread, args=(self.c_queue,None))
        self.c_thread.daemon = True
        self.c_thread.start()

        self.c_queue.put((self.driver.login, None))
        #self.c_queue.join() -- would block creator

        self.k_thread = Thread(target=kick_thread, args=(self.driver,None))
        self.k_thread.daemon = True
        self.k_thread.start()

        self.p_thread = Thread(target=preview_thread,
                               args=(self.driver,self.i_queue))
        self.p_thread.daemon = True
        self.p_thread.start()

    def close(self):
        self.c_queue.put((self.driver.logout, None))
        self.c_queue.join()

    def pantilt(self, pan=0, tilt=0):
        '''Pan and tilt camera to the given angles (degrees)'''
        Thread(target=self.driver.pantilt, args=(pan,tilt)).start()
        

    def zoom(self, zoom=10, speed=1):
        '''Set zoom level using given speed'''
        Thread(target=self.driver.zoom, args=(zoom,speed)).start()

    def getimg(self):
        while not self.i_queue.empty():
            self.img = self.i_queue.get()
        return self.img
