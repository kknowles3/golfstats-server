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

import pandas as pd
import numpy as np

team_picks_path = os.path.join(APP_PATH, 'data/2022/pga')
# ********* Update with actual picks once they are available
# team_picks_fname = '2021 UK Open Pool Selections - Test.csv'
team_picks_fname = 'PGA Picks for 2022.csv'
team_picks_skip_rows = 2 # Number of import rows to skip
db_name = 'pga2022'

# **********************************************************

def get_pool_player_names(pool_picks_df, name_cols):
    """
    Gets a distinct list of player names in the pool picks.  This can be used to
    reduce the number of team player scores that need to be updated.

    Parameters
    ----------
    pool_picks_df : TYPE
        DESCRIPTION.

    Returns
    -------
    players : TYPE
        DESCRIPTION.

    """
    
    id_list = [pool_picks_df[col] for col in pool_picks_df[name_cols]]
    
    players = pd.Series(np.sort(pd.concat(id_list).unique()))
    
    return players

def load_team_picks():
    
    fname = os.path.join(team_picks_path, team_picks_fname)
    team_picks_df = pd.read_csv(fname, index_col=False, skiprows=team_picks_skip_rows)
    team_picks_df.insert(loc=0, column='team_id', value=team_picks_df.index.values )

    return team_picks_df

def apply_pick_name_mappings(df, name_mappings, map_cols):
    '''
    In many pools, there are some name differences/inconsistencies between the names
    in the original player list and the team picks.  These can be found through an interative
    process of comparing the names in each set and creating a mapping dict from which these can be applied.

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.
    name_mappings : TYPE
        DESCRIPTION.
    map_cols : TYPE
        DESCRIPTION.

    Returns
    -------
    df : TYPE
        DESCRIPTION.

    '''

    map_df = df.copy()
    
    for col in map_cols:
        map_df[col] = map_df[col].replace(name_mappings)    
        
    
    return map_df

def save_and_reload_df(df, collection_name, orient='split', overwrite=True):

    # save df remotely
    rds.save_remote_df(df, collection_name, orient=orient, overwrite=overwrite, add_timestamp=True)
    
    # load df remotely
    df2 = rds.load_remote_df(collection_name)
    
    return df2

# orient = 'split'
# orient = 'records'
orient = 'list'
# orient = 'series'  # Not currently supported

# Save and reload tests to verify symmetry of saved and reloaded data
save_data = True
apply_mappings = True

# Get the player list df
team_picks_df = load_team_picks()

# Get the distinct list of player names in the pool picks
# These can be used to spot inconsistencies betwen the pool player list and the team picks
name_cols = team_picks_df.columns[2:]
players = get_pool_player_names(team_picks_df, name_cols)

# Apply name mappings
name_mappings = {
    'Daniel Berger ': 'Daniel Berger',
    'KH Lee': 'K.H. Lee',
    'Keegan Bradle': 'Keegan Bradley',
    'Matthew Fitzpatrick': 'Matt Fitzpatrick',
    'Sebastian Munoz': 'Sebastian Munoz',
    'Tyrell Hatton': 'Tyrrell Hatton',
    }

if apply_mappings:
    map_df = apply_pick_name_mappings(team_picks_df, name_mappings, map_cols=name_cols)
    players2 = get_pool_player_names(map_df, name_cols)

# Save player list df to remote server
if save_data:

    # Connect to golf stats data cluster
    rds = RemoteDataServer(db_name=db_name)
    # print(pymongo.version)

    df = map_df if apply_mappings else team_picks_df
    collection_name = 'pool_team_list'
    df1 = save_and_reload_df(df, collection_name, orient=orient, overwrite=True)
