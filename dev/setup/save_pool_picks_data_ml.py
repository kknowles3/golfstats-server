# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 19:20:05 2024

@author: kknow

Test script using fuzzy logic and string matching to find best matches between
pool picks and ESPN player names for golf tournament.

"""

import os
import pandas as pd
import numpy as np

from dev.util.data_util import RemoteDataServer
from dev.util.app_util import APP_PATH

from dev_util.pandas_util import save_df_to_csv

def load_team_picks():
    
    fname = os.path.join(team_picks_path, team_picks_fname)
    team_picks_df = pd.read_csv(fname, index_col=False, skiprows=team_picks_skip_rows)
    team_picks_df.insert(loc=0, column='team_id', value=team_picks_df.index.values )

    return team_picks_df

def trim_names(df):
    
    df_obj = df.select_dtypes(['object'])
    
    df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())
    
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

def load_espn_player_names(rds, espn_player_cname='espn_pool_player_list'):
    
    espn_player_df = rds.load_remote_df(collection=espn_player_cname)

    return espn_player_df    

def check_matching_names(team_picks_df, espn_player_df):
    
    # Get distinct list of pool players
    pool_players = get_pool_players(team_picks_df)
        
    # # Load the espn player names
    # espn_player_cname = "espn_pool_player_list"
    # espn_player_df = rds.load_remote_df(collection=espn_player_cname)
    
    # Check for matching names
    player_id_map = dict(zip(espn_player_df['EspnPlayer'], espn_player_df['ID']))
    pool_player_ids = pool_players.map(player_id_map)
    check_df = pd.DataFrame(data={'pool_player':pool_players, 'espn_id': pool_player_ids})
    
    error_names = check_df[check_df['espn_id'].isnull()]['pool_player']
    
    return error_names

def find_closest_matching_names(error_names, espn_player_df, num_matches=2, as_df=True):
    
    # https://pypi.org/project/fuzzywuzzy/
    from thefuzz import process

    espn_players = espn_player_df['EspnPlayer'].values
    
    error_matches = {}
    
    for error_name in error_names:
        matches = process.extract(error_name, espn_players, limit=num_matches)
        error_matches[error_name] = matches
        
    if as_df:
        
        df_rows = []
        for name, matches in error_matches.items():
            
            row = {
                'name': name,
                'bestMatch': matches[0][0],
                'bestScore': matches[0][1]
                }
            
            i = 1
            for match_item in matches[1:]:
                row.update({
                    'nextMatch{}'.format(i): match_item[0],
                    'nextScore{}'.format(i): match_item[1]                    
                    })
            df_rows.append(row)
            
        df = pd.DataFrame(df_rows)
        
        df = df.sort_values(by=['bestScore', 'name'], ascending=False, ignore_index=True)
        
        return df
        
    return error_matches

def apply_name_mods(pool_df, matches_df):
    
    name_mods = dict(zip(matches_df['name'], matches_df['bestMatch']))

    mod_cols = pool_df.columns[2:]
    
    pool_df[mod_cols] = pool_df[mod_cols].replace(name_mods)
    
    return pool_df

def save_and_reload_df(df, collection_name, orient='split', overwrite=True):

    # save df remotely
    rds.save_remote_df(df, collection_name, orient=orient, overwrite=overwrite, add_timestamp=True)
    
    # load df remotely
    df2 = rds.load_remote_df(collection_name)
    
    return df2

if __name__ == "__main__":
    
    team_picks_path = os.path.join(APP_PATH, 'data/2024/ukopen')
    team_picks_fname = 'pool_picks.csv'
    name_corrections_fname = 'pool_pick_corrections.csv'
    team_picks_skip_rows = 0 # Number of import rows to skip
    db_name = 'ukopen2024'
    
    # orient = 'split'
    # orient = 'records'
    orient = 'list'
    # orient = 'series'  # Not currently supported

    save_data = True

    # Initialize the data server
    rds = RemoteDataServer(db_name=db_name)

    # Get the player list df
    team_picks_df = load_team_picks()
    print('Found {} sets of team picks'.format(len(team_picks_df)))

    # Trim string values
    team_picks_df = trim_names(team_picks_df)

    # # Apply known name mods
    # team_picks_df = apply_name_mods(team_picks_df)
    
    # Get distinct list of pool players
    pool_players = get_pool_players(team_picks_df)
    print("There are {} distinct players across the pool picks".format(len(pool_players)))
    
    #Get the ESPN player list
    espn_player_df = load_espn_player_names(rds)
    
    # Check for errors and name mismatches
    error_names = check_matching_names(team_picks_df, espn_player_df)
    if len(error_names) > 0:
        print("There are {} names with matching errors".format(len(error_names)))
        print("\n".join(error_names.values))

    else:    
        print('No name matching errors found')
        
    # Find closest player name matches in ESPN list
    matches_df = find_closest_matching_names(
        error_names, 
        espn_player_df, 
        num_matches=2)

    print(matches_df[['name', 'bestMatch', 'bestScore']])
    
    # Check for user confirmation to save best matches
    choice = input('Apply best match name corrections? Press Y or y to confirm: ')
    if choice.upper() == 'Y':

        # Apply name corrections
        print("Applying {} name corrections".format(len(matches_df)))
        mod_pool_df = apply_name_mods(
            pool_df=team_picks_df, 
            matches_df=matches_df)

        # Re-check for mismatches
        error_names = check_matching_names(team_picks_df, espn_player_df)
        if len(error_names) > 0:
            print("There are {} names with matching errors".format(len(error_names)))
            print("\n".join(error_names.values))
    
        else:    
            print('No name matching errors found after modifications')
    
    if save_data:
        
        # Check for user confirmation to save best matches
        choice = input('Save best match name corrections? Press Y or y to confirm: ')
        if choice.upper() == 'Y':

            print("Saving {} name corrections locally".format(len(matches_df)))

            # Save locally
            save_df_to_csv(
                df=matches_df,
                path=team_picks_path,
                fname=name_corrections_fname)

            print('Saving {} sets of team picks'.format(len(team_picks_df)))
            df = team_picks_df
            collection_name = 'pool_team_list'
            df1 = save_and_reload_df(df, collection_name, orient=orient, overwrite=True)
            
            # Check if saved and reload match
            if df.equals(df1):
                print("Saved data matches reloaded data")
            else:
                print("Saved and reloaded data have differences, possibly different data types")
            
            # Apply name corrections
            
            # with open(os.path.join(path, fname), 'wb') as output_file:
            #     pickle.dump(obj, output_file, pickle.HIGHEST_PROTOCOL)   
        else:
            print('Save cancelled by user')
            # return False
        
    