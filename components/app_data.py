# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 09:42:35 2021

@author: kknow

Master data file for the site.  For now, we will pre-load the data sets we need.


"""

# from dev.espn.espn_golf_event import EspnGolfEvent
# from dev.espn.pool_event import PoolEventScorer
# from dev_util.mongo_util import MongoDataServer
# from dev.util.update_util import ScoreUpdater
# # from dev.util.update_util import ScoreUpdater2
# from dev_util.app_util import get_config_val

##############################################################
# Admin data for site

##############################################################
# Golf scoring data

# TODO Push this to Mongo server
EVENT_CONFIGS = {
    
    # 2025 Configs
    "masters2025": {
        'site_title': "Masters Pool 2025",
        'event_tag': "Masters Pool 2025",
        'event_id': '401703504',
        'db_name': 'masters2025',
        'logo_url': 'https://a.espncdn.com/i/espn/misc_logos/500/masters_17.png',
        'score_url': "https://www.espn.com/golf/leaderboard/_/tournamentId/{}"
        },
    
    # 2024 Configs
    "masters2024": {
        'site_title': "Masters Pool 2024",
        'event_tag': "Masters Pool 2024",
        'event_id': '401580344',
        'db_name': 'masters2024',
        'logo_url': 'https://a.espncdn.com/i/espn/misc_logos/500/masters_17.png',
        'score_url': "https://www.espn.com/golf/leaderboard/_/tournamentId/{}"
        },
    'pga2024': {
        'site_title': "PGA Champ. Pool 2024",
        'event_tag': "PGA Pool 2024",
        'event_id': '401580351',
        'db_name': 'pga2024',
        'logo_url': '/assets/img/2023_pga_logo.jpg',
        'score_url': "https://www.espn.com/golf/leaderboard/_/tournamentId/{}"
        },
    'usopen2024': {
        'site_title': "US Open Pool 2024",
        'event_tag': "US Open Pool 2024",
        'event_id': '401580355',
        'db_name': 'usopen2024',
        'logo_url': '/assets/img/2024_usopen_logo.jpg',
        'score_url': "https://www.espn.com/golf/leaderboard/_/tournamentId/{}"
        },
    'ukopen2024': {
        'site_title': "The Open Championship Pool 2024",
        'event_tag': "The Open Chanmpionship Pool 2024",
        'event_id': '401580360',
        'db_name': 'ukopen2024',
        'logo_url': '/assets/img/2024_ukopen_logo.jpg',
        'score_url': "https://www.espn.com/golf/leaderboard/_/tournamentId/{}"
        },

    # 2023 Configs
    'ukopen2023': {
        'site_title': "The Open Championship Pool 2023",
        'event_tag': "The Open Championship Pool 2023",
        'event_id': '401465539',
        'db_name': 'ukopen2023',
        'logo_url': '/assets/img/2023_ukopen_logo.jpg',
        'score_url': "https://www.espn.com/golf/leaderboard/_/tournamentId/{}"
        },
    'usopen2023': {
        'site_title': "US Open Pool 2023",
        'event_tag': "US Open Pool 2023",
        'event_id': '401465533',
        'db_name': 'usopen2023',
        'logo_url': '/assets/img/2023_usopen_logo.jpg',
        'score_url': "https://www.espn.com/golf/leaderboard/_/tournamentId/{}"
        },
    'pga2023': {
        'site_title': "PGA Champ. Pool 2023",
        'event_tag': "PGA Pool 2023",
        'event_id': '401465523',
        'db_name': 'pga2023',
        'logo_url': '/assets/img/2023_pga_logo.jpg',
        'score_url': "https://www.espn.com/golf/leaderboard/_/tournamentId/{}"
        },
    "masters2023": {
        'site_title': "Masters Pool 2023",
        'event_tag': "Masters Pool 2023",
        'event_id': '401465508',
        'db_name': 'masters2023',
        'logo_url': 'https://a.espncdn.com/i/espn/misc_logos/500/masters_17.png',
        'score_url': "https://www.espn.com/golf/leaderboard/_/tournamentId/{}"
        },

    # 2022 Configs    
    "masters2022": {
        'site_title': "Masters Pool 2022",
        'event_tag': "Masters Pool 2022",
        'event_id': '401353232',
        'db_name': 'masters2022',
        'logo_url': 'https://a.espncdn.com/i/espn/misc_logos/500/masters_17.png',
        'score_url': "https://www.espn.com/golf/leaderboard/_/tournamentId/{}"
        },
    'pga2022': {
        'site_title': "PGA Champ. Pool 2022",
        'event_tag': "PGA Pool 2022",
        'event_id': '401353226',
        'db_name': 'pga2022',
        'logo_url': '/assets/img/2022_pga_logo.jpg',
        'score_url': "https://www.espn.com/golf/leaderboard/_/tournamentId/{}"
        },
    'usopen2022': {
        'site_title': "US Open Pool 2022",
        'event_tag': "US Open Pool 2022",
        'event_id': '401353222',
        'db_name': 'usopen2022',
        'logo_url': '/assets/img/2022_usopen_logo.jpg',
        'score_url': "https://www.espn.com/golf/leaderboard/_/tournamentId/{}"
        },
    'ukopen2022': {
        'site_title': "The Open Championship Pool 2022",
        'event_tag': "The Open Championship Pool 2022",
        'event_id': '401353217',
        'db_name': 'ukopen2022',
        'logo_url': '/assets/img/2022_usopen_logo.jpg',
        'score_url': "https://www.espn.com/golf/leaderboard/_/tournamentId/{}"
        },
    
    # 2021 Configs
    "masters": {
        'site_title': "Masters Pool 2021",
        'event_tag': "Masters Pool 2021",
        'event_id': '401243010',
        'db_name': 'masters2021',
        'logo_url': 'https://a.espncdn.com/i/espn/misc_logos/500/masters_17.png'
        },
    
    'pga': {
        'site_title': "PGA Champ. Pool 2021",
        'event_tag': "PGA Pool 2021",
        'event_id': '401243418',
        'db_name': 'pga2021',
        'logo_url': '/assets/img/2021-pga-championship-logo2.jpg',
        'score_url': "https://www.espn.com/golf/leaderboard/_/tournamentId/{}"
        },
    
    'usopen': {
        'site_title': "US Open Pool 2021",
        'event_tag': "US Open Pool 2021",
        'event_id': '401243414',
        'db_name': 'usopen2021',
        'logo_url': '/assets/img/2021-U.S.-OPEN_TORREY-PINES_FULL-COLOR-LOGO.jpg',
        'score_url': "https://www.espn.com/golf/leaderboard/_/tournamentId/{}"
        },

    'ukopen': {
        'site_title': "The Open Pool 2021",
        'event_tag': "The Open Pool 2021",
        'event_id': '401243410',
        'db_name': 'ukopen2021',
        'logo_url': '/assets/img/2021-British-Open.jpg',
        'score_url': "https://www.espn.com/golf/leaderboard/_/tournamentId/{}"
        },

    }

# Get the event-specific configuration parameters
current_event_tag = 'masters2025'
current_event_config = EVENT_CONFIGS[current_event_tag]

# 6/23/23 KK: Move the loaders to a separate file, so we can access event config 
# data without overhead of instantiating the instances

# Get the event-specific configuration parameters
# event_tag = 'usopen2023'
# event_config = EVENT_CONFIGS[event_tag]

# SITE_TITLE = event_config['site_title']
# DB_NAME = event_config['db_name']
# LOGO_URL = event_config['logo_url']
# EVENT_TAG = event_config['event_tag']
# EVENT_ID = event_config['event_id']
# SCORE_URL = event_config['score_url'].format(EVENT_ID)

# # Consider moving to event config data
# # event_id = 401243010 # Masters
# # event_id = EVENT_ID

# # score_url = "https://www.espn.com/golf/leaderboard/_/tournamentId/{}".format(event_id)
# # db_name = 'masters2021'
# # db_name = 'pga2021'

# rds = RemoteDataServer(db_name=DB_NAME)
# ege = EspnGolfEvent(rds, SCORE_URL)
# pool = PoolEventScorer(rds)
# update_freq_secs = 5
# # updater = ScoreUpdater2(update_freq_secs=update_freq_secs)
# updater = ScoreUpdater(rds=rds, ege=ege, pool=pool)

# # Start the updater, so update is running by default
# # ****************** Uncomment this to start updating by default ***************************
# # KK 4/7/22: Currently commented out for 2022 initial testing
# # KK 5/22/22: Turned it back on.
# # TODO Add environment variable to determine whether to have on or off at startup
# if get_config_val('LIVE_UPDATE', "APP_CONFIG") == 'ON':
#     updater.start_updates()
# # ******************************************************************************************