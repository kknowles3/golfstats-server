# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 09:26:29 2021

@author: kknow

Utility script for creating capped collection that have limits on total size and 
maximum number of documents

"""

from pymongo import MongoClient
from dev.util.app_util import get_config_val
import certifi

connect_str = get_config_val("admin", "GSD_Server")
client = MongoClient(connect_str, tlsCAFile=certifi.where())

# db_name = 'masters2021'
db_name = 'masters2022'
db = client.get_database(db_name)

# Create a new capped collection for pool scores
# collection_name = 'pool_score'
# max_items = 10
# max_size = 50000 * max_items
# collection_params = {'capped':True, 'size':max_size, 'max':max_items}
# collection = db.create_collection(collection_name, **collection_params)

# Create a new capped collection for player scores
collection_name = 'player_score'
max_items = 10
max_size = 20000 * max_items
collection_params = {'capped':True, 'size':max_size, 'max':max_items}
collection = db.create_collection(collection_name, **collection_params)

# Create a new capped collection for player scores
collection_name = 'pool_score'
max_items = 100
max_size = 51200000
collection_params = {'capped':True, 'size':max_size, 'max':max_items}
collection = db.create_collection(collection_name, **collection_params)
