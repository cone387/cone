import logging
from .downloader import downloader
from . import recorder
from . import spider


downloader_logger = logging.getLogger(downloader.__name__)
recorder_logger = logging.getLogger(recorder.__name__)
spider_logger = logging.getLogger(spider.__name__)


# BASIC_FORMAT = "[%(asctime)s][%(levelname)s][%(funcName)s] %(message)s" 
BASIC_FORMAT = "[%(asctime)s][%(levelname)s] %(message)s"
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)

log_console = logging.StreamHandler()
log_console.setFormatter(formatter)

downloader_logger.setLevel(logging.INFO)
recorder_logger.setLevel(logging.INFO)
spider_logger.setLevel(logging.DEBUG)

downloader_logger.addHandler(log_console)
recorder_logger.addHandler(log_console)
spider_logger.addHandler(log_console)


def add_file_hanlder(filename, encoding='utf-8'):
    f_handler = logging.FileHandler(filename, encoding=encoding)
    logger.addHandler(f_handler)

def set_level_debug():
    logger.setLevel(logging.DEBUG)

def set_level_info():
    logger.setLevel(logging.INFO)
