# -*- coding: utf-8 -*-
"""
Created on Sat Feb  6 10:57:03 2021

@author: kknow

Collection of application-level utilities

"""

import os
# import math
import json
import pytz
# import datetime as dt
import logging

# Setting for Heroku environment
# TODO Generalize - consider adding Heroku environment variable
APP_PATH = os.environ.get('APP_PATH', os.getcwd())

# TODO Move this to config vars
# BASE_TIME_ZONE = 'UTC'
RPT_TIME_ZONE_TAG = 'America/New_York'
BASE_TZ = pytz.utc
RPT_TZ = pytz.timezone(RPT_TIME_ZONE_TAG)

# Initialize the app logger
def init_app_logger(app_name, logFormat=None):

    # Initialize app logger
    # https://realpython.com/python-logging/
    # logFormatter = '%(asctime)s - %(funcName)s - %(levelname)s - %(message)s'
    logFormat = '%(asctime)s - %(levelname)s - %(message)s' if logFormat is None else logFormat
    dateFormat = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(format=logFormat, datefmt=dateFormat, level=logging.INFO)
    
    # TODO Do we need this?
    logging.getLogger("requests").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.INFO)
    
    logger = logging.getLogger(app_name)
    # logger.setLevel(logging.INFO)
    
    return logger

# TODO Convert these datetime and timezone methods into a consolidated class

# Standalone utility method to get the value of a configuration item
# TODO Convert this into a generic configuration utility for broader reuse
# TODO Add error handling if config value isn't found
def get_config_val(config_data_key, config_data_grp=None, config_fname='config.json'):
    fname = config_fname  # default configuration data file
    env_var_name = config_data_key
    
    config_val = None
    
    # Check if file exists
    file_exists = os.path.isfile(fname)
    if file_exists:
        with open(fname, "r") as jsonfile:
            data = json.load(jsonfile) # Reading the file
            # print("Read successful")
            jsonfile.close()
            if config_data_grp is None:
                config_val = data.get(config_data_key, None)
            else:
                d = data.get(config_data_grp, None)                
                if d is not None:
                    config_val = d.get(config_data_key, None)
                else:
                    # TODO Convert to logger
                    print("Invalid or missing config_data_grp: {}".format(config_data_grp))
    else:
        # If not, check environment config
        # print("File: {} not found".format(fname))
        # print("Checking for configuration variables")
        config_val = os.getenv(env_var_name, None)

    return config_val

