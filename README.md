Larus
----------------

### Introduction

Larus is a simplified Gunicorn clone, I wrote this cause I'm boring.

### Install

`pip intsall larus`

### Usage

    Usage: larus [OPTIONS] MODULE_APP

    Options:
      -w, --workers INTEGER  number of workers, default: 1
      -b, --bind TEXT        address to bind: host:port, default: 127.0.0.1:8000
      -c, --chdir TEXT       change the working director
      --help                 Show this message and exit.

For example, if `myapp.py` contains wsgi app: `app`, we can serve it with larus with:

    larus myapp:app

with `4` workers and bind to `0.0.0.0:5000`:

    larus -w 4 -b 0.0.0.0:5000 myapp:app
