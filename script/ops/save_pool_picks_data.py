# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 10:16:24 2021

@author: kknow

Test script for saving pool picks data to the remote data server

"""

# import datetime

import os
import pandas as pd

from dev.util.data_util import RemoteDataServer
from dev.util.app_util import APP_PATH

# from components.data import ege, pool

"""
Main static data components:

    - pool picks data.  This is a list of each team's picks for the pga event

Static data lists do not need to be managed through the scoring server.  They can
be fed once at the beginning of the event.  If there are issues or updates, the changes 
can be manually deployed from a local machine.

**** Note that this is the testing implementation that reuses the Master Pool picks.
It will be updated with the actual picks once they are submitted.

"""

team_picks_path = os.path.join(APP_PATH, 'data/2022/pga')
# ********* Update with actual picks once they are available
# team_picks_fname = '2021 UK Open Pool Selections - Test.csv'
team_picks_fname = 'PGA Picks for 2022.csv'
team_picks_skip_rows = 2 # Number of import rows to skip
db_name = 'pga2022'

# **********************************************************

def load_team_picks():
    
    fname = os.path.join(team_picks_path, team_picks_fname)
    team_picks_df = pd.read_csv(fname, index_col=False, skiprows=team_picks_skip_rows)
    team_picks_df.insert(loc=0, column='team_id', value=team_picks_df.index.values )

    return team_picks_df

def save_and_reload_df(df, collection_name, orient='split', overwrite=True):

    # save df remotely
    rds.save_remote_df(df, collection_name, orient=orient, overwrite=overwrite, add_timestamp=True)
    
    # load df remotely
    df2 = rds.load_remote_df(collection_name)
    
    return df2

# Connect to golf stats data cluster
rds = RemoteDataServer(db_name=db_name)
# print(pymongo.version)

# orient = 'split'
# orient = 'records'
orient = 'list'
# orient = 'series'  # Not currently supported

# Save and reload tests to verify symmetry of saved and reloaded data
save_data = True

# Get the player list df
team_picks_df = load_team_picks()

# Save player list df to remote server
if save_data:
    df = team_picks_df
    collection_name = 'pool_team_list'
    df1 = save_and_reload_df(df, collection_name, orient=orient, overwrite=True)
