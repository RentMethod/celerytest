from . import start_celery_worker
from celerytest.config import CELERY_TEST_CONFIG_MEMORY


class CeleryTestCaseMixin(object):
    '''
    Use to run a celery worker in the background for this TestCase.

    Worker is started and stopped on class setup/teardown.
    Use self.worker.idle.wait() to make sure tasks have stopped executing.
    '''
    celery_config = CELERY_TEST_CONFIG_MEMORY
    celery_app = None
    celery_concurrency = 1
    celery_share_worker = True

    @classmethod
    def start_worker(cls):
        return start_celery_worker(cls.celery_app,
                                   config=cls.celery_config,
                                   concurrency=cls.celery_concurrency)

    @classmethod
    def setup_class(cls):
        cls.worker = cls.start_worker()
        cls.shared_worker = cls.worker

    @classmethod
    def teardown_class(cls):
        cls.worker.stop()
        cls.worker.join()

    def setUp(self):
        if not getattr(self, 'shared_worker', False):
            self.worker = self.start_worker()

    def tearDown(self):
        if not getattr(self, 'shared_worker', False):
            self.worker.stop()
