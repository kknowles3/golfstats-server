# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 12:40:54 2023

@author: kknow
"""

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from dev.util.app_util import get_config_val

uri = get_config_val("admin", "GSD_Server")
# uri = "mongodb+srv://<username>:<password>@golfstatsdata.qrc6r.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)