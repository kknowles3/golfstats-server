# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 14:55:02 2025

@author: kknow

Test a new pool event scorer that use the json data set for the 
scoring data.

"""

import pandas as pd
import numpy as np
import dateparser

from dev_util.datetime_util import get_now
from dev_util.gen_util import calc_function_time

# from dev.util.app_util import APP_PATH
# from dev.util.data_util import RemoteDataLoader
from dev_util.mongo_util import MongoDataLoader
from pymongo import DESCENDING
# from dev.util.app_util import convert_utc_to_timezone

# TODO Consider adding golf event as an initialization parameter to streamline
# score recalculations
class PoolEventScorerJson():
    
    def __init__(
            self, 
            # mdl:MongoDataLoader, 
            player_list_df,
            pool_list_df,
            ref_datestr=None, 
            dt_offset=None
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
        
        # self.mdl = mdl
        self.ref_datestr = ref_datestr
        self.dt_offset = dt_offset
        
        # self.pool_list_path = os.path.join(APP_PATH, 'data')
        # self.pool_list_fname = 'Masters Picks_2021_edit.csv'
        # self.player_list_path = os.path.join(APP_PATH, 'data')
        # self.player_list_fname = 'espn_list2.csv'

        # TODO MOve these into app config data
        # self.player_list_collection = 'espn_pool_player_list'
        # self.pool_list_collection = "pool_team_list"
        # self.pool_score_collection = 'pool_score'
        self.espn_player_col = 'displayName'
        self.espn_id_col = 'id'
        
        self.player_score_col = 'parScoreValue'
        self.pool_score_col = 'Score'
        self.tb_score_col = 'TB_Score'

        self.pool_list_df =  pool_list_df
        self.pool_team_map = None
        self.pool_id_df = None
        
        self.player_list_df = player_list_df
        self.pool_player_map = None
        self.pool_id_map = None
        self.id_pool_map = None

        self.pool_player_ids = None  # Series of player ids selected in the pool
        self.pool_player_score_df = None # Player scores filtered by selected players in this pool
        
        self.pool_score_df = None
        self.last_update = None
        self.update_fmt_string = "%m/%d/%y %I:%M:%S %p"
        self.status_tag = None

        # Mapping between pool team list column names and player ids
        self.pool_name_id_col_map = {
            'PLAYER 1':'P1_ID', 
            'PLAYER 2':'P2_ID', 
            'PLAYER 3':'P3_ID', 
            'PLAYER 4':'P4_ID', 
            'TIEBREAKER':'TB_ID',
            'PLAYER 5 (SUB)':'SUB_ID'
            }

        # TODO Move to initialization
        # Mappings between player id columns and related columns
        self.pool_player_tags = [
            'P1',
            'P2',
            'P3',
            'P4',
            'TB',
            'SUB',
            'SIT'
            ]
        
        id_tag = "_ID"
        score_tag = "_Score"
        made_cut_tag = "_MadeCut"
        
        self.player_id_cols = [f"{ptag}{id_tag}" for ptag in self.pool_player_tags]
        self.player_score_cols = [f"{ptag}{score_tag}" for ptag in self.pool_player_tags]
        self.player_made_cut_cols = [f"{ptag}{made_cut_tag}" for ptag in self.pool_player_tags]
        
        self.player_id_score_map = dict(zip(self.player_id_cols, self.player_score_cols))
        self.player_id_cut_map = dict(zip(self.player_id_cols, self.player_made_cut_cols))
        
        self.__initialize()

    def __set_dt_offset(self):
    
        dtbase = dateparser.parse(self.ref_datestr)
    
        # Get the current time and calculate the dt offset for simulating earlier point in time
        dtnow = get_now()
        
        self.dt_offset = dtnow - dtbase
    
        return None
    
    def __initialize(self):
        
        # Load the pool team list
        # self.pool_list_df = self.__load_pool_list()
        # TODO Not sure if we still need both of these
        self.id_team_map = dict(zip(self.pool_list_df['team_id'], self.pool_list_df['TEAM NAME']))
        self.team_id_map = dict(zip(self.pool_list_df['TEAM NAME'], self.pool_list_df['team_id']))
        
        # Load the player list
        # df = self.__load_player_list()
        # self.player_list_df = df
        df = self.player_list_df
        # self.pool_player_map = dict(zip(df['PoolName'], df[self.espn_player_col]))
        
        # pool_id_map = self.pool_id_map
        player_id_map = dict(zip(df[self.espn_player_col], df[self.espn_id_col]))
        self.player_id_map = player_id_map
        # self.id_pool_map = dict(zip(df.index.values, df['PoolName']))
        self.id_player_map = {v:k for k,v in player_id_map.items()}

        pool_id_df = self.pool_list_df.copy()
        # pool_id_df[player_map_cols] = pool_id_df[player_map_cols].replace(self.pool_id_map)
        
        pool_name_id_map = self.pool_name_id_col_map
        
        for name_col, id_col in pool_name_id_map.items():
            if name_col in pool_id_df.columns.values:
                pool_id_df[id_col] = pool_id_df[name_col].map(player_id_map)
            # else:
            #     # print("Column: {} not found in pool_id_df".format(name_col))
            #     ...

        # drop name columns
        name_cols = list(pool_name_id_map.keys())
        pool_id_df = pool_id_df.drop(columns=name_cols)
        self.pool_id_df = pool_id_df

        # Get the distinct list of player ids in the pool
        # id_list = [self.pool_list_df[col] for col in self.pool_list_df.columns[2:]]    
        # KK edit 5/20/21 - modified to get ids instead of names
        id_list = [pool_id_df[col] for col in pool_id_df.columns[2:]]
        self.pool_player_ids = pd.Series(np.sort(pd.concat(id_list).unique()))

        # Check for dt offset        
        if self.ref_datestr is not None:
            if self.dt_offset is None:
                self.__set_dt_offset()
            else:
                print('Using dt_offset input parameter and ignoring ref_datestr input')

        return None
    
    # def __load_pool_list(self):
        
    #     fname = os.path.join(self.pool_list_path, self.pool_list_fname)
    #     pool_list_df = pd.read_csv(fname, header=3, index_col=False)
    #     pool_list_df.insert(loc=0, column='team_id', value=pool_list_df.index.values )
        
    #     return pool_list_df

    # def __load_pool_list(self):
        
    #     mdl = self.mdl        
    #     collection = self.pool_list_collection
    #     pool_list_df = mdl.load_remote_df(collection)

    #     return pool_list_df

    # def __load_player_list(self):
        
    #     fname = os.path.join(self.player_list_path, self.player_list_fname)
    #     player_list_df = pd.read_csv(fname, index_col=False)
        
    #     return player_list_df

    # def __load_player_list(self):
        
    #     mdl = self.mdl
    #     collection = self.player_list_collection
    #     player_list_df = mdl.load_remote_df(collection)
        
    #     return player_list_df
    
    def add_player_score_cols(
            self,
            pool_id_df,
            player_scores_df):
        
        player_id_col = 'playerId'
        
        player_score_col = self.player_score_col
        pool_score_col = self.pool_score_col
        
        player_id_cols = self.player_id_cols
        id_col_names = [pid_col for pid_col in player_id_cols if pid_col in pool_id_df.columns.values]
        
        ## KK 4/7/22: Change score column label
        id_score_map = dict(zip(player_scores_df[player_id_col], player_scores_df[player_score_col].astype(int)))
        # id_cut_map = dict(zip(player_scores_df[player_id_col], player_scores_df[made_cut_col]))
        # id_cut_map[999] = False

        score_col_map = self.player_id_score_map
        
        pool_score_df = pool_id_df

        # TODO This needs work to generalize across columns
        for pid_col_name, score_col_name in score_col_map.items():
        
            if pid_col_name in id_col_names:
                pool_score_df[score_col_name] = pool_score_df[pid_col_name].map(id_score_map)
            # else:
            #     # print("Column: {} not found in team player ids".format(pid_col_name))
            #     ...
                
        score_cols = self.player_score_cols[:4]
        pool_score_df[pool_score_col] = pool_score_df[score_cols].sum(axis=1)

        return pool_score_df
        
    def add_made_cut_cols(
            self,
            pool_score_df,
            player_scores_df
            ):

        player_id_col = 'playerId'
        made_cut_col = 'madeCut'

        cut_col_map = self.player_id_cut_map
        
        player_id_cols = self.player_id_cols
        id_col_names = [pid_col for pid_col in player_id_cols if pid_col in pool_score_df.columns.values]
        
        id_cut_map = dict(zip(player_scores_df[player_id_col], player_scores_df[made_cut_col]))
        id_cut_map[999] = False

        for pid_col_name, cut_col_name in cut_col_map.items():
        
            if pid_col_name in id_col_names:
                pool_score_df[cut_col_name] = pool_score_df[pid_col_name].map(id_cut_map)
            # else:
                # print("Column: {} not found in team player ids".format(pid_col_name))
                # ...

        cut_col_names = self.player_made_cut_cols[:4]
        pool_score_df['MadeCut'] = pool_score_df[cut_col_names].min(axis=1)

        return pool_score_df
    
    @calc_function_time
    def calc_pool_scores_df(
            self, 
            player_scores_df, 
            pool_id_df=None,
            exclude_cut_teams=True):
        """
        Recalculates pool scores by team and by player from a set of espn player scores

        Parameters
        ----------
        player_scores_df : DataFrame
            List of ESPN scores by players.

        Returns
        -------
        pool_score_df : TYPE
            Returns a DataFrame of scores by team.

        """

        pool_id_df = self.pool_id_df if pool_id_df is None else pool_id_df
        
        # player_score_col = self.player_score_col
        pool_score_col = self.pool_score_col
        tb_score_col = self.tb_score_col
        
        # TODO Move to class variables
        player_id_col = 'playerId'
        # made_cut_col = 'madeCut'
        
        scores_df = player_scores_df
        # 7/20/23 KK: Added drop na to drop players who have nan ids (e.g., amateurs that no one picked)
        scores_df = scores_df[scores_df[player_id_col].isin(self.pool_player_ids).dropna()]
        self.pool_player_score_df = scores_df

        # TODO Do we need this?
        pool_score_df = self.pool_id_df.drop(columns=['TEAM NAME']).copy()

        ###########################
        # Add player score columns
        ###########################
        
        pool_score_df = self.add_player_score_cols(
            pool_score_df,
            player_scores_df)

        #######################
        # Add made cut columns
        #######################
                
        pool_score_df = self.add_made_cut_cols(
            pool_score_df, 
            player_scores_df)

        ######################
        # Add ranking columns
        ######################
        
        # https://stackoverflow.com/questions/41974374/pandas-rank-by-multiple-columns
        pool_score_df['Rank'] = pool_score_df[[pool_score_col, tb_score_col]].apply(tuple, axis=1).rank(method='min', na_option='bottom')

        gb = pool_score_df.groupby(by='MadeCut')
        pool_score_df['CutRank'] = gb['Score'].rank(method='min', na_option='bottom')
        
        if exclude_cut_teams:
            pool_score_df = pool_score_df[pool_score_df['MadeCut'] == True].reset_index(drop=True)

        self.pool_score_df = pool_score_df

        return pool_score_df
    
    # TODO COnvert to use new routine with sub column
    def calc_pool_score_data(
            self, 
            player_score_data, 
            transform_df=False, 
            orient='split', 
            append_player_scores=True):
        """
        Recalculates team scores, including the scores for each player on the team, plus some additional
        metadata describing the update.  Includes an option to transform the score df into 
        record format for remote data storage.
        
        Parameters
        ----------
        player_score_data : TYPE
            DESCRIPTION.
        transform_df : TYPE, optional
            DESCRIPTION. The default is False.
        orient : TYPE, optional
            DESCRIPTION. The default is 'split'.

        Returns
        -------
        score_data : TYPE
            DESCRIPTION.

        """
        
        # TODO Review the logic for processing the player score data.
        # Consider using generic method for recovering dataframe.
        # This approach relies on some embedded assumptions about the
        # player score data structure (i.e., either dataframe or data records and orient)        
        # Check whether the player score df has been transformed to data records and orient
        player_score_df = self.mdl.get_df_from_data(player_score_data)
        
        # Filter player_scores to exclude non-pool players
        player_score_df = player_score_df[player_score_df['PlayerId'].isin(self.pool_player_ids)]
        self.player_score_df = player_score_df
        
        self.pool_score_df = self.calc_pool_scores_df(player_score_df)
        self.last_update = player_score_data.get('last_update', None)
        self.status_tag = player_score_data.get('status_tag', None)

        score_data = {
            "last_update": self.last_update,
            "status_tag": self.status_tag
            }
        
        if transform_df:
            score_data['orient'] = orient
            score_data['data'] = self.pool_score_df.to_dict(orient)
        else:
            score_data['df'] = self.pool_score_df

        if append_player_scores:
            player_score_tag = {}
            score_data['player_score_data'] = player_score_tag
            if transform_df:
                player_score_tag['orient'] = orient
                player_score_tag['data'] = player_score_df.to_dict(orient)
            else:
                player_score_tag['df'] = player_score_df
    
        return score_data
    
    def get_post_cut_lineup_for_team(
            self,
            # pool_score_df,
            team_score_row
            ):
    
        row = team_score_row
        
        base_ids = self.pool_player_tags[:4]
        id_cols = self.player_id_cols[:4]
        cut_cols = self.player_made_cut_cols[:4]

        num_missed_cut = (row[cut_cols] == False).sum()
        
        pool_ref_cols = [
            'team_id',
            'TEAM NAME'
            ]
        ref_cols = [ref_col for ref_col in pool_ref_cols if ref_col in team_score_row]
        
        new_row = row[ref_cols].copy()
    
        # sub_id = None
        # is_tb = False
        sub_pos = None
        sit_id = None
        sub_tb = None
        
        # tb_base = 'TB'
        # sub_base = 'SUB'
        id_tag = '_ID'
        
        tb_id_tag = 'TB_ID'
            
        for base_id, id_col, cut_col in zip(base_ids, id_cols, cut_cols):
            
            if (row[cut_col] == False) and (sub_pos is None):
    
                sub_pos = base_id
                # row['SUB_POS'] = sub_pos
                
                sit_id = row[id_col]
                # row['SIT_ID'] = sit_id
                
                if row[tb_id_tag] == row[id_col]:
                    sub_tb = True
                    # row['SUB_TB'] = sub_tb
    
                break
            
        new_row['SUB_POS'] = sub_pos
        new_row['SIT_ID'] = sit_id
        new_row['SUB_TB'] = sub_tb
        new_row['NumCutBefore'] = num_missed_cut
    
        for base_id in base_ids:
            
            out_col = "{}{}".format(base_id, id_tag)
            
            base = "SUB" if base_id == sub_pos else base_id
            id_col = "{}{}".format(base, id_tag)
            
            new_row[out_col] = row[id_col]
            
        new_row['TB_ID'] = row['SUB_ID'] if sub_tb else row['TB_ID']
    
        return new_row      

    def get_post_cut_lineup_df(
            self,
            pool_score_df,
            ):
        
        # TODO Add option for reference columns
        # TODO Add made_cut lines (or recalc pool score)
        # TODO Update lineup and recalc pool score.
        
        rows = []
        for idx, row in pool_score_df.iterrows():
            row = self.get_post_cut_lineup_for_team(row)
            rows.append(row)
            
        df = pd.DataFrame(rows)
            
        return df
    
    # def load_pool_score_data(self):
    #     '''
    #     Loads most recent pool scores and player scores from the remote data service

    #     Returns
    #     -------
    #     pool_score_data : TYPE
    #         DESCRIPTION.

    #     '''

    #     # Get the newest score
    #     collection = self.pool_score_collection
    #     # find_kwargs = {'sort': [('last_update', DESCENDING)]}
    #     kwargs = {'find_kwargs': {'sort': [('last_update', DESCENDING)]}}
                  
    #     # Check for dt_offset
    #     if self.dt_offset is not None:
    #         dt_now = get_now()
    #         dt_then = dt_now - self.dt_offset
    #         kwargs.update({"filter_tag": { "last_update": {'$lt': dt_then}}})
        
    #     pool_score_data = self.mdl.load_remote_data_item(collection, **kwargs)

    #     return pool_score_data        

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
        
    #     self.pool_score_df = pool_score_df
    #     self.last_update = pool_score_data.get("last_update", "missing last update")
    #     self.status_tag = pool_score_data.get("status_tag", "missing_status_tag")

    #     # ************** Testing *********************************
    #     # # Load the saved player scores for the matching update tag
    #     # collection_name = "player_score"
    #     # filter_tag = {'last_update':self.last_update}
    #     # scores_df = self.rdl.load_remote_df(collection_name, filter_tag)
    #     # scores_df = scores_df[scores_df['PlayerId'].isin(self.pool_player_ids)]
    #     # self.pool_player_score_df = scores_df

    #     # Get player score data from pool score data        
    #     player_score_data = pool_score_data.get('player_score_data', None)
    #     if player_score_data is None:
    #         # raise ValueError('Invalid or missing player score data in pool score data set.')
    #         self.pool_player_score_df = None
    #     else:
    #         player_score_df = self.mdl.get_df_from_data(player_score_data)
    #         player_score_df = player_score_df[player_score_df['PlayerId'].isin(self.pool_player_ids)]
    #         self.pool_player_score_df = player_score_df
        
    #     return None

    # def load_pool_scores_df(self):
    #     """
    #     Loads most recent pool score df from the remote data service

    #     Returns
    #     -------
    #     pool_score_df : TYPE
    #         DESCRIPTION.

    #     """
        
    #     self.load_pool_scores()
    #     pool_score_df = self.pool_score_df
        
    #     return pool_score_df

    # def load_pool_player_scores_df(self):
    #     """
    #     Loads most recent pool player score df from the remote data service

    #     Returns
    #     -------
    #     pool_player_score_df : TYPE
    #         DESCRIPTION.

    #     """
        
    #     self.load_pool_scores()
    #     pool_player_score_df = self.pool_player_score_df
        
    #     return pool_player_score_df
    
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

    # TODO Do we need this? If so, refactor to use class variables
    def get_team_player_id_df(
            self, 
            pool_score_df=None, 
            exclude_cut_teams=True):
        
        pool_score_df = self.pool_score_df if pool_score_df is None else pool_score_df

        if exclude_cut_teams:
            pool_score_df = pool_score_df[pool_score_df['MadeCut'] == True]
        
        # Get the ids still in the pool
        team_ids = pool_score_df['team_id']
        
        # Filter pool_id_df for teams who made cut
        pool_id_df = self.pool_id_df
        team_player_id_df = pool_id_df[pool_id_df['team_id'].isin(team_ids)].copy()
            
        # Convert pool id columns to int
        id_cols = ['P1_ID', 'P2_ID', 'P3_ID', 'P4_ID', 'TB_ID']
        team_player_id_df[id_cols] = team_player_id_df[id_cols].astype(int)

        return team_player_id_df

if __name__ == "__main__":

    event_id = 401703504

    ###########################################
    # Get the inputs for the pool event scorer
    ###########################################

    #################################
    # Get the team player picks data    
    #################################

    from devx.pool.pool_event_loader import PoolEventLoader
    
    db_name = 'masters2025_dev'
    
    mdl = MongoDataLoader(db_name=db_name)
    pel = PoolEventLoader(mdl=mdl)

    # This is static and doesn't need to be refreshed
    pool_list_df = pel.load_pool_list_df()
    
    ##############################
    # Get the ESPN player data df
    ##############################

    from devx.espn.golf_event_request import GolfEventRequester
    
    # TODO Replace this with call to load data saved in mongodb,
    
    loader = GolfEventRequester(event_id=event_id)
    
    ged = loader.load_golf_event_data()
    
    comp_data = ged.get_competition_data()
    
    competitors = comp_data.get_competitors()
    
    player_scores_df = competitors.get_player_scores()
    
    athletes = competitors.get_athletes()
    
    athletes_df = athletes.to_df()

    ###################################
    # Initialize the pool event scorer 
    ###################################
    
    pes = PoolEventScorerJson(
            player_list_df=athletes_df,
            pool_list_df=pool_list_df,
        )
    
    # Calculate pool event scores
    pool_scores_df = pes.calc_pool_scores_df(
        player_scores_df=player_scores_df,
        exclude_cut_teams=False)
    
    #####################################
    # Calculate the new lineup with subs
    #####################################

    # Calculate the score for the first two rounds. We can
    # use this for next tournament to calculated the projected
    # cut score for the first two rounds and whether we expect
    # teams to make the cut with or without subs.
    
    post_cut_pool_df = pes.get_post_cut_lineup_df(
        pool_scores_df)
    
    num_teams = len(post_cut_pool_df)
    num_made_cut_before = len(post_cut_pool_df[post_cut_pool_df['NumCutBefore'] == 0])
    print(f"Number of teams who made cut before subs: {num_made_cut_before}/{num_teams}")

    ##################################
    # Add some scoring metric columns
    ##################################
    
    post_cut_pool_df = pes.add_player_score_cols(
        post_cut_pool_df,
        player_scores_df)
    
    post_cut_pool_df = pes.add_made_cut_cols(
        post_cut_pool_df, 
        player_scores_df)
    
    num_made_cut_after = len(post_cut_pool_df[post_cut_pool_df['MadeCut'] == True])
    print(f"Number of teams who made cut after subs: {num_made_cut_after}/{num_teams}")

    num_saved_with_sub = num_made_cut_after - num_made_cut_before    
    print(f"Number of teams who were saved with subs: {num_saved_with_sub}/{num_teams}")
    