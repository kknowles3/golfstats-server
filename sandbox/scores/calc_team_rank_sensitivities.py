# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 10:22:23 2023

@author: kknow

Test script for calculating team rank sensitivities with respect to player
scores over a range of standard scoring scenarios (e.g., eagle, birdie, bogey,
double bogey, triple bogey)

"""

import pandas as pd

from components.app_data import EVENT_CONFIGS
from dev.espn.pool_event import PoolEventScorer
from dev_util.mongo_util import MongoDataServer

from sandbox.scores.calc_score_scenario import ScoreResetter

from dev_util.gen_util import calc_function_time

@calc_function_time
def calc_team_rank_sensitivities(pool, pool_player_score_df):
    
    # TODO Consider standard deviation shocks based on remaining scores, which incorporates number of holes remaining
    # display(scen_pool_player_score_df)
    
    # Current player scores for active players who haven't finished the round
    active_pool_player_score_df = scen_pool_player_score_df[scen_pool_player_score_df['MadeCut']]
    
    active_players = active_pool_player_score_df['PLAYER']
    active_player_ids = active_pool_player_score_df['PlayerId']
    
    current_player_scores= list(active_pool_player_score_df['ParScore'].values)
    shock_pool_player_score_df = active_pool_player_score_df.copy()
    
    score_shocks = {
        'Eagle': -2,
        'Birdie': -1,
        'Bogey': 1,
        'DoubleBogey': 2,
        'TripleBogey': 3
    }
    
    # Loop through players and generate score shocks
    # TODO Consider whether to do all calculations in a loop or pre-generate full set of shocks
    shock_player_score_data = []
    key_col = 'team_id'
    val_col = 'Rank'
     
    for i, (player, pid, score) in enumerate(zip(active_players, active_player_ids, current_player_scores)):
        
        # d = dict(
        #         player = player,
        #         current_score = score,
        #         label = 'current',
        #         score_shock = 0,
        #         team_ranks = dict(zip(scen_pool_score_df[key_col], scen_pool_score_df[val_col]))
        #     )
        # shock_player_score_data.append(d)
        
        di = dict(
            player = player,
            playerId = pid,
            current_score = score
            )

        dj = {}        
        for label, score_shock in score_shocks.items():
            shock_player_scores = current_player_scores.copy()
            shock_player_scores[i] += score_shock
            
            # Update shocked player score
            shock_pool_player_score_df['ParScore'] = shock_player_scores
            
            # Recalc team scores
            shock_pool_score_df = pool.calc_pool_scores_df(shock_pool_player_score_df)
            
            # Keep subset of the data
            
            dj[label] = dict(
                score_shock = score_shock,
                team_ranks = dict(zip(shock_pool_score_df[key_col], shock_pool_score_df[val_col]))
                )
            
            di['score_shocks'] = dj

        shock_player_score_data.append(di)
    
        # display(pd.DataFrame(shock_player_score_data))
        
    return shock_player_score_data

@calc_function_time
def create_rank_sensitivity_df(pool_score_df, shock_player_score_data):

    current_team_score = pool_score_df.loc[team_id]['Rank']
    # print(current_team_score)
    
    team_rows = []
    for d in shock_player_score_data:
        
        player = d['player']
        player_id = d['playerId']
        player_score = d['current_score']
        score_shocks = d['score_shocks']
        
        for label, di in score_shocks.items():
            
            dj = {
                'team_id': team_id,
                'player_id': player_id,
                'player': player,
                'player_score': player_score,
                'scenario': label,
                'team_ranks': di['team_ranks'].get(team_id)
            }
        
            team_rows.append(dj)
    
    df = pd.DataFrame(team_rows)
    df['team_rank_chg'] =  (current_team_score - df['team_ranks']).astype(int)
    
    # Filter for non-zero results
    df = df[abs(df['team_rank_chg']) > 1e-6]
    df = df.sort_values(by='team_rank_chg', ascending=False).reset_index(drop=True)
    
    return df
    
@calc_function_time
def filter_sensitivity_results(pool, team_id, rank_sensitivity_df):
    
    # Get player_ids for team
    pid_cols = ['P{}_ID'.format(i) for i in [1,2,3,4]]
    team_player_ids = list(pool.pool_id_df[pool.pool_id_df['team_id'] == team_id][pid_cols].values)[0]
    
    df = rank_sensitivity_df
    
    team_df = df[df['player_id'].isin(team_player_ids)]
    opp_df = df[~df['player_id'].isin(team_player_ids)]
    
    # help_df = df[df['team_rank_chg'] > 0]
    # hurt_df = df[df['team_rank_chg'] < 0]
    
    # Create a simple pivot view
    pivot_cols = ['player', 'player_score'] + ['Eagle', 'Birdie', 'Bogey', 'DoubleBogey', 'TripleBogey']
    
    team_pivot_df = team_df.pivot(index=['player', 'player_score'], columns='scenario', values='team_rank_chg').fillna("-").reset_index()
    team_pivot_df = team_pivot_df[pivot_cols]
    
    opp_pivot_df = opp_df.pivot(index=['player', 'player_score'], columns='scenario', values='team_rank_chg').fillna("-").reset_index()
    opp_pivot_df = opp_pivot_df[pivot_cols]

    results = {
        'teamPlayers': team_pivot_df,
        'oppPlayers': opp_pivot_df
        }
    
    return results
    
if __name__ == "__main__":
    
    team_id = 87

    event_tag = 'usopen2023'
    filter_cuts = True
    
    event_config = EVENT_CONFIGS.get(event_tag)
    event_id = event_config.get('event_id')
    
    stats = ScoreResetter(event_id)
    
    db_name = event_config['db_name']
    
    mds = MongoDataServer(db_name=db_name)
    pool = PoolEventScorer(mds)

    # Create pool score scenario
    round_num = 4
    final_grp_prior_hole = 9
    
    # Get the player scores for active pool teams who made the cut
    pool.load_pool_scores()
    pool_player_score_df = pool.pool_player_score_df

    # Get player scorecards for pool players who made cut
    active_pool_players = pool_player_score_df[pool_player_score_df['MadeCut'] == True]['PLAYER'].reset_index(drop=True)
    player_scorecards = stats.get_player_scorecards(
        espn_player_names=active_pool_players, 
        multi_request=True, 
        max_workers=20
    )
    
    # Create scoring scenario
    scen_pool_player_score_df = stats.create_prior_score_scenario(
        round_num=round_num, 
        final_grp_prior_hole=final_grp_prior_hole, 
        pool_player_score_df=pool_player_score_df,
        player_scorecards=player_scorecards,
        filter_cuts=filter_cuts
        )

    # Recalculate team scores for the prior score scenario
    scen_pool_score_df = pool.calc_pool_scores_df(scen_pool_player_score_df)

    shock_player_score_data = calc_team_rank_sensitivities(pool=pool, pool_player_score_df=scen_pool_player_score_df)
    
    rank_sensitivity_df = create_rank_sensitivity_df(pool_score_df=scen_pool_score_df, shock_player_score_data=shock_player_score_data)
    
    sens_results = filter_sensitivity_results(pool=pool, team_id=team_id, rank_sensitivity_df=rank_sensitivity_df)
   
