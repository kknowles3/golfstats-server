# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 10:58:06 2023

@author: kknow

Utility script for converting an existing collection to a capped collection.

TODO Check that max_items contraint hits before max_size. Otherwise, docs will
stop saving

https://www.tutorialspoint.com/invoke-converttocapped-and-convert-an-existing-collection-to-capped-in-mongodb

"""

from pymongo import MongoClient
from dev.util.app_util import get_config_val
from dev_util.mongo_util import create_capped_collection, convert_capped_collection
import certifi

if __name__ == "__main__":
    
    connect_str = get_config_val("admin", "GSD_Server")
    client = MongoClient(connect_str, tlsCAFile=certifi.where())
    
    # db_name = 'masters2021'
    db_name = 'pga2023'
    db = client.get_database(db_name)
    
    # Create a new capped collection for pool scores
    # collection_name = 'pool_score'
    # max_items = 10
    # max_size = 50000 * max_items
    # collection_params = {'capped':True, 'size':max_size, 'max':max_items}
    # collection = db.create_collection(collection_name, **collection_params)
    
    # Create a new capped collection for player scores
    collection_name = 'player_score'
    max_items = 1000
    max_size = 20000 * max_items
    # collection_params = {'capped':True, 'size':max_size, 'max':max_items}
    # collection = db.create_collection(collection_name, **collection_params)
    collection1 = db.get_collection(collection_name)
    if collection1 is None:
        collection1 = create_capped_collection(db=db, cname=collection_name, max_size=max_size, max_items=max_items)
    else:
        result1 = convert_capped_collection(db=db, cname=collection_name, max_size=max_size, max_items=max_items)
        # collection1 = db.get_collection(collection_name)
    stats1 = db.command("collstats", collection_name)
    
    # TODO Fix issue where max_size is the constraining factor - i.e., increase max size
    # Create a new capped collection for player scores
    collection_name = 'pool_score'
    max_items = 1000
    max_size = 60914560

    # To create a new capped collection
    # collection_params = {'capped':True, 'size':max_size, 'max':max_items}
    # collection = db.create_collection(collection_name, **collection_params)
    collection2 = db.get_collection(collection_name)
    if collection2 is None:
        collection2 = create_capped_collection(db=db, cname=collection_name, max_size=max_size, max_items=max_items)
    else:
        result2 = convert_capped_collection(db=db, cname=collection_name, max_size=max_size, max_items=max_items)
    stats2 = db.command("collstats", collection_name)
    
    # # To convert an existing collection
    # # collection_params = {'convertToCapped':collection_name, 'size':max_size, 'max':max_items}
    # # result = db.command(collection_params)
    # result = convert_capped_collection(db=db, cname=collection_name, max_size=max_size, max_items=max_items)
    # coll = db.get_collection(collection_name)
    # stats = coll.stats()

