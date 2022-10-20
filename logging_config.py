import sys
import logging.config
from utilites import check_dir


def set_logging(log_name):
    log_dir = 'logs'
    check_dir(log_dir)
    filename = f'{log_dir}/{log_name}.log'
    dict_config = {
        "version": 1, "disable_existing_loggers": False,
        "formatters": {'fmt_file': {'format': '%(levelname)s | %(name)s | %(asctime)s | %(message)s'},
                       'fmt_console': {'format': '%(levelname)s | %(message)s'}},
        "handlers": {'console': {'class': 'logging.StreamHandler', 'stream': sys.stdout, 'level': 'INFO',
                                 'formatter': 'fmt_console'},
                     'file': {'class': 'logging.FileHandler', 'formatter': 'fmt_file', 'level': 'DEBUG',
                              'filename': filename, 'encoding': 'utf8', 'mode': 'a'}},
        "loggers": {log_name: {'level': 'DEBUG', 'handlers': ['console', 'file']}},
    }
    logging.config.dictConfig(dict_config)
    return logging.getLogger(log_name)
