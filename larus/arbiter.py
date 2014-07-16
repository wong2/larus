#-*-coding:utf-8-*-

import os
import sys
import signal
import logging
from multiprocessing import Process
from multiprocessing.queues import SimpleQueue
from utils import create_sockets, format_addr_str
from workers.sync import SyncWorker


class Arbiter(object):

    SIG_NAMES = dict(
        (getattr(signal, 'SIG%s' % name), name.lower())
            for name in 'TTIN TTOU TERM USR2'.split()
    )
    SIGNALS = SIG_NAMES.keys()

    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.workers = []
        self.setup()

    def setup(self):
        self.pid = os.getpid()
        self.worker_nums = self.config['workers']
        self.worker_class = SyncWorker
        self.queue = SimpleQueue()
        self.setup_logger()
        self.setup_signals()

        addresses = self.config['binds']
        self.sockets = create_sockets(addresses, self.logger)

        addresses_str = ', '.join(map(format_addr_str, addresses))
        self.logger.info('Arbiter booted')
        self.logger.info('Listening on: %s (%s)', addresses_str, self.pid)
        self.logger.info('Using worker: %s', self.worker_class)

    def setup_logger(self):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)-15s [%(process)d] [%(levelname)s] %(message)s',
                            handlers=[logging.StreamHandler()])
        self.logger = logging.getLogger(__name__)

    def setup_signals(self):
        [signal.signal(sig, self.handle_signal) for sig in self.SIGNALS]

    def handle_signal(self, signum, frame):
        self.queue.put(signum)

    def run(self):
        self.spawn_workers()
        while True:
            try:
                signum = self.queue.get() # blocking
                signame = self.SIG_NAMES.get(signum)
                handler = getattr(self, 'handle_%s' % signame, None)
                if not handler:
                    self.logger.error('No handler for signal: %s', signame)
                    continue

                self.logger.info('Handling signal: %s', signame)
                handler()
            except KeyboardInterrupt:
                self.stop()

    def stop(self):
        self.logger.info('Stopping')
        for worker in self.workers:
            self.kill_worker(worker)
        for sock in self.sockets:
            sock.close()
        sys.exit(0)

    def spawn_worker(self):
        args = (self.app, self.sockets, self.logger, self.config)
        return Process(target=self.worker_class.create, args=args)

    def spawn_workers(self):
        diff = self.worker_nums - len(self.workers)
        for n in range(diff):
            worker = self.spawn_worker()
            self.workers.append(worker)
            worker.start()
            self.logger.info('Botting worker: %s', worker.pid)

    def kill_worker(self, worker):
        self.logger.info('Killing worker: %s' % worker.pid)
        worker.terminate()
        worker.join()

    def handle_ttin(self):
        self.worker_nums += 1
        self.spawn_workers()

    def handle_ttou(self):
        if self.worker_nums <= 1:
            return

        worker = self.workers.pop(0)
        self.kill_worker(worker)
        self.worker_nums -= 1
