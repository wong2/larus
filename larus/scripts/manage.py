#-*-coding:utf-8-*-

import os
import sys
import click
from larus.arbiter import Arbiter
from larus.utils import import_app


#TODO: add worker class option
@click.command()
@click.option('--workers', '-w', default=1, help='number of workers, defaults to 1')
@click.option('--bind', '-b', multiple=True, default=(), help='address to bind: host:port, defaults to 127.0.0.1:8000')
@click.option('--chdir', '-c', default='.', help='change the working director')
@click.argument('module_app')
def main(workers, bind, chdir, module_app):
    if not bind:
        bind = ['127.0.0.1:8000']

    binds = [b.split(':') for b in bind]
    binds = [(host, int(port)) for host, port in binds]

    config = {
        'workers': workers,
        'binds': binds,
    }

    path = os.path.abspath(chdir)
    os.chdir(path)
    sys.path.insert(0, path)

    try:
        app = import_app(module_app)
    except ImportError as e:
        click.echo('[Import Application Error]: %s' % e.message)
    else:
        Arbiter(app, config).run()


if __name__ == '__main__':
    main()
