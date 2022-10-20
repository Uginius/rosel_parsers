import sys
import logging.config
from utilites import check_dir


def set_logging(log_name, mode='a', write_errors=False):
    log_dir = 'logs'
    check_dir(log_dir)
    filename = f'{log_dir}/{log_name}.log'
    dict_config = {
        "handlers": {
            'console': {
                'class': 'logging.StreamHandler', 'stream': sys.stdout,
                'level': 'INFO',
                'formatter': 'fmt_console'},
            'file': {
                'class': 'logging.FileHandler',
                'level': 'DEBUG',
                'formatter': 'fmt_file',
                'filename': filename, 'encoding': 'utf8', 'mode': mode},
        }
    }
    if write_errors:
        err_filename = f'{log_dir}/{log_name}_err.log'
        handlers = dict_config['handlers']
        handlers['errors'] = {
            'class': 'logging.FileHandler', 'level': 'DEBUG', 'formatter': 'fmt_file',
            'filename': err_filename, 'encoding': 'utf8', 'mode': 'w'}

    dict_config.update({
        "version": 1, "disable_existing_loggers": False,
        "formatters": {'fmt_file': {'format': '%(levelname)s | %(name)s | %(asctime)s | %(message)s'},
                       'fmt_console': {'format': '%(levelname)s | %(message)s'}},
        "loggers": {
            log_name: {'level': 'DEBUG',
                       'handlers': ['console', 'file', 'errors'] if write_errors else ['console', 'file']
                       }
        },
    })
    logging.config.dictConfig(dict_config)
    return logging.getLogger(log_name)
