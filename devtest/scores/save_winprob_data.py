# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 15:53:44 2024

@author: kknow
"""

if __name__ == "__main__":
    
    from components.app_data import EVENT_CONFIGS
    from dev.espn.pool_event import PoolEventScorer
    from dev_util.mongo_util import MongoDataServer
    # from dev_util.gen_util import calc_function_time

    from sandbox.scores.calc_score_distribution import ScoreStatsLoader
    from sandbox.scores.calc_score_distribution import GolfScoreSimulator
    
    event_tag = 'usopen2024'
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
    
    gss = GolfScoreSimulator(
        score_stats_loader=stats_loader,
        pool_event_scorer=pool
        )

    # #####################################################
    # # Generate random team scores and summary statistics
    # #####################################################
    
    # team_score_stats_df = gss.recalc_team_stats_df(
    #     num_trials=num_trials, 
    #     num_places=num_places)
    
    team_score_stats_data = gss.recalc_team_stats_data(
        num_trials=num_trials, 
        num_places=num_places,
        transform_df=True)
    
    team_score_stats_df = mds.get_df_from_data(team_score_stats_data)

    