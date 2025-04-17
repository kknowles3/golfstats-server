# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 11:52:31 2023

@author: kknow

"""

# import pandas as pd

from components.app_data import EVENT_CONFIGS
from dev.espn.pool_event import PoolEventScorer
from dev_util.mongo_util import MongoDataServer

from sandbox.scores.calc_score_scenario import ScoreResetter
from sandbox.scores.calc_score_distribution import GolfScoreSimulator

if __name__ == "__main__":

    event_tag = 'masters2025'
    filter_cuts = False # Keep cuts to deal with downstream logic that needs cleanup
    num_trials = 100000
    
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
    final_pool_score_df = pool.pool_score_df.copy()
    
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
    
    scen_pool_score_df = pool.calc_pool_scores_df(player_scores_df=scen_pool_player_score_df, exclude_cut_teams=True)

    #########################
    # Simulate golf scores
    #########################
    
    hole_score_stats = stats.get_hole_score_stats()

    gss = GolfScoreSimulator(
        hole_score_stats=hole_score_stats,
        pool_event_scorer=pool
        )
    
    #########################
    # Generate Random Scores
    #########################
    
    # # TODO Consider moving this into the player score calculate routine,
    # # or consider a method to get the active players who made cut with related
    # # enrichments
    # # Get the active pool players who made the cut and add a couple columns
    # active_pool_player_score_df = scen_pool_player_score_df[scen_pool_player_score_df['MadeCut'] == True].reset_index(drop=True)
    # active_pool_player_score_df = gss.add_prior_holes(active_pool_player_score_df)
    # active_pool_player_score_df = gss.add_remaining_rounds(active_pool_player_score_df)
    
    # Don't need these items, unless using for validation testing
    # # Hole Frequency Distributions
    # hole_freq_dist = gss.hole_freq_dist
    
    # hole_probs = {k:d.get('probs') for k,d in hole_freq_dist.items()}
    # hole_probs_df = pd.DataFrame(hole_probs)
    
    # Generate random trials for each player's score
    # trial_sets = [10, 100, 1000, 10000]
    # for n in trial_sets:
    #     print('Calculating random player scores for {} trials'.format(n))
    #     rand_player_scores = gss.calc_random_player_scores(scen_pool_player_score_df, num_trials=n)
    rand_player_scores = gss.calc_random_player_scores(scen_pool_player_score_df, num_trials=num_trials)
    
    #############################################
    # Get team ids that are still active in pool
    #############################################
    
    # # TODO This needs to be encapsulated
    # # scen_pool_score_df = pool.calc_pool_scores_df(player_scores_df=scen_pool_player_score_df)
    
    # # active_pool_score_df = scen_pool_score_df[scen_pool_score_df['MadeCut'] == True]
    # active_pool_score_df = scen_pool_score_df
    
    # # Get the ids still in the pool
    # team_made_cut_ids = active_pool_score_df['team_id']
    
    # # Filter pool_id_df for teams who made cut
    # pool_id_df = pool.pool_id_df
    # active_pool_id_df = pool_id_df[pool_id_df['team_id'].isin(team_made_cut_ids)].copy()
        
    # # Convert pool id columns to int
    # id_cols = ['P1_ID', 'P2_ID', 'P3_ID', 'P4_ID', 'TB_ID']
    # active_pool_id_df[id_cols] = active_pool_id_df[id_cols].astype(int)
    
    team_player_id_df = pool.get_team_player_id_df(pool_score_df=scen_pool_score_df, exclude_cut_teams=True)
    
    #####################################################
    # Generate random team scores and summary statistics
    #####################################################
    
    rand_team_scores = gss.calc_random_team_scores(rand_player_scores, team_player_id_df)
    
    team_score_stats_df = gss.calc_team_summary_stats(rand_team_scores, team_player_id_df, num_places=7)
    
    # # Add actual finish for events that have completed
    # start_rank_d = dict(zip(active_pool_score_df['team_id'], active_pool_score_df['Rank']))
    # team_score_stats_df['StartRank'] = team_score_stats_df.index.to_series().map(start_rank_d)

    # # Actual finish from the initial pool score
    # act_finish_d = dict(zip(pool_score_df.index.to_series(), pool_score_df['Rank']))
    # team_score_stats_df['ActFinish'] = team_score_stats_df.index.to_series().map(act_finish_d)
    
    # team_score_stats_df['FinishDiff'] = team_score_stats_df['StartRank'] - team_score_stats_df['ActFinish']
    # team_score_stats_df['StdDevDiff'] = team_score_stats_df['FinishDiff'] / team_score_stats_df['std']

    # # Add actual finish for events that have completed
    # start_rank_d = dict(zip(scen_pool_score_df['team_id'], scen_pool_score_df['Rank']))
    # team_score_stats_df['StartRank'] = team_score_stats_df.index.to_series().map(start_rank_d)

    # # Actual finish from the initial pool score
    # act_finish_d = dict(zip(pool_score_df.index.to_series(), pool_score_df['Rank']))
    # team_score_stats_df['ActFinish'] = team_score_stats_df.index.to_series().map(act_finish_d)
    
    # team_score_stats_df['FinishDiff'] = team_score_stats_df['StartRank'] - team_score_stats_df['ActFinish']
    # team_score_stats_df['StdDevDiff'] = team_score_stats_df['FinishDiff'] / team_score_stats_df['std']
    
    team_score_stats_df = gss.add_final_score_stats(
        team_score_stats_df=team_score_stats_df,
        start_pool_score_df=scen_pool_score_df, 
        final_pool_score_df=final_pool_score_df
        )