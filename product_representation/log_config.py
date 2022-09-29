import logging
import sys

root_logger = logging.getLogger()
root_logger.level = logging.INFO
log_handler = logging.StreamHandler(stream=sys.stdout)
file_handler = logging.FileHandler(filename='logs/prre_oz_wb.log', mode='w', encoding='utf8')
formatter = logging.Formatter(fmt='%(levelname)s | %(lineno)d | %(message)s')
log_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
root_logger.addHandler(log_handler)
root_logger.addHandler(file_handler)
log = root_logger


if __name__ == '__main__':
    print(root_logger)
    print(root_logger.handlers)
    root_logger.info('HEY')
    root_logger.error('Error')
