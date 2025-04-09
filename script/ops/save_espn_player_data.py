# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 10:16:24 2021

@author: kknow

Test script for saving espn player data to the remote data server

"""

# import datetime

import os
import pandas as pd

from dev.util.data_util import RemoteDataServer
from dev.util.app_util import APP_PATH

# from components.data import ege, pool
# from components.data import EVENT_CONFIGS

"""
Main static data components:

    - espn pga player list.  This is a list of espn golfers in the pga event and mapped pool names

Static data lists do not need to be managed through the scoring server.  They can
be fed once at the beginning of the event.  If there are issues or updates, the changes 
can be manually deployed from a local machine.

"""

def load_player_list():
    
    fname = os.path.join(player_list_path, player_list_fname)
    player_list_df = pd.read_csv(fname, index_col=False)
    
    return player_list_df

# Note that last names were generated externally for the pga event
def get_last_name(name):
    return name.split(" ")[-1]
    
def get_last_names(df, name_col='PoolName'):
    last_names = df[name_col].apply(lambda x: get_last_name(x))
    return last_names

def save_and_reload_df(df, collection_name, orient='split', overwrite=True):

    # save df remotely
    # now = datetime.datetime.now()
    # rds.save_remote_df(df, collection_name, orient=orient, meta_tags={'save_timestamp': now}, overwrite=overwrite)
    rds.save_remote_df(df, collection_name, orient=orient, overwrite=overwrite, add_timestamp=True)
    
    # load df remotely
    df2 = rds.load_remote_df(collection_name)
    
    return df2

# *************** Set the event tag *************
# Get the event-specific configuration parameters
event_tag = 'usopen'
db_name = 'usopen2021'

# File location settings
# TODO Consider moving this to the event configuration data
player_list_path = os.path.join(APP_PATH, 'data/{}'.format(event_tag))
player_list_fname = 'espn_player_list_2021.csv'

# Connect to golf stats data cluster
rds = RemoteDataServer(db_name=db_name)
# print(pymongo.version)

orient = 'split'
# orient = 'records'
# orient = 'list'
# orient = 'series'  # Not currently supported

# # Refresh player scores from ESPN site
# player_score_df = ege.load_player_scores()
# player_score_data = ege.load_player_score_data(transform_df=False)

# # pool = MastersPool()
# pool_score_df = pool.calc_pool_scores_df(player_score_df)
# pool_score_data = pool.calc_pool_score_data(player_score_data)

# Save and reload tests to verify symmetry of saved and reloaded data
save_data = True

# Get the player list df
# player_list_df = ege.player_list_df
player_list_df = load_player_list()
# last_names = get_last_names(player_list_df)
# player_list_df['LastName'] = last_names

# ********* Manual overrides for last name reporting **************
# Add manual overrides for Johnsons
# TODO consider moving this into the configuration data
# player_list_df.loc[player_list_df.PoolName == 'Dustin Johnson', 'LastName'] = 'Johnson, D.'
# player_list_df.loc[player_list_df.PoolName == 'Zach Johnson', 'LastName'] = 'Johnson, Z.'
# player_list_df.loc[player_list_df.PoolName == 'Michael Johnson', 'LastName'] = 'Johnson, M.'
last_name_edits = [
    # (PoolName, LastName)
    ('Dustin Johnson', 'Johnson, D'),
    ('Zach Johnson', 'Johnson, Z'),
    ('Michael Johnson', 'Johnson, M'),
    ('Eduardo Molinari', 'Molinari, E'),
    ('Francesco Molinari', 'Molinari, F'),
    ('Alvaro Ortiz', 'Ortiz, A'),
    ('Carlos Ortiz', 'Ortiz, C'),
    ('Cameron Smith', 'Smith, C'),
    ('Jordan Smith', 'Smith, J'),
    ('Chan Kim', 'Kim, C'),
    ('Si Woo Kim', 'Kim, SW'),
    ]

for pool_name, last_name in last_name_edits:
    player_list_df.loc[player_list_df.PoolName == pool_name, 'LastName'] = last_name

# Save player list df to remote server
if save_data:
    df = player_list_df
    collection_name = 'espn_player_list'
    df1 = save_and_reload_df(df, collection_name, orient=orient, overwrite=True)

# Get the pool list df
# pool_list_df = pool.pool_id_df
# df = pool_list_df
# collection_name = 'pool_team_list'
# df2 = save_and_reload_df(df, collection_name, orient=orient, overwrite=True)

# df = player_score_df
# collection_name = 'player_score'
# df3 = save_and_reload_df(df, collection_name, orient=orient, overwrite=True)

# df = pool_score_df
# collection_name = 'pool_score'
# df4 = save_and_reload_df(df, collection_name, orient=orient, overwrite=True)

