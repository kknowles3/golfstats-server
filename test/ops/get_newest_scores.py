# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 09:26:29 2021

@author: kknow

Utility script for creating capped collection that have limits on total size and 
maximum number of documents

"""

from pymongo import MongoClient, DESCENDING
from dev.util.app_util import get_config_val
from dev.util.data_util import RemoteDataServer

connect_str = get_config_val("admin", "GSD_Server")
client = MongoClient(connect_str)

db_name = 'masters2021'
db = client.get_database(db_name)

collection_name = 'player_score'
collection = db.get_collection(collection_name)

# Get newest item from collection
# data_from_db = collection.find().sort('last_update', pymongo.DESCENDING).limit(1)
data_from_db = collection.find_one(sort=[('last_update', DESCENDING)])

# Testing remote data server
rds = RemoteDataServer(db_name, connect_str)
find_kwargs = {'sort': [('last_update', DESCENDING)]}
data_from_db2 = rds.load_remote_data_item(collection_name, find_kwargs=find_kwargs)

# Testing multiple data items
data_items = rds.load_remote_data_items(collection_name, find_kwargs=find_kwargs)

# Get list of update datetimes
find_kwargs = {'projection':['last_update'], 'sort': [('last_update', DESCENDING)]}
last_updates = rds.load_remote_data_items(collection_name, find_kwargs=find_kwargs)

# Get list of recent updates
find_kwargs = {'projection':{'_id':False, 'last_update':True, 'status_tag':True}, 'sort': [('last_update', DESCENDING)]}
last_updates2 = rds.load_remote_data_items(collection_name, find_kwargs=find_kwargs)