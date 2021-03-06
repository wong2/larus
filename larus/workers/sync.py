#-*-coding:utf-8-*-

import errno
import select
import socket
from http_parser.http import NoMoreData
from larus import wsgi
from larus.workers.base import BaseWorker


class SyncWorker(BaseWorker):

    def run(self):
        [sock.setblocking(0) for sock in self.sockets]
        while True:
            readables, _, _ = select.select(self.sockets, [], [], self.timeout)
            for sock in readables:
                client = None
                try:
                    client, addr = sock.accept()
                except socket.error as e:
                    if client and hasattr(client, 'close'):
                        client.close()
                    if e.args[0] not in (errno.EAGAIN,):
                        raise
                else:
                    self.handle(sock, client, addr)

    def handle(self, server, client, addr):
        try:
            environ, response = wsgi.create(server, client, self.config)
        except NoMoreData:
            client.close()

        result = None
        try:
            result = self.app(environ, response.start_response)
            for data in result:
                response.send_data(data)
        except Exception as e:
            raise e
        finally:
            response.close()
            client.close()
            if hasattr(result, 'close'):
                result.close()
