# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 15:38:22 2023

@author: kknow

This file contains the class instances that update, load, and save scoring data

TODO Consider ways to lazy load, manage cached data, and provide cleaner
ways to access the data components (e.g., consider a data container class)

"""

from dev.espn.espn_golf_event import EspnGolfEvent
from dev.espn.pool_event import PoolEventScorer
# from dev_util.mongo_util import MongoDataServer
from dev.util.data_util import RemoteDataServer
from dev.util.update_util import ScoreUpdater
# from dev.util.update_util import ScoreUpdater2
from dev.util.app_util import get_config_val

from components.app_data import EVENT_CONFIGS

# Get the event-specific configuration parameters
event_tag = 'masters2025'
event_config = EVENT_CONFIGS[event_tag]

SITE_TITLE = event_config['site_title']
DB_NAME = event_config['db_name']
LOGO_URL = event_config['logo_url']
EVENT_TAG = event_config['event_tag']
EVENT_ID = event_config['event_id']
SCORE_URL = event_config['score_url'].format(EVENT_ID)

# Consider moving to event config data
# event_id = 401243010 # Masters
# event_id = EVENT_ID

# score_url = "https://www.espn.com/golf/leaderboard/_/tournamentId/{}".format(event_id)
# db_name = 'masters2021'
# db_name = 'pga2021'

# mds = MongoDataServer(db_name=DB_NAME)
rds = RemoteDataServer(db_name=DB_NAME)
ege = EspnGolfEvent(rds, SCORE_URL)
pool = PoolEventScorer(rds)
update_freq_secs = 5
# updater = ScoreUpdater2(update_freq_secs=update_freq_secs)
updater = ScoreUpdater(mds=rds, ege=ege, pool=pool)

# Start the updater, so update is running by default
# ****************** Uncomment this to start updating by default ***************************
# KK 4/7/22: Currently commented out for 2022 initial testing
# KK 5/22/22: Turned it back on.
# TODO Add environment variable to determine whether to have on or off at startup
if get_config_val('LIVE_UPDATE', "APP_CONFIG") == 'ON':
    updater.start_updates()
# ******************************************************************************************