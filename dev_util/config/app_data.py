# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 09:46:03 2022

@author: kknow
"""

from dev_util.app_util import init_app_logger

def get_logger(app_name):

    logFormat = '[%(levelname)s %(name)s] %(message)s'
    logger = init_app_logger(app_name, logFormat)
    
    # handler = logging.StreamHandler(stream=sys.stdout)
    # formatter = logging.Formatter('[%(levelname)s %(name)s] %(message)s')
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)

    return logger

# Cached variable for app logger
APP_NAME = 'dev-util'
logger = get_logger(app_name=APP_NAME)