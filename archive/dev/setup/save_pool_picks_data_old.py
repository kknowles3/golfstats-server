# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 10:16:24 2021

@author: kknow

Test script for saving pool picks data to the remote data server

"""

# import datetime

import os
import pandas as pd
import numpy as np

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

def load_team_picks():
    
    fname = os.path.join(team_picks_path, team_picks_fname)
    team_picks_df = pd.read_csv(fname, index_col=False, skiprows=team_picks_skip_rows)
    team_picks_df.insert(loc=0, column='team_id', value=team_picks_df.index.values )

    return team_picks_df

def trim_names(df):
    
    df_obj = df.select_dtypes(['object'])
    
    df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())
    
    return df

def apply_name_mods(df):
    '''
    Add name mappings in cases where the pool pick data doesn't match the 
    player field data

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.

    Returns
    -------
    df : TYPE
        DESCRIPTION.

    '''
    
    name_mods = {
        'Brian Harmon': 'Brian Harman', 
        'Corey Connors': 'Corey Conners', 
        'Danny Willet': 'Danny Willett', 
        'Joran Spieth': 'Jordan Spieth',
        'Matthew Fitzpatric': 'Matt Fitzpatrick',
        'Matthew Fitzpatrick': 'Matt Fitzpatrick',
        'Seamus Power': 'Séamus Power',
        'Shane Lowery': 'Shane Lowry',
        'Sungae Im': 'Sungjae Im',
        'Tyrrel Hatton': 'Tyrrell Hatton',
        'Tyrell Hatton': 'Tyrrell Hatton',
        "Matthew Fizpatrick": 'Matt Fitzpatrick',
        "Patrick Ree": "Patrick Reed",
        "Rory Mcilroy": "Rory McIlroy",
        "Alexander Bjork": "Alexander Björk",
        "Byun Hun An": "Byeong Hun An",
        "Louie Oosthuizen": "Louis Oosthuizen",
        "Nicolai Hojgaard": "Nicolai Højgaard",
        "Joaquin Niemann": "Joaquín Niemann"

        }
    
    mod_cols = df.columns[2:]
    df[mod_cols] = df[mod_cols].replace(name_mods)
    
    return df

def get_pool_players(player_list_df):
    """
    Gets a distinct list of players in the pool.  This can be used to
    reduce the number of team player scores that need to be updated.

    Parameters
    ----------
    player_list_df : TYPE
        DESCRIPTION.

    Returns
    -------
    player_ids : TYPE
        DESCRIPTION.

    """
    
    name_lists = [player_list_df[col].dropna() for col in player_list_df.columns[2:]]
    
    pool_players = pd.Series(np.sort(pd.concat(name_lists).unique()))
    
    return pool_players

def check_matching_names(team_picks_df):
    
    # Get distinct list of pool players
    pool_players = get_pool_players(team_picks_df)
        
    # Load the espn player names
    espn_player_cname = "espn_pool_player_list"
    espn_player_df = rds.load_remote_df(collection=espn_player_cname)
    
    # Check for matching names
    player_id_map = dict(zip(espn_player_df['EspnPlayer'], espn_player_df['ID']))
    pool_player_ids = pool_players.map(player_id_map)
    check_df = pd.DataFrame(data={'pool_player':pool_players, 'espn_id': pool_player_ids})
    
    error_names = check_df[check_df['espn_id'].isnull()]['pool_player']
    
    return error_names

def save_and_reload_df(df, collection_name, orient='split', overwrite=True):

    # save df remotely
    rds.save_remote_df(df, collection_name, orient=orient, overwrite=overwrite, add_timestamp=True)
    
    # load df remotely
    df2 = rds.load_remote_df(collection_name)
    
    return df2

if __name__ == '__main__':

    #####################
    # Configuration data
    #####################
    
    team_picks_path = os.path.join(APP_PATH, 'data/2024/pga')
    # ********* Update with actual picks once they are available
    # team_picks_fname = '2021 UK Open Pool Selections - Test.csv'
    team_picks_fname = 'pool_picks.csv'
    team_picks_skip_rows = 0 # Number of import rows to skip
    db_name = 'pga2024'

    
    # Connect to golf stats data cluster
    rds = RemoteDataServer(db_name=db_name)
    # print(pymongo.version)
    
    # orient = 'split'
    # orient = 'records'
    orient = 'list'
    # orient = 'series'  # Not currently supported
    
    # Save and reload tests to verify symmetry of saved and reloaded data
    fail_on_mismatch = True
    save_data = False
    
    # Get the player list df
    team_picks_df = load_team_picks()
    print('Found {} sets of team picks'.format(len(team_picks_df)))
    
    # Trim string values
    team_picks_df = trim_names(team_picks_df)
    
    # Apply known name mods
    team_picks_df = apply_name_mods(team_picks_df)
    
    # Get distinct list of pool players
    pool_players = get_pool_players(team_picks_df)
    
    # Apply pool pick name mappings, where pool name doesn't match ESPN name
    pool_espn_map = {
        'Erik Van Rooyen': 'Erik van Rooyen',
        'JT Poston': 'J.T. Poston',
        'Ludvig Aberg': 'Ludvig Åberg',
        "Matthias Pavon": 'Matthieu Pavon',
        'Joaquin Niemann': 'Joaquín Niemann'
        }
    
    team_picks_df = team_picks_df.replace(pool_espn_map)
    
    # Check for errors
    error_names = check_matching_names(team_picks_df)
    
    if len(error_names) > 0:
        print('Found {} names with matching errors'.format(len(error_names)))
        print("\n".join(error_names.values))
        print("Unable to save team picks data")
    else:    
        print('No name matching errors found')
        # Save player list df to remote server
        if save_data:
            print('Saving {} sets of team picks'.format(len(team_picks_df)))
            df = team_picks_df
            collection_name = 'pool_team_list'
            df1 = save_and_reload_df(df, collection_name, orient=orient, overwrite=True)
            
            # Check if saved and reload match
            if df.equals(df1):
                print("Saved data matches reloaded data")
            else:
                print("Saved and reloaded data have differences, possibly different data types")

