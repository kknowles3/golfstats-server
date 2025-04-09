# -*- coding: utf-8 -*-
"""
Created on Sat Apr  9 11:28:12 2022

@author: kknow
"""

# from components.data import DB_NAME, SCORE_URL
# from components.data import ege, pool

from dev.espn.espn_golf_event import EspnGolfEvent
from dev.espn.pool_event import PoolEventScorer
# from dev.util.update_util import ScoreUpdater
from dev.util.data_util import RemoteDataServer

if __name__ == "__main__":
    
    # event_tag = 'masters2022'
    # event_config = EVENT_CONFIGS[event_tag]

    # SITE_TITLE = event_config['site_title']
    # DB_NAME = event_config['db_name']
    # LOGO_URL = event_config['logo_url']
    # EVENT_TAG = event_config['event_tag']
    # EVENT_ID = event_config['event_id']
    # SCORE_URL = event_config['score_url'].format(EVENT_ID)
    
    db_name = 'ukopen2024'
    event_id = 401580360
    player_score_cname = 'player_score'
    pool_score_cname = 'pool_score'
    score_url = 'https://www.espn.com/golf/leaderboard/_/tournamentId/{}'.format(event_id)
    
    rds = RemoteDataServer(db_name=db_name)
    ege = EspnGolfEvent(rds, score_url)
    pool = PoolEventScorer(rds)
    # updater = ScoreUpdater(rds, ege, pool)
    
    # Refresh player scores from ESPN site
    transform_df = False
    append_player_scores = True
    player_score_data = ege.get_player_score_data(transform_df=True, refresh=True)
    pool_score_data = pool.calc_pool_score_data(player_score_data, transform_df=transform_df, append_player_scores=append_player_scores)