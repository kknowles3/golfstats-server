# -*- coding: utf-8 -*-
"""
Created on Sun Apr 18 12:59:53 2021

@author: kknow
"""

from dev.espn.espn_golf_event import EspnGolfEvent
from dev.espn.pool_event import PoolEventScorer
from dev.util.data_util import RemoteDataServer

from dev_util.mongo_util import MongoDataServer
# from dev_util.data_util import get_nested_item
from dev_util.datetime_util import get_now, get_utc_as_local_str

import threading
import time
from timeit import default_timer as timer
# import dateparser

from multiprocessing import Lock

# Trying one global server instance for saving the scoring data to MongoDb
class ScoreUpdater():
    
    def __init__(self, mds:MongoDataServer, ege:EspnGolfEvent, pool:PoolEventScorer):

        self.__is_updating__ = False
        self.update_freq_secs = 10
        self.__update_thread__ = None
        
        self.mds = mds
        self.ege = ege
        self.pool = pool
        
        self.player_score_cname = 'player_score'
        self.pool_score_cname = 'pool_score'
        
        self.player_score_res = None
        self.pool_score_res = None
        
        self.player_score_data = None
        self.pool_score_data = None
        
        # TODO Implement this and show on update page
        self.last_update_check = None
        
    def is_updating(self):
        return self.__is_updating__

    def update_player_scores(self, refresh=True, save_remote=True):
    
        # Refresh player scores from ESPN site
        self.player_score_data = self.ege.get_player_score_data(transform_df=True, refresh=refresh)
        
        if save_remote:
            # save data remotely
            res = self.mds.save_remote_data(self.player_score_data, self.player_score_cname, overwrite=False)
            self.player_score_res = res
        
        return None
    
    # TODO Add thread-safe locks
    # See: https://stackoverflow.com/questions/3310049/proper-use-of-mutexes-in-python
    # See response from Chris B.
    def update_pool_scores(self, refresh=True, save_remote=True, append_player_scores=True):
        
        if refresh:
            self.update_player_scores(refresh=refresh, save_remote=save_remote)
    
        self.pool_score_data = self.pool.calc_pool_score_data(self.player_score_data, transform_df=True, append_player_scores=append_player_scores)
        
        if save_remote:
            # save data remotely
            res = self.mds.save_remote_data(self.pool_score_data, self.pool_score_cname, overwrite=False)
            self.pool_score_res = res

    # run the update loop
    def __run_update_loop__(self):

        self.__is_updating__ = True
        while True:
            dt_now = get_now()
            print('Live updating: {}'.format(get_utc_as_local_str(dt_now)))
            # self.ege.refresh_scores()
            start = timer()
            self.update_pool_scores(refresh=True, save_remote=True)
            end = timer()
            # Adjust sleep timer for time to do the update
            time.sleep(self.update_freq_secs - (end-start))
            if not self.__is_updating__:
                print("Stopping updater")
                break
        print('broke from while loop')
        
    # Starts updating
    def start_updates(self):

        self.__update_thread__ = threading.Thread(target=self.__run_update_loop__, args=()) 
        t1 = self.__update_thread__
        t1.start()
        print('started thread')
            
    # Stops updating
    def stop(self):
        self.__is_updating__ = False
        if self.__update_thread__ is not None:
            self.__update_thread__.join()
            print('joined thread')

# ***********************************************************************
# ***********************************************************************
# ***********************************************************************

mutex = Lock()

# def compare_data_items(prior_player_score_data, player_score_data):
    
#     items_match = True
#     # Compare key items
#     for k,lst in player_score_data.items():
        
#         print("Checking key: {}".format(k))
#         lst2 = prior_player_score_data.get(k)
#         if lst == lst2:
#             print("Current {} data matches prior data".format(k))
#         else:
#             items_match = False
#             print('Found differences in key: {}, checking list items'.format(k))
#             for i,v in enumerate(lst):
#                 v2 = lst2[i]
#                 if v != v2:
#                     print('Found item mismatch')
#                     print('Current: {}'.format(v))
#                     print('Prior {}'.format(v2))

#     return items_match

# def get_last_update_local(utc_str):
    
#     utc_dt = dateparser.parse(utc_str)
#     local_dt_str = get_utc_as_local_str(utc_dt)
    
#     return local_dt_str

# # Load the most-recently saved player score data
# def load_prior_player_scores(rds):
    
#     player_score_cname = 'player_score'

#     db = rds.db
#     coll = db.get_collection(player_score_cname)
#     # prior_player_score_data = coll.find(({}).sort('last_update', -1).limit(1)
#     data_from_db = coll.find(sort=[('last_update', -1)], limit=1)
    
#     # find_kwargs = {'sort': [('last_update', -1)]}
#     # prior_player_score_data = rds.load_remote_data_items(player_score_cname, find_kwargs=find_kwargs)
#     prior_player_score_data = [doc for doc in data_from_db][0]
#     last_update_str = prior_player_score_data.get('last_update')
#     last_update_local_str = get_utc_as_local_str(last_update_str)    
#     print("Player score data last updated: {}".format(last_update_local_str))
    
#     # prior_player_scores = get_nested_item(prior_pool_score_data, keys=['player_score_data', 'data'])
#     prior_player_scores = prior_player_score_data.get('data')
    
#     return prior_player_scores

# def load_prior_pool_scores(rds):
    
#     pool_score_cname = 'pool_score'

#     db = rds.db
#     coll = db.get_collection(pool_score_cname)
#     # prior_player_score_data = coll.find(({}).sort('last_update', -1).limit(1)
#     data_from_db = coll.find(sort=[('last_update', -1)], limit=1)
    
#     # find_kwargs = {'sort': [('last_update', -1)]}
#     # prior_player_score_data = rds.load_remote_data_items(player_score_cname, find_kwargs=find_kwargs)
#     prior_pool_score_data = [doc for doc in data_from_db][0]
#     last_update_str = prior_pool_score_data.get('last_update')
#     last_update_local_str = get_utc_as_local_str(last_update_str)    
#     print("Pool score data last updated: {}".format(last_update_local_str))
    
#     prior_pool_scores = prior_pool_score_data.get('data')
    
#     return prior_pool_scores
    
# def update_player_scores(ege, rds, refresh=True, save_remote=True, prior_player_scores=None):

#     player_score_cname = 'player_score'
#     # Refresh player scores from ESPN site
#     player_score_data = ege.get_player_score_data(transform_df=True, refresh=refresh)

#     # Compare items using simple string matches to overcome limitation of standard comparisons
#     items_match = str(player_score_data.get('data')) == str(prior_player_scores)
    
#     # TOOD Consider where to move this
#     if not items_match:
#         if save_remote:
#             # save data remotely
#             rds.save_remote_data(player_score_data, player_score_cname, overwrite=False)
#             # self.player_score_res = res
#     else:
#         print("No update required for player scores")
    
#     return player_score_data

# def update_pool_scores(prior_player_scores=None, prior_pool_scores=None, refresh=True, save_remote=True, append_player_scores=True):

#     db_name = 'masters2023'
#     pool_score_cname = 'pool_score'
#     event_id = 401465508
#     score_url = "https://www.espn.com/golf/leaderboard/_/tournamentId/{}".format(event_id)

#     rds = RemoteDataServer(db_name=db_name)
#     ege = EspnGolfEvent(rds, score_url)
#     pool = PoolEventScorer(rds)
    
#     # Update player scores, includes check for whether we need to update    
#     if prior_player_scores is None:
#         prior_player_scores = load_prior_player_scores(rds)
        
#     player_score_data = update_player_scores(ege=ege, rds=rds, refresh=refresh, save_remote=save_remote, prior_player_scores=prior_player_scores)

#     if prior_pool_scores is None:
#         prior_pool_scores = load_prior_pool_scores(rds)

#     # Refresh player scores from ESPN site
#     pool_score_data = pool.calc_pool_score_data(player_score_data, transform_df=True, append_player_scores=append_player_scores)

#     # Compare items using simple string matches to overcome limitation of standard comparisons
#     items_match = str(pool_score_data.get('data')) == str(prior_pool_scores)
    
#     # TOOD Consider where to move this
#     if not items_match:
#         if save_remote:
#             # save data remotely
#             rds.save_remote_data(pool_score_data, pool_score_cname, overwrite=False)
#             # self.player_score_res = res
#     else:
#         print("No update required for pool scores")

#     player_scores = player_score_data.get('data')
#     pool_scores = pool_score_data.get('data')    
    
#     return player_scores, pool_scores
    
# # TODO Add thread-safe locks
# # See: https://stackoverflow.com/questions/3310049/proper-use-of-mutexes-in-python
# # See response from Chris B.
# def update_pool_scores(prior_player_scores=None, prior_pool_scores=None, refresh=True, save_remote=True, append_player_scores=True):

#     # event_id = 401465508
#     db_name = 'masters2023'
#     pool_score_cname = 'pool_score'
#     # score_url = "https://www.espn.com/golf/leaderboard/_/tournamentId/{}".format(event_id)

#     rds = RemoteDataServer(db_name=db_name)
#     # ege = EspnGolfEvent(rds, score_url)
#     pool = PoolEventScorer(rds)

#     # Update player scores, includes check for whether we need to update    
#     if prior_player_scores is None:
#         prior_player_scores = load_prior_player_scores(rds)
        
#     player_score_data = update_player_scores(ege=ege, rds=rds, refresh=refresh, save_remote=save_remote, prior_player_scores=prior_player_scores)

#     # Update pool scores, includes check for whether we need to update    
#     if prior_pool_scores is None:
#         prior_pool_scores = load_prior_pool_scores(rds)

#     pool_score_data = pool.calc_pool_score_data(player_score_data, transform_df=True, append_player_scores=append_player_scores)
    
#     player_scores = get_nested_item(pool_score_data, ['player_score_data', 'data'])

#     # if player_score_data != prior_player_score_data: 
#     if str(player_scores) != str(prior_player_scores): 
           
#         if save_remote:
#             # save data remotely
#             rds.save_remote_data(pool_score_data, pool_score_cname, overwrite=False)
#             # self.pool_score_res = res
#     else:
#         print("No change in player scores")

#     return pool_score_data

# # run the update loop
# def run_update_loop(prior_player_scores, prior_pool_scores):

#     with mutex:
        
#         print('started thread')
#         # dt_now = get_now()
#         # print('Live updating: {}'.format(get_utc_as_local_str(dt_now)))
#         # self.ege.refresh_scores()
#         # start = timer()
#         prior_player_scores, prior_pool_scores = update_pool_scores(
#             prior_player_scores=prior_player_scores,
#             prior_pool_scores=prior_pool_scores,
#             refresh=True, 
#             save_remote=True
#             )
#         # end = timer()
#         # # Adjust sleep timer for time to do the update
#         # time.sleep(update_freq_secs - (end-start))
    
#     return prior_player_scores, prior_pool_scores

# Trying one global server instance for saving the scoring data to MongoDb
class ScoreUpdater2():
    
    def __init__(self, update_freq_secs=10):

        self.__is_updating__ = False
        self.update_freq_secs = update_freq_secs
        self.__update_thread__ = None
        
        self.db_name = 'pga2023'
        self.event_id = 401465523
        self.score_url = "https://www.espn.com/golf/leaderboard/_/tournamentId/{}".format(self.event_id)

        self.player_score_cname = 'player_score'
        self.pool_score_cname = 'pool_score'
        # self.player_score_res = None
        # self.pool_score_res = None
        
        # self.player_score_data = None
        # self.pool_score_data = None
        
        self.mds = MongoDataServer(db_name=self.db_name)
        # self.ege = ege
        # self.pool = pool
        
        # TODO Implement this and show on update page
        self.last_update_check = None
        
        self.mutex = Lock()
        
    def is_updating(self):
        return self.__is_updating__

    # Load the most-recently saved player score data
    def load_prior_player_scores(self, mds):
        
        # player_score_cname = 'player_score'

        db = mds.db
        coll = db.get_collection(self.player_score_cname)
        # prior_player_score_data = coll.find(({}).sort('last_update', -1).limit(1)
        data_from_db = coll.find(sort=[('last_update', -1)], limit=1)
        
        # find_kwargs = {'sort': [('last_update', -1)]}
        # prior_player_score_data = rds.load_remote_data_items(player_score_cname, find_kwargs=find_kwargs)
        prior_player_score_data = [doc for doc in data_from_db][0]
        last_update_str = prior_player_score_data.get('last_update')
        last_update_local_str = get_utc_as_local_str(last_update_str)    
        print("Player score data last updated: {}".format(last_update_local_str))
        
        # prior_player_scores = get_nested_item(prior_pool_score_data, keys=['player_score_data', 'data'])
        prior_player_scores = prior_player_score_data.get('data')
        
        return prior_player_scores

    def load_prior_pool_scores(self, mds):
        
        # pool_score_cname = 'pool_score'

        db = mds.db
        coll = db.get_collection(self.pool_score_cname)
        # prior_player_score_data = coll.find(({}).sort('last_update', -1).limit(1)
        data_from_db = coll.find(sort=[('last_update', -1)], limit=1)
        
        # find_kwargs = {'sort': [('last_update', -1)]}
        # prior_player_score_data = rds.load_remote_data_items(player_score_cname, find_kwargs=find_kwargs)
        prior_pool_score_data = [doc for doc in data_from_db][0]
        last_update_str = prior_pool_score_data.get('last_update')
        last_update_local_str = get_utc_as_local_str(last_update_str)    
        print("Pool score data last updated: {}".format(last_update_local_str))
        
        prior_pool_scores = prior_pool_score_data.get('data')
        
        return prior_pool_scores

    def update_player_scores(self, ege, mds, refresh=True, save_remote=True, prior_player_scores=None):
    
        # Refresh player scores from ESPN site
        player_score_data = ege.get_player_score_data(transform_df=True, refresh=refresh)
    
        # Compare items using simple string matches to overcome limitation of standard comparisons
        items_match = str(player_score_data.get('data')) == str(prior_player_scores)
        
        # TOOD Consider where to move this
        if not items_match:
            if save_remote:
                # save data remotely
                mds.save_remote_data(player_score_data, self.player_score_cname, overwrite=False)
                # self.player_score_res = res
        else:
            print("No update required for player scores")
        
        return player_score_data

    def update_pool_scores(self, prior_player_scores=None, prior_pool_scores=None, refresh=True, save_remote=True, append_player_scores=True):

        with self.mutex:
            
            # db_name = 'masters2023'
            # pool_score_cname = 'pool_score'
            # event_id = 401465508
            # score_url = "https://www.espn.com/golf/leaderboard/_/tournamentId/{}".format(event_id)
            
            start = timer()
            # MDS is a heavyweight initialization. See if we can reuse
            mds = self.mds
            ege = EspnGolfEvent(mds, self.score_url)
            pool = PoolEventScorer(mds)
            end = timer()
            print("Initialized loaders in {:,.2f} seconds".format(end-start))
            
            # Update player scores, includes check for whether we need to update    
            if prior_player_scores is None:
                prior_player_scores = self.load_prior_player_scores(mds)
                
            player_score_data = self.update_player_scores(ege=ege, mds=mds, refresh=refresh, save_remote=save_remote, prior_player_scores=prior_player_scores)
    
            if prior_pool_scores is None:
                prior_pool_scores = self.load_prior_pool_scores(mds)
    
            # Refresh player scores from ESPN site
            pool_score_data = pool.calc_pool_score_data(player_score_data, transform_df=True, append_player_scores=append_player_scores)
    
            # Compare items using simple string matches to overcome limitation of standard comparisons
            items_match = str(pool_score_data.get('data')) == str(prior_pool_scores)
            
            # TOOD Consider where to move this
            if not items_match:
                if save_remote:
                    # save data remotely
                    mds.save_remote_data(pool_score_data, self.pool_score_cname, overwrite=False)
                    # self.player_score_res = res
            else:
                print("No update required for pool scores")
    
            player_scores = player_score_data.get('data')
            pool_scores = pool_score_data.get('data')    
            
            return player_scores, pool_scores

    # run the update loop
    def __run_update_loop__(self, prior_player_scores=None, prior_pool_scores=None):
        
        self.__is_updating__ = True
        while True:
            dt_now = get_now()
            print('Live updating: {}'.format(get_utc_as_local_str(dt_now)))
            # self.ege.refresh_scores()
            start = timer()
            prior_player_scores, prior_pool_scores = self.update_pool_scores(
                prior_player_scores=prior_player_scores,
                prior_pool_scores=prior_pool_scores,
                refresh=True, 
                save_remote=True
                )
            self.last_update_check = get_now()
            end = timer()
            print("Updated pool scores in {:,.2f} seconds".format(end-start))
            # Adjust sleep timer for time to do the update
            wait_secs = max(self.update_freq_secs - (end-start),0)
            print("Waiting for {:,.2f} seconds".format(wait_secs))
            time.sleep(max(wait_secs,0))
            if not self.__is_updating__:
                print("Stopping updater")
                break
        print('broke from while loop')
        
        return None

    # Starts updating
    def start_updates(self, multi_thread=True):

        if multi_thread:
            self.__update_thread__ = threading.Thread(target=self.__run_update_loop__, args=())
            t1 = self.__update_thread__
            t1.start()
        else:
            # Run in main thread - for debugging
            self.__run_update_loop__()
        
    # Stops updating
    def stop(self):
        self.__is_updating__ = False
        if self.__update_thread__ is not None:
            self.__update_thread__.join()
            print('joined thread')

# Main code for testing thread callback loop
def main():
    
    update_freq_secs = 2
    multi_thread = False

    db_name = 'masters2024'
   
    # updater = ScoreUpdater2(update_freq_secs=update_freq_secs)
    event_id = 401580344
    score_url = 'https://www.espn.com/golf/leaderboard/_/tournamentId/{}'.format(event_id)

    rds = RemoteDataServer(db_name=db_name)
    ege = EspnGolfEvent(rds, score_url)
    pool = PoolEventScorer(rds)
   
    updater = ScoreUpdater(mds=rds, ege=ege, pool=pool)
    
    # # player_score_data = updater.update_player_scores(ege, mds, refresh=True, save_remote=True, prior_player_scores=None)
    # player_score_data = updater.update_player_scores(refresh=True, save_remote=True)

    pool_score_data = updater.update_pool_scores(refresh=True, save_remote=True, append_player_scores=True)
    
        
    # t1 = threading.Thread(target=updater.start, args=()) 
    # updater.update_thread.start()
    # updater.start_updates(multi_thread=multi_thread)
    updater.start_updates()
    time.sleep(10)
    updater.stop()
    time.sleep(2)
    # updater.update_thread.join()
    # print('Thread stopped')
    # updater.start_updates(multi_thread=multi_thread)
    updater.start_updates()
    time.sleep(4)
    updater.stop()


if __name__ == '__main__':
    main()        