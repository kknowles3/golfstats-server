# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 11:50:39 2023

@author: kknow

Test script for simulating team cut probabilities

"""

from components.app_data import EVENT_CONFIGS
from dev.espn.pool_event import PoolEventScorer
from dev_util.mongo_util import MongoDataServer

from sandbox.scores.calc_score_distribution import ScoreStats, GolfScoreSimulator

class GolfCutLineSimulator(GolfScoreSimulator):
    
    def __init__(self, hole_score_stats, pool_event_scorer):
        
        super().__init__(hole_score_stats, pool_event_scorer)

if __name__ == "__main__":
    
    num_players_cut = 70
    
    event_tag = 'ukopen2023'
    num_trials = 100000
    thru_round = 2
    
    event_config = EVENT_CONFIGS.get(event_tag)
    event_id = event_config.get('event_id')
    db_name = event_config['db_name']
    
    mds = MongoDataServer(db_name=db_name)
    pool = PoolEventScorer(mds)

    # Get the player scores for active pool teams who made the cut
    pool.load_pool_scores()
    pool_player_score_df = pool.pool_player_score_df
    
    pool_score_df = pool.calc_pool_scores_df(player_scores_df=pool_player_score_df, exclude_cut_teams=False)
    
    #########################
    # Get course hole stats
    #########################
    
    stats = ScoreStats(event_id=event_id)
    hole_score_stats = stats.get_hole_score_stats()

    #########################
    # Simulate cut scores
    #########################

    gss = GolfCutLineSimulator(hole_score_stats=hole_score_stats, pool_event_scorer=pool)

    rand_player_scores = gss.calc_random_player_scores(pool_player_score_df, num_trials=num_trials, thru_round=thru_round)

    team_player_id_df = pool.get_team_player_id_df(pool_score_df=pool_score_df, exclude_cut_teams=False)
    rand_team_scores = gss.calc_random_team_scores(rand_player_scores, team_player_id_df)

    team_score_stats_df = gss.calc_team_summary_stats(rand_team_scores, team_player_id_df, num_places=7)

    ...
