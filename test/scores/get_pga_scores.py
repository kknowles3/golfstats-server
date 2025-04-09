# -*- coding: utf-8 -*-
"""
Created on Tue May 18 14:14:41 2021

@author: kknow
"""

from dev.espn.espn_golf_event import EspnGolfEvent
from dev.espn.pool_event import PoolEventScorer
from dev.util.update_util import ScoreUpdater
from dev.util.data_util import RemoteDataServer

##############################################################
# Admin data for site

##############################################################
# Golf scoring data

# Consider moving to event config data
# event_id = 401243010 # masters
event_id = 401243418 # pga

score_url = "https://www.espn.com/golf/leaderboard/_/tournamentId/{}".format(event_id)
db_name = 'pga2021'

rds = RemoteDataServer(db_name=db_name)
ege = EspnGolfEvent(rds, score_url)

# Refresh scores
ege.refresh_scores()

scores_df = ege.scores_df

# Get pool scores
pool = PoolEventScorer(rds)
# updater = ScoreUpdater(rds, ege, pool)

updater = ScoreUpdater(rds, ege, pool)
updater.update_pool_scores(refresh=True, save_remote=True, append_player_scores=True)
