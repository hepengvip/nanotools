from celery import Celery
from tornado import ioloop
from tornado.options import define, options, parse_command_line
from tornado.web import Application

import sys
sys.path.append('.')

from nanotools import celery_config  # NOQA
from nanotools.common.urls import get_web_apis  # NOQA
from nanotools.common.config import app_config  # NOQA
from nanotools.common.logging import logger  # NOQA


def makeup_webapp(**kwargs):
    logger.info(f'makeup webapp with {kwargs}')
    app = Application(get_web_apis(), **kwargs)
    return app


def start_webapp():
    define('debug', default=False, type=bool, help='Enable debug mode')
    define('autoreload', default=False, type=bool, help='Enable autoreload')
    define(
        'gzip', default=True, type=bool,
        help='Applies the gzip content encoding to the response')
    try:
        parse_command_line()
        webapi_addr = app_config['webapi_addr']
        webapp = makeup_webapp(
            debug=options.debug,
            autoreload=options.autoreload,
            gzip=options.gzip,
        )
        webapp.listen(**webapi_addr)
        loop = ioloop.IOLoop.current()
        loop.start()
    except KeyboardInterrupt:
        loop.stop()


def makeup_celeryapp():
    app = Celery()
    app.config_from_object(celery_config)
    return app


celery_app = makeup_celeryapp()


if __name__ == '__main__':
    start_webapp()
