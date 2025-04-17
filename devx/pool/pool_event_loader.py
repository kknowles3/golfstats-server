# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 15:27:29 2025

@author: kknow

Test class for loading pool event data from mongodb.

Under construction

"""


# import pandas as pd
# import numpy as np
# import dateparser
from dev_util.datetime_util import get_now

# from dev.util.app_util import APP_PATH
# from dev.util.data_util import RemoteDataLoader
from dev_util.mongo_util import MongoDataLoader
from pymongo import DESCENDING
# from dev.util.app_util import convert_utc_to_timezone

# TODO Consider adding golf event as an initialization parameter to streamline
# score recalculations
class PoolEventLoader():
    
    def __init__(
            self, 
            mdl:MongoDataLoader, 
            # ref_datestr=None, 
            # dt_offset=None
            ):
        '''
        Initialization routine. The optional ref_datestr parameter
        allows for testing from a prior reference point in time, such as from a
        prior round or earlier in the current day.
        
        If class is initialized with neither ref_datestr not dt_offset, then all
        refreshes occur relative to the current datetime.
        
        If class initialized with both ref_datestr and dt_offset, dt_offset input is used,
        and ref_datestr is ignored.
    
        Parameters
        ----------
        mdl : MongoDataLoader
            DESCRIPTION.
        ref_datestr : str, optional
            Optional reference datetime string for testing from a prior point
            in time. Should be expressed in a format parseable by dateparser to
            convert the string (e.g., "03/24/23 08:00:00 PM EDT") to a python 
            datetime.  The default is None.
        dt_offset : timedelta, optional
            Optional datetime offset that specifies a "back-in-time" shift relative
            to the current datetime.
        
        Returns
        -------
        None.

        '''
        
        self.mdl = mdl
        # self.ref_datestr = ref_datestr
        # self.dt_offset = dt_offset
        
        # self.pool_list_path = os.path.join(APP_PATH, 'data')
        # self.pool_list_fname = 'Masters Picks_2021_edit.csv'
        # self.player_list_path = os.path.join(APP_PATH, 'data')
        # self.player_list_fname = 'espn_list2.csv'

        # TODO MOve these into app config data
        self.player_list_collection = 'espn_pool_player_list'
        self.pool_list_collection = "pool_team_list"
        self.pool_score_collection = 'pool_score'
        # self.espn_player_col = 'displayName'
        # self.espn_id_col = 'id'
        
        # self.player_score_col = 'ParScore'
        # self.pool_score_col = 'Score'
        # self.tb_score_col = 'TB_Score'

        # self.pool_list_df =  pool_list_df
        # self.pool_team_map = None
        # self.pool_id_df = None
        
        # self.player_list_df = player_list_df
        # self.pool_player_map = None
        # self.pool_id_map = None
        # self.id_pool_map = None

        # self.pool_player_ids = None  # Series of player ids selected in the pool
        # self.pool_player_score_df = None # Player scores filtered by selected players in this pool
        
        # self.pool_score_df = None
        # self.last_update = None
        # self.update_fmt_string = "%m/%d/%y %I:%M:%S %p"
        # self.status_tag = None

        # self.__initialize()

    # def __initialize(self):
        
    #     # Load the pool team list
    #     # self.pool_list_df = self.__load_pool_list()
    #     # TODO Not sure if we still need both of these
    #     self.id_team_map = dict(zip(self.pool_list_df['team_id'], self.pool_list_df['TEAM NAME']))
    #     self.team_id_map = dict(zip(self.pool_list_df['TEAM NAME'], self.pool_list_df['team_id']))
        
    #     # Load the player list
    #     # df = self.__load_player_list()
    #     # self.player_list_df = df
    #     df = self.player_list_df
    #     # self.pool_player_map = dict(zip(df['PoolName'], df[self.espn_player_col]))
    #     self.player_id_map = dict(zip(df[self.espn_player_col], df[self.espn_id_col]))
    #     # self.id_pool_map = dict(zip(df.index.values, df['PoolName']))
    #     self.id_player_map = dict(zip(df[self.espn_id_col], df[self.espn_player_col]))

    #     # self.pool_id_df = self.pool_list_df.replace(self.pool_id_map)
        
    #     # # TODO Move to class variable
    #     # # Names of columns for mapping from player name to ESPN id
    #     # player_map_cols = [
    #     #     'PLAYER 1',
    #     #     'PLAYER 2',
    #     #     'PLAYER 3',
    #     #     'PLAYER 4',
    #     #     'TIEBREAKER'
    #     #     ]
    #     pool_id_df = self.pool_list_df.copy()
    #     # pool_id_df[player_map_cols] = pool_id_df[player_map_cols].replace(self.pool_id_map)
        
    #     # col_names = ['P1_ID', 'P2_ID', 'P3_ID', 'P4_ID', 'TB_ID']
    #     # pool_id_df.columns = col_names
    #     all_col_names = {
    #         'PLAYER 1':'P1_ID', 
    #         'PLAYER 2':'P2_ID', 
    #         'PLAYER 3':'P3_ID', 
    #         'PLAYER 4':'P4_ID', 
    #         'TIEBREAKER':'TB_ID',
    #         'PLAYER 5 (SUB)':'SUB_ID'
    #         }
        
    #     # Filter columns names based on what is in pool_df
    #     col_names = {name_col:id_col for name_col,id_col in all_col_names.items() if name_col in pool_id_df.columns.values}
        
    #     pool_id_map = self.pool_id_map
        
    #     for name_col, id_col in col_names.items():
    #         if name_col in pool_id_df.columns.values:
    #             pool_id_df[id_col] = pool_id_df[name_col].map(pool_id_map)
    #         else:
    #             print("Column: {} not found in pool_id_df".format(name_col))

    #     # drop name columns
    #     name_cols = list(col_names.keys())
    #     pool_id_df = pool_id_df.drop(columns=name_cols)
            
    #     # pool_id_df.rename(columns=col_names, inplace=True)
    #     self.pool_id_df = pool_id_df

    #     # Get the distinct list of player ids in the pool
    #     # id_list = [self.pool_list_df[col] for col in self.pool_list_df.columns[2:]]    
    #     # KK edit 5/20/21 - modified to get ids instead of names
    #     id_list = [self.pool_id_df[col] for col in self.pool_id_df.columns[2:]]   
    #     self.pool_player_ids = pd.Series(np.sort(pd.concat(id_list).unique()))

    #     # Check for dt offset        
    #     if self.ref_datestr is not None:
    #         if self.dt_offset is None:
    #             self.__set_dt_offset()
    #         else:
    #             print('Using dt_offset input parameter and ignoring ref_datestr input')

    #     return None
    
    # def __load_pool_list(self):
        
    #     fname = os.path.join(self.pool_list_path, self.pool_list_fname)
    #     pool_list_df = pd.read_csv(fname, header=3, index_col=False)
    #     pool_list_df.insert(loc=0, column='team_id', value=pool_list_df.index.values )
        
    #     return pool_list_df

    def load_pool_list_df(self):
        
        mdl = self.mdl        
        collection = self.pool_list_collection
        pool_list_df = mdl.load_remote_df(collection)

        return pool_list_df

    # def __load_player_list(self):
        
    #     fname = os.path.join(self.player_list_path, self.player_list_fname)
    #     player_list_df = pd.read_csv(fname, index_col=False)
        
    #     return player_list_df

    def load_player_list_df(self):
        
        mdl = self.mdl
        collection = self.player_list_collection
        player_list_df = mdl.load_remote_df(collection)
        
        return player_list_df
    
    # def calc_pool_scores_df(
    #         self, 
    #         player_scores_df, 
    #         exclude_cut_teams=True):
    #     """
    #     Recalculates pool scores by team and by player from a set of espn player scores

    #     Parameters
    #     ----------
    #     player_scores_df : DataFrame
    #         List of ESPN scores by players.

    #     Returns
    #     -------
    #     pool_score_df : TYPE
    #         Returns a DataFrame of scores by team.

    #     """
        
    #     player_score_col = self.player_score_col
    #     pool_score_col = self.pool_score_col
    #     tb_score_col = self.tb_score_col
        
    #     scores_df = player_scores_df
    #     # 7/20/23 KK: Added drop na to drop players who have nan ids (e.g., amateurs that no one picked)
    #     scores_df = scores_df[scores_df['PlayerId'].isin(self.pool_player_ids).dropna()]
    #     self.pool_player_score_df = scores_df
        
    #     pool_score_df = self.pool_id_df.drop(columns=['TEAM NAME']).copy()
        
    #     id_df = self.pool_id_df[self.pool_id_df.columns[2:]]

    #     ## KK 4/7/22: Change score column label
    #     # id_score_map = dict(zip(scores_df['PlayerId'], scores_df['ParScore'].astype(int)))
    #     id_score_map = dict(zip(scores_df['PlayerId'], scores_df[player_score_col].astype(int)))
    #     id_cut_map = dict(zip(scores_df['PlayerId'], scores_df['MadeCut']))
    #     # Add Charley Hoffman - this is hard-coded for now
    #     id_cut_map[999] = False

    #     col_names =   ['P1_Score', 'P2_Score', 'P3_Score', 'P4_Score', 'TB_Score']
    #     pool_score_df[col_names] = id_df.replace(id_score_map)
    #     # pool_score_df = self.pool_id_df.replace(id_score_map)
    #     pool_score_df[pool_score_col] = pool_score_df[col_names[:4]].sum(axis=1)
                
    #     # Check whether players made cut
    #     col_names =   ['P1_MadeCut', 'P2_MadeCut', 'P3_MadeCut', 'P4_MadeCut', 'TB_MadeCut']

    #     # 4/10/25 KK: Possible workaround for downcasting issue with replace
    #     # pool_score_df[col_names] = id_df.replace(id_cut_map).infer_objects(copy=False)
    #     # pool_score_df[col_names] = id_df.map(pd.Series(id_cut_map))
    #     for dest_col, src_col in zip(col_names, id_df.columns.values):
    #         # pool_score_df[dest_col] = id_df[src_col].map(pd.Series(id_cut_map))
    #         pool_score_df[dest_col] = id_df[src_col].map(id_cut_map)
        
    #     pool_score_df['MadeCut'] = pool_score_df[col_names[:4]].min(axis=1)
        
    #     # pool_score_df['Score'] = pool_score_df.iloc[:, :4].sum(axis=1)
    #     # pool_score_df['MakeCut'] = pool_score_df[col_names[:4]].max(axis=1) <= cut_line

    #     # pool_score_df['Rank'] = pool_score_df[pool_score_col].rank(method='min', na_option='bottom')
    #     # https://stackoverflow.com/questions/41974374/pandas-rank-by-multiple-columns
    #     pool_score_df['Rank'] = pool_score_df[[pool_score_col, tb_score_col]].apply(tuple, axis=1).rank(method='min', na_option='bottom')

    #     gb = pool_score_df.groupby(by='MadeCut')
    #     pool_score_df['CutRank'] = gb['Score'].rank(method='min', na_option='bottom')
        
    #     if exclude_cut_teams:
    #         pool_score_df = pool_score_df[pool_score_df['MadeCut'] == True]

    #     self.pool_score_df = pool_score_df

    #     return pool_score_df

    # def calc_pool_score_data(self, player_score_data, transform_df=False, orient='split', append_player_scores=True):
    #     """
    #     Recalculates team scores, including the scores for each player on the team, plus some additional
    #     metadata describing the update.  Includes an option to transform the score df into 
    #     record format for remote data storage.
        
    #     Parameters
    #     ----------
    #     player_score_data : TYPE
    #         DESCRIPTION.
    #     transform_df : TYPE, optional
    #         DESCRIPTION. The default is False.
    #     orient : TYPE, optional
    #         DESCRIPTION. The default is 'split'.

    #     Returns
    #     -------
    #     score_data : TYPE
    #         DESCRIPTION.

    #     """
        
    #     # TODO Review the logic for processing the player score data.
    #     # Consider using generic method for recovering dataframe.
    #     # This approach relies on some embedded assumptions about the
    #     # player score data structure (i.e., either dataframe or data records and orient)        
    #     # Check whether the player score df has been transformed to data records and orient
    #     player_score_df = self.mdl.get_df_from_data(player_score_data)
        
    #     # Filter player_scores to exclude non-pool players
    #     player_score_df = player_score_df[player_score_df['PlayerId'].isin(self.pool_player_ids)]
    #     self.player_score_df = player_score_df
        
    #     self.pool_score_df = self.calc_pool_scores_df(player_score_df)
    #     self.last_update = player_score_data.get('last_update', None)
    #     self.status_tag = player_score_data.get('status_tag', None)

    #     score_data = {
    #         "last_update": self.last_update,
    #         "status_tag": self.status_tag
    #         }
        
    #     if transform_df:
    #         score_data['orient'] = orient
    #         score_data['data'] = self.pool_score_df.to_dict(orient)
    #     else:
    #         score_data['df'] = self.pool_score_df

    #     if append_player_scores:
    #         player_score_tag = {}
    #         score_data['player_score_data'] = player_score_tag
    #         if transform_df:
    #             player_score_tag['orient'] = orient
    #             player_score_tag['data'] = player_score_df.to_dict(orient)
    #         else:
    #             player_score_tag['df'] = player_score_df
    
    #     return score_data
    
    def load_pool_score_data(self):
        '''
        Loads most recent pool scores and player scores from the remote data service

        Returns
        -------
        pool_score_data : TYPE
            DESCRIPTION.

        '''

        # Get the newest score
        collection = self.pool_score_collection
        # find_kwargs = {'sort': [('last_update', DESCENDING)]}
        kwargs = {'find_kwargs': {'sort': [('last_update', DESCENDING)]}}
                  
        # Check for dt_offset
        if self.dt_offset is not None:
            dt_now = get_now()
            dt_then = dt_now - self.dt_offset
            kwargs.update({"filter_tag": { "last_update": {'$lt': dt_then}}})
        
        pool_score_data = self.mdl.load_remote_data_item(collection, **kwargs)

        return pool_score_data        

    # def load_pool_scores(self):
    #     """
    #     Loads most recent pool scores and player scores from the remote data service

    #     Returns
    #     -------
    #     None
        
    #     """
        
    #     # Moved to separate method
    #     # # Get the newest score
    #     # collection = self.pool_score_collection
    #     # # find_kwargs = {'sort': [('last_update', DESCENDING)]}
    #     # kwargs = {'find_kwargs': {'sort': [('last_update', DESCENDING)]}}
                  
    #     # # Check for dt_offset
    #     # if self.dt_offset is not None:
    #     #     dt_now = get_now()
    #     #     dt_then = dt_now - self.dt_offset
    #     #     kwargs.update({"filter_tag": { "last_update": {'$lt': dt_then}}})
        
    #     # pool_score_data = self.mdl.load_remote_data_item(collection, **kwargs)

    #     pool_score_data = self.load_pool_score_data()
        
    #     pool_score_df = self.mdl.get_df_from_data(pool_score_data)
        
    #     # self.pool_score_df = pool_score_df
    #     # self.last_update = pool_score_data.get("last_update", "missing last update")
    #     # self.status_tag = pool_score_data.get("status_tag", "missing_status_tag")

    #     # # ************** Testing *********************************
    #     # # # Load the saved player scores for the matching update tag
    #     # # collection_name = "player_score"
    #     # # filter_tag = {'last_update':self.last_update}
    #     # # scores_df = self.rdl.load_remote_df(collection_name, filter_tag)
    #     # # scores_df = scores_df[scores_df['PlayerId'].isin(self.pool_player_ids)]
    #     # # self.pool_player_score_df = scores_df

    #     # # Get player score data from pool score data        
    #     # player_score_data = pool_score_data.get('player_score_data', None)
    #     # if player_score_data is None:
    #     #     # raise ValueError('Invalid or missing player score data in pool score data set.')
    #     #     self.pool_player_score_df = None
    #     # else:
    #     #     player_score_df = self.mdl.get_df_from_data(player_score_data)
    #     #     player_score_df = player_score_df[player_score_df['PlayerId'].isin(self.pool_player_ids)]
    #     #     self.pool_player_score_df = player_score_df
        
    #     return None

    def load_pool_scores_df(self):
        """
        Loads most recent pool score df from the remote data service

        Returns
        -------
        pool_score_df : TYPE
            DESCRIPTION.

        """
        
        pool_score_data = self.load_pool_score_data()

        pool_score_df = self.mdl.get_df_from_data(pool_score_data)

        # pool_score_df = self.pool_score_df
        
        return pool_score_df

    def load_pool_player_scores_df(self):
        """
        Loads most recent pool player score df from the remote data service

        Returns
        -------
        pool_player_score_df : TYPE
            DESCRIPTION.

        """
        
        pool_score_data = self.load_pool_scores()

        # Get player score data from pool score data        
        player_score_data = pool_score_data.get('player_score_data', None)
        if player_score_data is None:
            # raise ValueError('Invalid or missing player score data in pool score data set.')
            # self.pool_player_score_df = None
            return None
        else:
            player_score_df = self.mdl.get_df_from_data(player_score_data)
            player_score_df = player_score_df[player_score_df['PlayerId'].isin(self.pool_player_ids)]
            # self.pool_player_score_df = player_score_df
        
        return player_score_df
    
    # def get_last_update_tag(self):
    #     """
    #     Gets a formatted string with the last update time. The format
    #     is set by the update_fmt_string parameter

    #     Returns
    #     -------
    #     update_tag : TYPE
    #         DESCRIPTION.

    #     """
        
    #     last_update = self.last_update
    #     if last_update is None:
    #         update_tag = 'Missing last update value'
    #     else:
    #         update_tag = last_update.strftime(self.update_fmt_string)
        
    #     return update_tag
    
    # def get_team_player_id_df(self, pool_score_df=None, exclude_cut_teams=True):
        
    #     pool_score_df = self.pool_score_df if pool_score_df is None else pool_score_df

    #     if exclude_cut_teams:
    #         pool_score_df = pool_score_df[pool_score_df['MadeCut'] == True]
        
    #     # Get the ids still in the pool
    #     team_ids = pool_score_df['team_id']
        
    #     # Filter pool_id_df for teams who made cut
    #     pool_id_df = self.pool_id_df
    #     team_player_id_df = pool_id_df[pool_id_df['team_id'].isin(team_ids)].copy()
            
    #     # Convert pool id columns to int
    #     id_cols = ['P1_ID', 'P2_ID', 'P3_ID', 'P4_ID', 'TB_ID']
    #     team_player_id_df[id_cols] = team_player_id_df[id_cols].astype(int)

    #     return team_player_id_df
