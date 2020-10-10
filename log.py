import os

import logging
from logging.handlers import RotatingFileHandler

from config import config


def setup_logger(console=False):
    """
    Setup logger
    Args:
        console - True: enable log output to console
    
    Returns:
        logger
    """
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
    logger = logging.getLogger('vm_processor')
    logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(os.path.join(config['LOG']['DIR'], 'homelab-control.log'), maxBytes=1024 * 1024 * 100, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    if console:
        logger.addHandler(console_handler)

    return logger


HomelabLogger = setup_logger()
