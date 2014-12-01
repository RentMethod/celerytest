class CELERY_TEST_CONFIG(object):
    CELERY_SEND_EVENTS = True
    CELERYD_POOL = 'threads'
    CELERYD_CONCURRENCY = 1
    CELERYD_HIJACK_ROOT_LOGGER = False
    CELERYD_LOG_FORMAT = "%(message)s"

class CELERY_TEST_CONFIG_MEMORY(object):
    BROKER_URL = 'memory://'
    BROKER_TRANSPORT_OPTIONS = {'polling_interval': .01}
    CELERY_RESULT_BACKEND = "cache"
    CELERY_CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

class CELERY_TEST_CONFIG_AMQP(object):
    BROKER_URL = 'amqp://'
    CELERY_RESULT_BACKEND = "amqp"
    CELERY_DEFAULT_QUEUE = 'test_default'
    CELERY_DEFAULT_EXCHANGE = 'test_default'
    CELERY_RESULT_EXCHANGE = 'test_celeryresults'
    CELERY_BROADCAST_QUEUE = 'test_celeryctl'
