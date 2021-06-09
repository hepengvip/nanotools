import sys
import os
import os.path
import logging
import logging.config
import tornado.log

from nanotools.common import ensure_dir


FMT = "[%(asctime)s][%(levelname)s] - %(filename)s:%(lineno)s - %(message)s"


SERVER_LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": FMT,
                "encoding": "utf-8"
            }
        },
        "handlers": {
            "nanotools": {
                "level": "DEBUG",
                "filters": None,
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": "./logs/nanotools.log",
                "formatter": "default",
                "encoding": "utf-8",
                "when": "D"
            }
        },
        "loggers": {
            "nanotools": {
                "handlers": [
                    "nanotools"
                ],
                "level": "DEBUG",
                "encoding": "utf-8",
                "propagate": True
            }
        }
    }


# 创建日志目录
log_path = os.path.join('.', 'logs')
if not ensure_dir(log_path, create=True):
    raise RuntimeError(f'Could not create logdir: {log_path}')

if SERVER_LOGGING_CONFIG:
    logging.config.dictConfig(SERVER_LOGGING_CONFIG)
tornado.log.enable_pretty_logging()

logger = logging.getLogger('nanotools')

stdout_handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(stdout_handler)
