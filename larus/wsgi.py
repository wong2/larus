#-*-coding:utf-8-*-

import utils
from http_parser.http import HttpStream
from http_parser.reader import SocketReader
from . import SERVER_SOFTWARE

class Headers(object):
    
    def __init__(self, request):
        self.request = request
        self._headers = []
        self.status = None

    @property
    def default_headers(self):
        req = self.request
        version = req.version()
        connection = 'keep-alive' if req.should_keep_alive() else 'close'
        default_headers = [
            'HTTP/%s.%s %s' % (version[0], version[1], self.status),
            'Server: %s' % SERVER_SOFTWARE,
            'Date: %s' % utils.http_date(),
            'Connection: %s' % connection,
        ]
        return default_headers

    def append(self, header):
        self._headers.append(header)

    def set_status(self, status):
        self.status = status

    def is_empty(self):
        return len(self._headers) == 0
    
    def __str__(self):
        headers = self.default_headers
        headers.extend(['%s: %s' % (k,v) for k, v in self._headers])
        return '\r\n'.join(headers) + '\r\n\r\n'


class Response(object):

    def __init__(self, req, client):
        self.req = req
        self.client = client
        self.headers_sent = False
        self.headers = Headers(req)
        self.content_length = None
        self.bytes_sent = 0
        self._is_chuncked = None

    def start_response(self, status, headers, exc_info=None):
        if exc_info:
            try:
                if self.headers_sent:
                    raise exc_info[0], exc_info[1], exc_info[2]
            finally:
                exc_info = None
        elif not self.headers.is_empty():
            raise AssertionError('Response headers already set')

        self.headers.set_status(status)
        for name, value in headers:
            lower_name = name.lower().strip()
            value = str(value).strip()
            if utils.is_hoppish(lower_name):
                continue
            elif lower_name == 'content-length':
                self.content_length = int(value)
            self.headers.append((name, value))

        return self.send_data

    @property
    def is_chuncked(self):
        if self._is_chuncked is not None:
            return self._is_chuncked

        if self.content_length is not None:
            chunked = False
        elif self.req.version() <= (1, 0):
            chunked = False
        elif utils.get_status_code(self.status) in (204, 304):
            chunked = False
        else:
            chunked = True
            self.headers.append(('Transfer-Encoding', 'chunked'))

        self._is_chuncked = chunked
        return chunked

    def send_data(self, data):
        self.send_headers()
        data_length = len(data)
        if self.content_length is not None:
            if self.bytes_sent >= self.content_length:
                return
            if self.bytes_sent + data_length > self.content_length:
                data_length = self.content_length - self.bytes_sent
                data = data[:data_length]
        self.bytes_sent += data_length
        self.write(data, chunked=self.is_chuncked)

    def send_headers(self):
        if self.headers_sent:
            return
        headers_str = str(self.headers)
        self.write(headers_str)
        self.headers_sent = True

    def write(self, data, chunked=False):
        if chunked:
            if isinstance(data, unicode):
                data = data.encode('utf-8')
            chunk_size = '%X\r\n' % len(data)
            data = b''.join([chunk_size, data, b'\r\n'])
        self.client.sendall(data)

    def close(self):
        if not self.headers_sent:
            self.send_headers()


def create(server, client, config):
    client.setblocking(1)
    request = HttpStream(SocketReader(client))
    environ = request.wsgi_environ()

    ''' 
    the environ produced by Python and C parser is not consistent
    we have to set some missing values here
    '''
    host, port = server.getsockname()
    environ.update({
        'SERVER_NAME': host,
        'SERVER_PORT': str(port),
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': utils.guess_scheme(environ),
        'wsgi.input': client,
        'wsgi.multithread': False,
        'wsgi.multiprocess': config['workers'] > 1,
        'wsgi.run_once': False,
        'wsgi.file_wrapper': utils.FileWrapper,
    })

    response = Response(request, client)
    
    return environ, response
