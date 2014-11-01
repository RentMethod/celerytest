[![Build Status](https://travis-ci.org/RentMethod/celerytest.svg?branch=master)](https://travis-ci.org/RentMethod/celerytest)

# celerytest - Integration testing with Celery
Writing (integration) tests that depend on Celery tasks is problematic. When you manually run a Celery worker together with your tests, it runs in a separate process and there's no clean way to address objects targeted by Celery from your tests. When you use a separate test database (as with Django for example), you'll have to duplicate configuration code so your Celery worker accesses the same database.

celerytest provides the ability to run a Celery worker in the background from your tests. It also allows your tests to monitor the worker and pause until Celery tasks are completed.

## Using celerytest

To start a Celery worker in a separate thread, use:

```python
app = Celery() # your Celery app
worker = start_celery_worker(app) # configure the app for our celery worker
```

To wait for the worker to finish executing tasks, use:

```python
result = some_celery_task.delay()
worker.idle.wait() # optionally specify time-out
```

### Django

To use this with your django app through django-celery, get your app as such:

```python
from djcelery.app import app
worker = start_celery_worker(app)
```

### TestCase

If you want to use this in a unittest TestCase, you can use CeleryTestCaseMixin. If you're writing unit tests that depend on a celery worker, though, you're doing it wrong. For unit tests, you'll want to mock your Celery methods and test them separately. You could use CeleryTestCaseMixin to write integration tests with Celery tasks, though.

```python
from unittest import TestCase
from celerytest.testcase import CeleryTestCaseMixin, setup_celery_worker
import time

app = Celery()
setup_celery_worker(app) # need to setup worker outside

class SomeTestCase(CeleryTestCaseMixin, TestCase):
    celery_app = app
    celery_concurrency = 4

    def test_something(self):
        result = multiply.delay(2,3)
        self.worker.idle.wait()
        self.assertEqual(result.get(), 6)
```

### Lettuce

To automatically launch a worker in the background while running a Lettuce integration test suite, add to ``terrain.py``:

```python
# terrain.py
from lettuce import *
from celerytest import start_celery_worker
from app import app

@before.harvest
def initial_setup(server):
    # memory transport may not work here
    world.celery = start_celery_worker(app, config="amqp")

@after.harvest
def cleanup(server):
    world.celery.stop()

@after.each_step
def after_step(step):
    # make sure we've received any scheduled tasks
    world.celery.active.wait(.05) 
    # allow tasks to complete
    world.celery.idle.wait(5)
```


## Installation

Clone the latest version of ``celerytest`` from GitHub:

    $ git clone git://github.com/RentMethod/celerytest.git

You can install it by doing the following,:

    $ tar xvfz celerytest-0.1.0.tar.gz
    $ cd celerytest-0.1.0
    # python setup.py install # as root
