# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 16:11:31 2023

@author: kknow
"""

from dev.util.data_util import RemoteDataServer
from dev.espn.espn_golf_event import EspnGolfEvent
from dev.espn.pool_event import PoolEventScorer

if __name__ == "__main__":
    
    save_remote = False
    
    db_name = 'ukopen2024'
    event_id = 401580360
    player_score_cname = 'player_score'
    pool_score_cname = 'pool_score'
    score_url = 'https://www.espn.com/golf/leaderboard/_/tournamentId/{}'.format(event_id)
    
    rds = RemoteDataServer(db_name=db_name)

    ege = EspnGolfEvent(rds, score_url)
    pool = PoolEventScorer(rds)
    
    player_score_data = ege.get_player_score_data(transform_df=True, refresh=True)
    player_score_df = rds.get_df_from_data(player_score_data)
    
    if save_remote:        
        rds.save_remote_data(player_score_data, player_score_cname, overwrite=False)
        
    pool_score_data = pool.calc_pool_score_data(player_score_data, transform_df=True, append_player_scores=True)
    pool_score_df = rds.get_df_from_data(pool_score_data)
    
    if save_remote:        
        rds.save_remote_data(pool_score_data, pool_score_cname, overwrite=False)