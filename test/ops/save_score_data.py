# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 10:16:24 2021

@author: kknow

Test script for saving static data to the remote data server

"""

# import os
# import pandas as pd
# import datetime

# import pymongo
from dev.util.data_util import RemoteDataServer
# from dev.espn.espn_golf_event import EspnGolfEvent
# from dev.espn.pool_event import MastersPool

# from dev.util.app_util import APP_PATH
from components.data import ege, pool

"""
Main static data components:

    - player list.  This is a list of the players in the tournament and a mapping
    to player names in the pool. This is static data that may change prior to the 
    event starting, but otherwise static during the event.  Does not require any 
    additional metadata other than a timestamp for saving remotely.
    - pool list.  This is a list of the teams and player picks for the event.  This is
    also static once the event starts (and usually the night before the start).  This does
    not require any additional metadata other than a timestamp for saving.

Player list and pool list do not need to be managed through the scoring server.  They can
be fed once at the beginning of the event.  If there are issues or updates, the changes 
can be manually deployed from a local machine.

Dynamic data components:
    
    - player scores.
    - pool scores.
    
    

"""

def save_and_reload_data(data_to_db, collection_name, overwrite=False):

    # save df remotely
    # now = datetime.datetime.now()
    res = rds.save_remote_data(data_to_db, collection_name, overwrite=overwrite)
    
    # load df remotely
    data_from_db = rds.load_remote_data(collection_name)
    
    return data_from_db, res

# Connect to golf stats data cluster
rds = RemoteDataServer('pga2022')
# print(pymongo.version)

# orient = 'split'
# orient = 'records'
orient = 'list'
# orient = 'series'  # Not currently supported

# Get the player list df
# player_list_df = ege.player_list_df

# Get the pool list df
# pool_list_df = pool.pool_id_df

# Refresh player scores from ESPN site
player_score_df = ege.refresh_scores()
player_score_data = ege.get_player_score_data(transform_df=True)

# Save and reload tests to verify symmetry of saved and reloaded data
data_to_db = player_score_data
collection_name = 'player_score'
data_from_db1, res1 = save_and_reload_data(data_to_db, collection_name, overwrite=False)

# Recalculate pool scores
pool_score_df = pool.calc_pool_scores_df(player_score_df)
pool_score_data = pool.calc_pool_score_data(player_score_data, transform_df=True)

# Save and reload tests to verify symmetry of saved and reloaded data
data_to_db = pool_score_data
collection_name = 'pool_score'
data_from_db2, res2 = save_and_reload_data(data_to_db, collection_name, overwrite=False)


