# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 10:34:32 2021

@author: kknow

Utility script to create random teams for testing


"""

import os
import pandas as pd

from dev.util.app_util import APP_PATH

import random

# from components.data import ege, pool
# from components.data import EVENT_CONFIGS

"""
Main static data components:

    - espn player list.  This is a list of espn golfers in the pga event and mapped pool names

Static data lists do not need to be managed through the scoring server.  They can
be fed once at the beginning of the event.  If there are issues or updates, the changes 
can be manually deployed from a local machine.

"""

def load_player_list():
    
    fname = os.path.join(player_list_path, player_list_fname)
    player_list_df = pd.read_csv(fname, index_col=False)
    
    return player_list_df

def create_random_team(pool_names, num_players=4):
    
    n = num_players
    players = random.sample(pool_names, n)
    
    # team = {'PLAYER{}:{}'.format(i+1, player) for i,player in enumerate(players) }
    team = {}
    for i,player in enumerate(players):
        team['PLAYER {}'.format(i+1)] = player
        
    team['TIEBREAKER'] = random.sample(players, 1)[0]
    
    return team

def create_random_teams(pool_names, num_teams=10):
    
    team_names = []
    teams = []
    
    for i in range(num_teams):
        team_names.append('Team{}'.format(i+1))
        teams.append(create_random_team(pool_names))
        # team = {'TEAM NAME': 'Team{}'.format(i)}
        # team.update(create_random_team(pool_names))
        # teams.append(team)
    
    pool_teams_df =  pd.DataFrame(data=teams, index=team_names)
     
    return pool_teams_df

# *************** Set the event tag *************
# Get the event-specific configuration parameters
event_tag = 'ukopen'

# File location settings
player_list_path = os.path.join(APP_PATH, 'data/{}'.format(event_tag))
player_list_fname = 'espn_player_list_2021.csv'

# Get the player list df
player_list_df = load_player_list()

pool_names = list(player_list_df['PoolName'].values)
team = create_random_team(pool_names)
pool_teams_df = create_random_teams(pool_names)