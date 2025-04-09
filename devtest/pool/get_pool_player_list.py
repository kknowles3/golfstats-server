# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 14:40:34 2023

@author: kknow
"""

import pandas as pd
import numpy as np

from dev.util.data_util import RemoteDataServer

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
    
    name_lists = [player_list_df[col] for col in player_list_df.columns[2:]]
    
    pool_players = pd.Series(np.sort(pd.concat(name_lists).unique()))
    
    return pool_players

if __name__ == "__main__":
    
    db_name = 'masters2023'
    rds = RemoteDataServer(db_name=db_name)

    # Load pool list
    pool_cname = 'pool_team_list'    
    pool_list_df = rds.load_remote_df(collection=pool_cname)

    pool_players = get_pool_players(pool_list_df)
    
    # Load the espn player names
    espn_player_cname = "espn_pool_player_list"
    espn_player_df = rds.load_remote_df(collection=espn_player_cname)
    
    # Check for matching names
    player_id_map = dict(zip(espn_player_df['EspnPlayer'], espn_player_df['ID']))
    pool_player_ids = pool_players.map(player_id_map)
    check_df = pd.DataFrame(data={'pool_player':pool_players, 'espn_id': pool_player_ids})
    
    error_names = check_df[check_df['espn_id'].isnull()]['pool_player']