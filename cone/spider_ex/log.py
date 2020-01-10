import logging


spider_logger = logging.getLogger(__name__)


# BASIC_FORMAT = "[%(asctime)s][%(levelname)s][%(funcName)s]%(message)s" 
BASIC_FORMAT = "[%(asctime)s][%(levelname)s] %(message)s"
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)

log_console = logging.StreamHandler()
log_console.setFormatter(formatter)


spider_logger.addHandler(log_console)
spider_logger.setLevel(logging.DEBUG)

