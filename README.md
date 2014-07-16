Larus: A WSGI HTTP Server [WIP]
--------------------------

### Introduction

Larus is a simplified Gunicorn clone

### Install

From PyPI:

    $ pip install larus

From source:

    $ python setup.py install

### Usage

    Usage: larus [OPTIONS] MODULE_APP

    Options:
      -w, --workers INTEGER  number of workers, default: 1
      -b, --bind TEXT        address to bind: host:port, default: 127.0.0.1:8000
      -c, --chdir TEXT       change the working director
      --help                 Show this message and exit.

For example, if `myapp.py` contains the wsgi app `app`, we can serve it with larus with:

    larus myapp:app

with `4` workers and bind to `0.0.0.0:5000`:

    larus -w 4 -b 0.0.0.0:5000 myapp:app

### Signals

You can use signals to dynamically increment or decrement the number of workers while serving:

* `TTIN`: Increment the number of workers by one
* `TTOU`: Decrement the number of workers by one

### Performance

In my simple benchmark using `ab`, Larus performs better than Gunicorn both running 4 sync workers.
Perhaps benefits from the C http parser Larus using.

TODO: add detailed comparison.

### TODO

* Add more worker types
