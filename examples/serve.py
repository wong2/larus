#-*-coding:utf-8-*-

from larus.arbiter import Arbiter
from app import app


options = {
    'workers': 4,
    'binds': [('127.0.0.1', 5000)]
}

if __name__ == '__main__':
    Arbiter(app, options).run()
