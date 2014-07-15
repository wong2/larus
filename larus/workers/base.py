#-*-coding:utf-8-*-

import os
import sys
import signal

class BaseWorker(object):

    def __init__(self, app, sockets, logger, config, timeout=30):
        self.app = app
        self.sockets = sockets
        self.logger = logger
        self.config = config
        self.timeout = timeout
        self.alive = True

        signal.signal(signal.SIGINT, self.handle_int)

    def __str__(self):
        return '<Worker %s>' % self.pid

    @property
    def pid(self):
        return os.getpid()

    def handle_int(self, sig, frame):
        self.alive = False
        sys.exit(1)

    @classmethod
    def create(cls, app, sockets, logger, config):
        worker = cls(app, sockets, logger, config)
        worker.run()

    def run(self):
        raise NotImplemented()
