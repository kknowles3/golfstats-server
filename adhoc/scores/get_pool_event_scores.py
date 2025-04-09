# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 11:04:48 2023

@author: kknow
"""

from components.data import pool, ege
# import pandas as pd

if __name__ == "__main__":
    
    # # Get the event-specific configuration parameters
    # event_tag = 'masters2023'
    # event_config = EVENT_CONFIGS[event_tag]
    
    # SITE_TITLE = event_config['site_title']
    # DB_NAME = event_config['db_name']
    # LOGO_URL = event_config['logo_url']
    # EVENT_TAG = event_config['event_tag']
    # EVENT_ID = event_config['event_id']
    # SCORE_URL = event_config['score_url'].format(EVENT_ID)
    
    # rds = RemoteDataServer(db_name=DB_NAME)
    # ege = EspnGolfEvent(rds, SCORE_URL)
    # pool = PoolEventScorer(rds)
    
    # Load player score data
    player_score_data = ege.get_player_score_data(transform_df=True)
    
    pool_score_data = pool.calc_pool_score_data(player_score_data)

    # df = pool.load_pool_scores_df()
    df = pool_score_data.get('df')
    
    pool_score_col = 'Score'
    tb_score_col = 'TB_Score'
    # # https://stackoverflow.com/questions/41974374/pandas-rank-by-multiple-columns
    df['RankTB'] = df[[pool_score_col, tb_score_col]].apply(tuple, axis=1).rank(method='min', na_option='bottom')
