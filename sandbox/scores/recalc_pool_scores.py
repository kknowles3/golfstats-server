# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 13:52:23 2023

@author: kknow

Test script for recalculating pool scores from a set of player scoring data

"""

from components.app_data import EVENT_CONFIGS
from dev.espn.pool_event import PoolEventScorer
from dev_util.mongo_util import MongoDataServer

from sandbox.scores.calc_score_scenario import ScoreResetter


if __name__ == "__main__":
    
    event_tag = 'ukopen2023'
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
    
    # # Get the round info for the players
    # # TODO Consolidate this into one method
    # players_round_info = stats.get_players_round_info(player_scorecards=player_scorecards, round_num=round_num)
    # players_round_info_df = stats.get_players_round_info_df(player_scorecards=player_scorecards, round_num=round_num)
    
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
