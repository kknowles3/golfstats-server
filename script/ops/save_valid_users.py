# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 13:03:38 2021

@author: kknow
"""

from dev.util.data_util import RemoteDataServer
from dev_util.app_util import get_config_val

# Connect to golf stats data cluster
db_name = 'static_data'
rds = RemoteDataServer(db_name)
# print(pymongo.version)

config_grp = 'VALID_USERS'
config_key = 'valid_user_pairs'
collection_name = 'valid_users'

valid_user_pairs = get_config_val(config_data_key=config_key, config_data_grp=config_grp)

if valid_user_pairs is not None:
    
    d = {'valid_user_pairs': valid_user_pairs}
    
    # Save remote data
    # This is expected to pass
    # Drop object id key to avoid error for saving duplicate key
    rds.save_remote_data(d, collection_name, overwrite=True, add_timestamp=True)
    
    # Load valid user pairs
    user_pairs = rds.load_remote_data_item(collection=collection_name)
    
