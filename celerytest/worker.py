import threading
import socket
from celery import signals, states

class CeleryWorkerThread(threading.Thread):
    '''
    Thread that runs a celery worker while monitoring its state.

    Useful for testing purposes. Use the idle and active signals
    to wait for tasks to complete.
    '''
    def __init__(self, app):
        super(CeleryWorkerThread, self).__init__()

        self.app = app
        self.workers = []
        self.monitor = CeleryMonitorThread(app)

        self.ready = threading.Event()
        self.active = self.monitor.active
        self.idle = self.monitor.idle

    def on_worker_init(self, sender=None, **kwargs):
        self.workers.append(sender)

    def on_worker_ready(self, sender=None, **kwargs):
        if not self.ready.is_set():
            self.ready.set()
        
    def run(self):
        signals.worker_init.connect(self.on_worker_init)
        signals.worker_ready.connect(self.on_worker_ready)

        self.monitor.daemon = self.daemon
        self.monitor.start()

        worker = self.app.Worker()
        worker.run()

    def stop(self):
        self.monitor.shutdown()
        
        for w in self.workers:
            w.terminate()
        
        signals.worker_init.disconnect(self.on_worker_init)
        signals.worker_ready.disconnect(self.on_worker_ready)

class CeleryMonitorThread(threading.Thread):
    '''
    Monitors a Celery app. Keeps track of pending tasks.
    Exposes idle and active events.
    '''
    
    def __init__(self, app):
        super(CeleryMonitorThread, self).__init__()

        self.app = app
        self.state = app.events.State()
        self.stop = False

        self.pending = 0
        self.idle = threading.Event()
        self.idle.set()
        self.active = threading.Event()

    def on_event(self, event):
        # maintain state
        self.state.event(event)
        
        # keep track of active task count
        if event['type'] == 'task-received':
            self.pending += 1
        elif event['type'] in ['task-succeeded','task-failed','task-revoked']:
            self.pending -= 1
        
        active = self.pending > 0
        # we might become inactive with tasks scheduled in future
        if event['type'] == 'worker-heartbeat' and event.get('active',-1) == 0:
            active = False

        # switch signals if needed
        if active and self.idle.is_set():
            self.idle.clear()
            self.active.set()
        elif not active and self.active.is_set():
            self.idle.set()
            self.active.clear()

    @property
    def pending_tasks(self):
        tasks = self.state.tasks.values()
        return [t for t in tasks if t.state in states.UNREADY_STATES]

    def run(self):
        with self.app.connection() as connection:
            recv = self.app.events.Receiver(connection, handlers={
                '*': self.on_event,
            })

            # we want to be able to stop from outside
            while not self.stop:
                try:
                    # use timeout so we can monitor if we should stop
                    recv.capture(limit=None, timeout=.2, wakeup=True)
                except socket.timeout:
                    pass

    def shutdown(self):
        self.stop = True
        self.join()
                
