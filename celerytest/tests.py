import time

from . import setup_celery_worker
from .testcase import CeleryTestCaseMixin
from unittest import TestCase

# set up a test app with some tasks
from celery import Celery
app = Celery()

setup_celery_worker(app)

@app.task
def wait_a_second(delay=1):
    time.sleep(delay)
    return delay
    
@app.task
def multiply(a, b):
    return a*b

class WorkerThreadTestCase(CeleryTestCaseMixin, TestCase):
    celery_app = app
    celery_concurrency = 4
    
    delay = .1
    overhead_time = 0.05

    def test_sequential(self):
        x, base, pwr = 1, 2, 5
        for i in range(0,pwr):
            result = multiply.delay(x, base)
            t1 = time.time()
            self.worker.active.wait()
            t2 = time.time()
            self.worker.idle.wait()
            t3 = time.time()
            x = result.get()
            self.assertEqual(x, pow(base,i+1))
            t4 = time.time()
            
            # see that we started in reasonable time
            self.assertTrue(t2-t1 < self.overhead_time)
            # see that we finished in reasonable time
            self.assertTrue(t3-t2 < self.overhead_time * 2)
            # see that we got the result in reasonable time
            self.assertTrue(t4-t3 < self.overhead_time)

        self.assertEqual(x, pow(base,pwr))

    def test_parallel(self):
        count = self.celery_concurrency
        results = [wait_a_second.delay(self.delay) for i in range(0,count)]

        # make sure we're actually testing parralism here
        # total expected time should be less than repeated delay
        self.assertTrue(self.delay * count > self.delay + (self.overhead_time * count))
        
        t1 = time.time()
        
        # wait until we start
        self.worker.active.wait()
        t2 = time.time()
        
        # then wait until we're done
        self.worker.idle.wait()
        t3 = time.time()
        
        # should have all results now
        [r.get() for r in results]
        t4 = time.time()

        # see that we started in reasonable time
        self.assertTrue(t2-t1 < self.overhead_time)
        # see that we finished in reasonable time (should have run in parallel)
        self.assertTrue(t3-t2 < self.delay + self.overhead_time * count)
        # see that we got the results in reasonable time
        self.assertTrue(t4-t3 < self.overhead_time)
