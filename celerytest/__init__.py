from config import CELERY_TEST_BACKEND_CONFIG, CELERY_TEST_CONFIG
from worker import CeleryWorkerThread

def setup_celery_worker(app, config='memory', concurrency=1):
    backend_conf = CELERY_TEST_BACKEND_CONFIG[config]
    conf = dict(CELERY_TEST_CONFIG.__dict__.items() + backend_conf.__dict__.items())
    conf['CELERYD_CONCURRENCY'] = concurrency
    if concurrency > 1:
        del conf['CELERYD_POOL']
    app.config_from_object(conf)

def start_celery_worker(app, config='memory', concurrency=1):
    setup_celery_worker(app, config=config, concurrency=concurrency)

    worker = CeleryWorkerThread(app)
    worker.daemon = True
    worker.start()
    worker.ready.wait()
    return worker
