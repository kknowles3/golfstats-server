# -*- coding: utf-8 -*-
"""
Created on Sat Jul 22 08:29:49 2023

@author: kknow

Test script for recalculating win probabilities

"""

# from components.app_data import EVENT_CONFIGS
# from dev.espn.pool_event import PoolEventScorer
# from dev_util.mongo_util import MongoDataServer
# # from dev_util.gen_util import calc_function_time

# from sandbox.scores.calc_score_distribution import ScoreStatsLoader
# from sandbox.scores.calc_score_distribution import GolfScoreSimulator

# # Moved to GolfScoreSimulator
# @calc_function_time
# def recalc_team_stats_df(gss:GolfScoreSimulator, num_trials, num_places):
    
#     pool:PoolEventScorer = gss.pool
    
#     #######################################################
#     # Get the input data we need for each calculation cycle
#     #######################################################
    
#     # Get the player scores for active pool teams who made the cut
#     pool_player_score_df = pool.load_pool_player_scores_df()
    
#     # Recalc team scores
#     pool_score_df = pool.calc_pool_scores_df(player_scores_df=pool_player_score_df, exclude_cut_teams=True)

#     # Get team ids that are still active in pool
#     team_player_id_df = pool.get_team_player_id_df(pool_score_df=pool_score_df, exclude_cut_teams=True)

#     # # Get the latest hole scoring stats
#     # hole_score_stats = stats_loader.get_hole_score_stats()

#     #########################
#     # Generate Random Scores
#     #########################
    
#     rand_player_scores = gss.calc_random_player_scores(pool_player_score_df, num_trials=num_trials, refresh_hole_stats=True)

#     #####################################################
#     # Generate random team scores and summary statistics
#     #####################################################
    
#     rand_team_scores = gss.calc_random_team_scores(rand_player_scores, team_player_id_df)
    
#     team_score_stats_df = gss.calc_team_summary_stats(rand_team_scores, team_player_id_df, num_places=num_places)

#     return team_score_stats_df
    
if __name__ == "__main__":

    from components.app_data import EVENT_CONFIGS
    from dev.espn.pool_event import PoolEventScorer
    from dev_util.mongo_util import MongoDataServer
    # from dev_util.gen_util import calc_function_time

    from sandbox.scores.calc_score_distribution import ScoreStatsLoader
    from sandbox.scores.calc_score_distribution import GolfScoreSimulator

    event_tag = 'masters2025'
    filter_cuts = True # Keep cuts to deal with downstream logic that needs cleanup
    num_trials = 10000
    num_places = 7
    
    event_config = EVENT_CONFIGS.get(event_tag)
    event_id = event_config.get('event_id')
    db_name = event_config['db_name']

    ####################################
    # Initialize calculators and loaders
    ####################################
    
    mds = MongoDataServer(db_name=db_name)
    pool = PoolEventScorer(mds)

    stats_loader = ScoreStatsLoader(event_id)
    
    # # Testing
    # player_score_jdata = stats_loader.get_player_score_data()
    # player_score_stats_jdata = stats_loader.get_player_score_stats_data()

    gss = GolfScoreSimulator(
        score_stats_loader=stats_loader,
        pool_event_scorer=pool
        )

    # #######################################################
    # # Get the input data we need for each calculation cycle
    # #######################################################
    
    # # Get the player scores for active pool teams who made the cut
    # pool.load_pool_scores()
    # pool_player_score_df = pool.pool_player_score_df
    
    # # Recalc team scores
    # pool_score_df = pool.calc_pool_scores_df(player_scores_df=pool_player_score_df, exclude_cut_teams=True)

    # # Get the latest hole scoring stats
    # hole_score_stats = stats.get_hole_score_stats()
    
    # #########################
    # # Simulate golf scores
    # #########################
    
    # #############################################
    # # Get team ids that are still active in pool
    # #############################################
    
    # team_player_id_df = pool.get_team_player_id_df(pool_score_df=pool_score_df, exclude_cut_teams=True)

    
    # #########################
    # # Generate Random Scores
    # #########################
    
    # # # TODO Consider moving this into the player score calculate routine,
    # # # or consider a method to get the active players who made cut with related
    # # # enrichments
    # # # Get the active pool players who made the cut and add a couple columns
    # # active_pool_player_score_df = scen_pool_player_score_df[scen_pool_player_score_df['MadeCut'] == True].reset_index(drop=True)
    # # active_pool_player_score_df = gss.add_prior_holes(active_pool_player_score_df)
    # # active_pool_player_score_df = gss.add_remaining_rounds(active_pool_player_score_df)
    
    # # Don't need these items, unless using for validation testing
    # # # Hole Frequency Distributions
    # # hole_freq_dist = gss.hole_freq_dist
    
    # # hole_probs = {k:d.get('probs') for k,d in hole_freq_dist.items()}
    # # hole_probs_df = pd.DataFrame(hole_probs)
    
    # # Generate random trials for each player's score
    # # trial_sets = [10, 100, 1000, 10000]
    # # for n in trial_sets:
    # #     print('Calculating random player scores for {} trials'.format(n))
    # #     rand_player_scores = gss.calc_random_player_scores(scen_pool_player_score_df, num_trials=n)
    # rand_player_scores = gss.calc_random_player_scores(pool_player_score_df, num_trials=num_trials, hole_score_stats=hole_score_stats)
    
    # #############################################
    # # Get team ids that are still active in pool
    # #############################################
    
    # # # TODO This needs to be encapsulated
    # # # scen_pool_score_df = pool.calc_pool_scores_df(player_scores_df=scen_pool_player_score_df)
    
    # # # active_pool_score_df = scen_pool_score_df[scen_pool_score_df['MadeCut'] == True]
    # # active_pool_score_df = scen_pool_score_df
    
    # # # Get the ids still in the pool
    # # team_made_cut_ids = active_pool_score_df['team_id']
    
    # # # Filter pool_id_df for teams who made cut
    # # pool_id_df = pool.pool_id_df
    # # active_pool_id_df = pool_id_df[pool_id_df['team_id'].isin(team_made_cut_ids)].copy()
        
    # # # Convert pool id columns to int
    # # id_cols = ['P1_ID', 'P2_ID', 'P3_ID', 'P4_ID', 'TB_ID']
    # # active_pool_id_df[id_cols] = active_pool_id_df[id_cols].astype(int)
    
    # team_player_id_df = pool.get_team_player_id_df(pool_score_df=pool_score_df, exclude_cut_teams=True)
    
    # #####################################################
    # # Generate random team scores and summary statistics
    # #####################################################
    
    # rand_team_scores = gss.calc_random_team_scores(rand_player_scores, team_player_id_df)
    
    # team_score_stats_df = gss.calc_team_summary_stats(rand_team_scores, team_player_id_df, num_places=7)
    
    # # # Add actual finish for events that have completed
    # # start_rank_d = dict(zip(active_pool_score_df['team_id'], active_pool_score_df['Rank']))
    # # team_score_stats_df['StartRank'] = team_score_stats_df.index.to_series().map(start_rank_d)

    # # # Actual finish from the initial pool score
    # # act_finish_d = dict(zip(pool_score_df.index.to_series(), pool_score_df['Rank']))
    # # team_score_stats_df['ActFinish'] = team_score_stats_df.index.to_series().map(act_finish_d)
    
    # # team_score_stats_df['FinishDiff'] = team_score_stats_df['StartRank'] - team_score_stats_df['ActFinish']
    # # team_score_stats_df['StdDevDiff'] = team_score_stats_df['FinishDiff'] / team_score_stats_df['std']

    # # # Add actual finish for events that have completed
    # # start_rank_d = dict(zip(scen_pool_score_df['team_id'], scen_pool_score_df['Rank']))
    # # team_score_stats_df['StartRank'] = team_score_stats_df.index.to_series().map(start_rank_d)

    # # # Actual finish from the initial pool score
    # # act_finish_d = dict(zip(pool_score_df.index.to_series(), pool_score_df['Rank']))
    # # team_score_stats_df['ActFinish'] = team_score_stats_df.index.to_series().map(act_finish_d)
    
    # # team_score_stats_df['FinishDiff'] = team_score_stats_df['StartRank'] - team_score_stats_df['ActFinish']
    # # team_score_stats_df['StdDevDiff'] = team_score_stats_df['FinishDiff'] / team_score_stats_df['std']
    
    team_score_stats_df = gss.recalc_team_stats_df(num_trials=num_trials, num_places=num_places)
    