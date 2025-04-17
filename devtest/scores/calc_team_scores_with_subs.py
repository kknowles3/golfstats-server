# -*- coding: utf-8 -*-
"""
Created on Sat Apr  9 11:28:12 2022

@author: kknow
"""

import pandas as pd
# from components.data import DB_NAME, SCORE_URL
# from components.data import ege, pool

from dev.espn.espn_golf_event import EspnGolfEvent
from dev.espn.pool_event import PoolEventScorer
# from dev.util.update_util import ScoreUpdater
from dev.util.data_util import RemoteDataServer

class PoolEventScorer2(PoolEventScorer):

    def calc_team_score_data_with_subs(
            self,
            team_id_row,
            # pid_col_names,
            # score_col_names,
            # cut_col_names,
            ):
        
        row = team_id_row.copy()
        
        base_ids = [
            'P1',
            'P2',
            'P3',
            'P4'
            ]

        tb_base = 'TB'
        sub_base = 'SUB'
        
        id_tag = '_ID'
        # score_tag = "_Score"
        cut_tag = '_MadeCut'
        
        cut_cols = ["{}{}".format(bid, cut_tag) for bid in base_ids]
        num_missed_cut = (row[cut_cols] == False).sum()
        row['NumMissedCut'] = num_missed_cut

        # We only do the sub if exactly one player missed the cut
        if num_missed_cut != 1:
            return row
        
        if row["{}{}".format(sub_base, cut_tag)] == False:
            return row
        
        # team_score_ids = []

        # sub_id = None
        # is_tb = False
        sub_pos = None
        sit_id = None
        sub_tb = None
        
        for base_id in base_ids:

            id_col = "{}{}".format(base_id, id_tag)
            cut_col = "{}{}".format(base_id, cut_tag)
            # score_col = "{}{}".format(base_id, score_tag)
            
            if (row[cut_col] == False) and (sub_pos is None):

                sub_pos = base_id
                # row['SUB_POS'] = sub_pos
                
                sit_id = row[id_col]
                # row['SIT_ID'] = sit_id
                
                if row["{}{}".format(tb_base, id_tag)] == row[id_col]:
                    sub_tb = True
                    # row['SUB_TB'] = sub_tb

                break
            
        row['SUB_POS'] = sub_pos
        row['SIT_ID'] = sit_id
        row['SUB_TB'] = sub_tb

        for base_id in base_ids:
            
            out_col = "{}{}2".format(base_id, id_tag)
            
            base = "SUB" if base_id == sub_pos else base_id
            id_col = "{}{}".format(base, id_tag)
            
            row[out_col] = row[id_col]

        return row
    
    def get_post_cut_lineup_for_team(
            self,
            # pool_score_df,
            team_score_row
            ):
    
        row = team_score_row
        
        base_ids = [
            'P1',
            'P2',
            'P3',
            'P4'
            ]
    
        tb_base = 'TB'
        sub_base = 'SUB'
        
        id_tag = '_ID'
        # score_tag = "_Score"
        cut_tag = '_MadeCut'
        
        cut_cols = ["{}{}".format(bid, cut_tag) for bid in base_ids]
        num_missed_cut = (row[cut_cols] == False).sum()
        # df['NumMissedCut'] = num_missed_cut
        
        ref_cols = [
            'team_id',
            'TEAM NAME'
            ]
        
        new_row = row[ref_cols].copy()
    
        # Get the sub-adjusted column mappings
        # col_map = {}
        
        # # We only do the sub if exactly one player missed the cut
        # if num_missed_cut != 1:
        #     return row
        
        # if row["{}{}".format(sub_base, cut_tag)] == False:
        #     return row
        
        # team_score_ids = []
    
        # sub_id = None
        # is_tb = False
        sub_pos = None
        sit_id = None
        sub_tb = None
        
        for base_id in base_ids:
    
            id_col = "{}{}".format(base_id, id_tag)
            cut_col = "{}{}".format(base_id, cut_tag)
            # score_col = "{}{}".format(base_id, score_tag)
            
            if (row[cut_col] == False) and (sub_pos is None):
    
                sub_pos = base_id
                # row['SUB_POS'] = sub_pos
                
                sit_id = row[id_col]
                # row['SIT_ID'] = sit_id
                
                if row["{}{}".format(tb_base, id_tag)] == row[id_col]:
                    sub_tb = True
                    # row['SUB_TB'] = sub_tb
    
                break
            
        new_row['SUB_POS'] = sub_pos
        new_row['SIT_ID'] = sit_id
        new_row['SUB_TB'] = sub_tb
    
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
        
        rows = []
        for idx, row in pool_score_df.iterrows():
            row = self.get_post_cut_lineup_for_team(row)
            rows.append(row)
            
        df = pd.DataFrame(rows)
            
        return df
           
    def calc_pool_scores_df_with_subs(
            self, 
            # pool_score_df, 
            player_score_df,
            pool_id_df=None,
            exclude_cut_teams=False):
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
        
        player_score_col = self.player_score_col
        pool_score_col = self.pool_score_col
        tb_score_col = self.tb_score_col
        
        scores_df = player_score_df
        # 7/20/23 KK: Added drop na to drop players who have nan ids (e.g., amateurs that no one picked)
        scores_df = scores_df[scores_df['PlayerId'].isin(self.pool_player_ids).dropna()]
        self.pool_player_score_df = scores_df
        
        pool_id_cols = pool_id_df.columns.values
        
        # TODO Consider moving to class variable
        pid_col_names = [
            'P1_ID',
            'P2_ID',
            'P3_ID',
            'P4_ID',
            'TB_ID',
            'SUB_ID'
            ]
        pid_col_names = [col for col in pid_col_names if (col in pool_id_cols)]

        # pool_id_df = self.pool_id_df
        
        # # TODO Add validation checks if columns are missing
        # id_cols = [pid_col for pid_col in pid_col_names if pid_col in pool_id_df.columns.values]
        
        # Create the base pool_score_df        
        # Keep all the columns for now
        # pool_score_df = self.pool_id_df.drop(columns=id_cols).copy()
        pool_score_df = pool_id_df.copy()

        # id_df = self.pool_id_df[self.pool_id_df.columns[2:]]
        # id_df = self.pool_id_df[self.pool_id_df.columns[2:]]
        # id_df = pool_id_df[id_cols]

        ## KK 4/7/22: Change score column label
        # id_score_map = dict(zip(scores_df['PlayerId'], scores_df['ParScore'].astype(int)))
        id_score_map = dict(zip(scores_df['PlayerId'], scores_df[player_score_col].astype(int)))
        id_cut_map = dict(zip(scores_df['PlayerId'], scores_df['MadeCut']))
        # Add Charley Hoffman - this is hard-coded for now
        id_cut_map[999] = False

        score_col_names =   [
            'P1_Score', 
            'P2_Score', 
            'P3_Score', 
            'P4_Score', 
            'TB_Score',
            'SUB_Score'
            ]

        ps_col_names = pool_score_df.columns.values
        
        # TODO This needs work to generalize across columns
        for score_col_name, pid_col_name in zip(score_col_names, pid_col_names):
        
            if pid_col_name in ps_col_names:
                pool_score_df[score_col_name] = pool_score_df[pid_col_name].map(id_score_map)
            else:
                print("Column: {} not found in team player ids".format(pid_col_name))

            # pool_score_df = self.pool_id_df.replace(id_score_map)

        pool_score_df[pool_score_col] = pool_score_df[score_col_names[:4]].sum(axis=1)
                
        # Check whether players made cut
        cut_col_names =   [
            'P1_MadeCut', 
            'P2_MadeCut',
            'P3_MadeCut',
            'P4_MadeCut',
            'TB_MadeCut',
            'SUB_MadeCut'
            ]

        # 4/10/25 KK: Possible workaround for downcasting issue with replace
        # pool_score_df[col_names] = id_df.replace(id_cut_map).infer_objects(copy=False)
        # pool_score_df[col_names] = id_df.map(pd.Series(id_cut_map))
        for dest_col, src_col in zip(cut_col_names, pid_col_names):
            # pool_score_df[dest_col] = id_df[src_col].map(pd.Series(id_cut_map))
            pool_score_df[dest_col] = pool_score_df[src_col].map(id_cut_map)
            
            
            
        # # TODO Add logic to handle sub scoring
        # # Get working first, and then optimize calcs

        # # Calculate the team score by team row, optimize later
        # rows = []
        
        # for idx, row in pool_score_df.iterrows():
            
        #     row = self.calc_team_score_data_with_subs(
        #             team_id_row=row,
        #             # pid_col_names,
        #             # score_col_names,
        #             # cut_col_names,
        #             )
            
        #     rows.append(row)
            
            
        # df = pd.DataFrame(rows)
        
        
        
        pool_score_df['MadeCut'] = pool_score_df[cut_col_names[:4]].min(axis=1)
        
        
        
        # TODO Add team made cut and team score
        # Let's first do this by team and then revisit performance optimization
        
        
        
        
        
        
        # pool_score_df['Score'] = pool_score_df.iloc[:, :4].sum(axis=1)
        # pool_score_df['MakeCut'] = pool_score_df[col_names[:4]].max(axis=1) <= cut_line

        # pool_score_df['Rank'] = pool_score_df[pool_score_col].rank(method='min', na_option='bottom')
        # https://stackoverflow.com/questions/41974374/pandas-rank-by-multiple-columns
        pool_score_df['Rank'] = pool_score_df[[pool_score_col, tb_score_col]].apply(tuple, axis=1).rank(method='min', na_option='bottom')

        gb = pool_score_df.groupby(by='MadeCut')
        pool_score_df['CutRank'] = gb['Score'].rank(method='min', na_option='bottom')
        
        if exclude_cut_teams:
            pool_score_df = pool_score_df[pool_score_df['MadeCut'] == True]

        self.pool_score_df = pool_score_df

        return pool_score_df
    
    def calc_pool_score_data_with_subs(
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
        
        self.pool_score_df = self.calc_pool_scores_df_with_subs(player_score_df)
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

if __name__ == "__main__":
    
    from components.app_data import EVENT_CONFIGS
    
    event_tag = 'masters2025'
    event_config = EVENT_CONFIGS[event_tag]

    # SITE_TITLE = event_config['site_title']
    # DB_NAME = event_config['db_name']
    # LOGO_URL = event_config['logo_url']
    # EVENT_TAG = event_config['event_tag']
    # EVENT_ID = event_config['event_id']
    # SCORE_URL = event_config['score_url'].format(EVENT_ID)
    
    # db_name = 'masters2025_dev'
    db_name = 'masters2025_dev'
    # db_name = event_config['db_name']
    
    # event_id = 401703504
    event_id = event_config.get('event_id')
    
    player_score_cname = 'player_score'
    pool_score_cname = 'pool_score'
    score_url = 'https://www.espn.com/golf/leaderboard/_/tournamentId/{}'.format(event_id)
    
    rds = RemoteDataServer(db_name=db_name)
    ege = EspnGolfEvent(rds, score_url)
    pool = PoolEventScorer2(rds)
    # updater = ScoreUpdater(rds, ege, pool)
    
    # Refresh player scores from ESPN site
    transform_df = False
    append_player_scores = True
    
    # TODO Add projected cut scores
    player_score_data = ege.get_player_score_data(transform_df=True, refresh=True)
    pool_score_data = pool.calc_pool_score_data_with_subs(
        player_score_data, 
        transform_df=transform_df, 
        append_player_scores=append_player_scores)
    
    player_score_df = pool_score_data.get('player_score_data',{}).get('df')
    pool_score_df = pool_score_data.get('df')
    
    pool_id_df = pool.get_post_cut_lineup_df(pool_score_df)
    pool_score_df2 = pool.calc_pool_scores_df_with_subs(
        player_score_df=player_score_df,
        pool_id_df=pool_id_df
        )

        
    