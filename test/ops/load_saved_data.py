# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 08:39:46 2021

@author: kknow
"""

from dev.util.data_util import RemoteDataServer, RemoteDataLoader

# Connect to golf stats data cluster
db_name = 'masters2021'
rds = RemoteDataServer(db_name)
rdl = RemoteDataLoader(db_name)
# print(pymongo.version)

collection_name = 'Test'
remote_data1 = rds.load_remote_data(collection_name)
remote_data2 = rdl.load_remote_data(collection_name)

print(remote_data1==remote_data2)

# Save remote data
# This is expected to pass
# Drop object id key to avoid error for saving duplicate key
remote_data1.pop("_id")
rds.save_remote_data(remote_data1, collection_name, overwrite=False, add_timestamp=True)

