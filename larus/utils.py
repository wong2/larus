#-*-coding:utf-8-*-

import sys
import time
import errno
import socket
from email.utils import formatdate


class FileWrapper(object):

    def __init__(self, filelike, blksize=8192):
        self.filelike = filelike
        self.blksize = blksize
        if hasattr(filelike, 'close'):
            self.close = filelike.close

    def __getitem__(self, key):
        data = self.filelike.read(self.blksize)
        if data:
            return data
        raise IndexError


def import_app(module_app):
    splitter = module_app.split(':')
    if len(splitter) == 1:
        module_name, app_name = splitter[0], 'application'
    else:
        module_name, app_name = splitter[:2]
    
    try:
        __import__(module_name)
    except ImportError:
        raise

    module = sys.modules[module_name]
    app = getattr(module, app_name, None)
    if app is None:
        raise ImportError('Failed to find application object from: %r' % module)
    if not callable(app):
        raise ImportError('Application object must be callable')
    return app


def create_tcp_socket(addr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) 
    sock.bind(addr)
    sock.setblocking(0)
    sock.listen(1024) # The maximum number of pending connections.
    return sock


def create_sockets(address_list, logger):
    socks = []
    for address in address_list:
        sock = None
        try:
            sock = create_tcp_socket(address)
        except socket.error as e:
            if e.args[0] == errno.EADDRINUSE:
                logger.error('Address in use: %s', address)
            elif e.args[0] == errno.EADDRNOTAVAIL:
                logger.error('Invalid address: %s', address)
                sys.exit(1)
        if sock is None:
            logger.error('Can not connect to %s', address)
            sys.exit(1)

        socks.append(sock)

    return socks


def format_addr_str(address):
    return '%s:%s' % address


def guess_scheme(environ):
    if environ.get('HTTP_X_FORWARDED_PROTOCOL', '').lower() == "ssl":
        return 'https'
    elif environ.get('HTTP_X_FORWARDED_SSL', '').lower() == "on":
        return 'https'
    else:
        return 'http'


def get_status_code(status):
    '''extract status code from status string
       200 OK -> 200
    '''
    code, text = status.strip().split()
    return int(code)


hop_headers = set('''
    connection keep-alive proxy-authenticate 
    proxy-authorization te trailers
    transfer-encoding upgrade'''.split())

def is_hoppish(name):
    return name.lower().strip() in hop_headers


def http_date(timestamp=None):
    if timestamp is None:
        timestamp = time.time()
    return formatdate(timestamp, localtime=False, usegmt=True)
