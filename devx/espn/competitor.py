# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 11:18:14 2025

@author: kknow
"""

import pandas as pd

from dev_util.data_util import DictDataWrapper, DataFrameConvertibleList
from dev_util.gen_util import calc_function_time

from devx.espn.athlete import AthleteListDataWrapper

class GolfCompetitorDataWrapper(DictDataWrapper):
    
    def __init__(self, jdata):
        
        super().__init__(data=jdata)

    def __calc_par_score(self, x):

        d = {'-':0, 'E':0, 'DQ':999, 'CUT':999, 'WD':999}
        
        if x is None:
            pname = self.get_nested_item(keys=['athlete', 'displayName'])
            print(f"Mising par score for player: {pname}, par score: {x}")
            return 0

        try:
            val = int(x)
            return val
        except ValueError:
            # pname = self.get_nested_item(keys=['athlete', 'displayName'])
            # print(f"Got value error for player: {pname}, par score: {x}")
            val = d.get(x,x)
            return val
            
        # val = d.get(x,x)
        
        # if val.isnumeric():
        #     val = int(val)
            
        return val
        
    def get_linescores_data(self, as_df=True):

        data = self.data
        
        # Get the scores by round
        linescores = data.get('linescores')
        
        if linescores is None:
            return None
        
        if as_df:
            
            df = pd.DataFrame(linescores)
        
            return df
        
        return linescores
    
    def get_linescores_by_period(self):
        
        linescores_data = self.get_linescores_data()
        
        linescores_by_pd = {d.get('period'):d for d in linescores_data}
        
        return linescores_by_pd
    
    # TODO Genearlize and get cut periods from event data
    def get_cut_score_to_par(self, cut_round=2):
        
        linescores_data = self.get_linescores_data(as_df=False)

        cut_score_to_par = 0
        
        for d in linescores_data:
            period = d.get('period')
            if period <= cut_round:
                score_display = d.get('displayValue')
                score_to_par = self.__calc_par_score(score_display)
                # print(score_to_par)
                cut_score_to_par += score_to_par
        
        return cut_score_to_par        
    
    def get_round_score_summary(self):
        
        linescores_data = self.get('linescores')
        
        scores_by_round = {"R{}".format(d.get('period')):d.get('value') for d in linescores_data}

        return scores_by_round

    def get_round_score_to_par(self):
        
        linescores_data = self.get('linescores')

        # scores_by_round = {"R{}".format(d.get('period')):d.get('value') for d in linescores_data}

        scores_by_round = {}
        
        for d in linescores_data:
            
            period = d.get('period')
            score_display = d.get('displayValue')
            score_to_par = self.__calc_par_score(score_display)

            scores_by_round[f"R{period}_toPar"] = score_to_par
            
        return scores_by_round
        
    def get_player_score_data(self):
        
        # TODO Add parScoreValue
        # TODO Add rankPrior
        
        data = self.data
        
        pid = data.get('id')
        pname = self.get_nested_item(keys=['athlete', 'displayName'])
        
        score_data = data.get('score')
        score_val_tot = score_data.get('value')
        par_score_label = score_data.get('displayValue')
        par_score_val = self.__calc_par_score(par_score_label)
        
        status_data = data.get('status')
        today = status_data.get('displayValue')
        thru = status_data.get('thru')
                
        status_type = status_data.get('type')
        status_tag = status_type.get('name')
        made_cut = False if status_tag == 'STATUS_CUT' else True
        
        pos_data = status_data.get('position')
        pos_val = pos_data.get('id')
        pos_label = pos_data.get('displayName')
        pos_tie = pos_data.get('isTie')
        
        movement = data.get('movement')

        # Get the scores by round
        score_by_round = self.get_round_score_summary()
        score_to_par_by_round = self.get_round_score_to_par()
        
        cut_score_to_par = self.get_cut_score_to_par()
        
        

        # linescores_df = self.get_linescores_data()
        
        # pd_score_map = dict(zip(linescores_df['period'], linescores_df['value']))

        # TODO Refactor column labels and use mapping if needed for backward
        # compatibility
        # Create the output dictionary
        score_data = {
            'position': pos_val,
            'playerId': pid,
            'playerName': pname,
            'parScoreLabel': par_score_label,
            'parScoreValue': par_score_val,
            'today': today,
            'thru': thru,
            'positionChange': movement,
            'positionLabel': pos_label,
            'positionIsTie': pos_tie,
            # 'totalScore': score_val_tot,
            }
        
        score_data.update(score_by_round)
        score_data.update(score_to_par_by_round)

        score_data['cutScoreToPar'] = cut_score_to_par
        score_data['totalScore'] = score_val_tot
        score_data['madeCut'] = made_cut
        
        return score_data


class GolfCompetitorListDataWrapper(DataFrameConvertibleList):
    
    def __init__(self, data:list):
        
        super().__init__(data)
        
    # def to_df(self):
    #     ...
        
    def get_athletes(self, as_wrapper=True)->AthleteListDataWrapper:
        
        lst = self.data
        
        athletes_data = [d.get('athlete') for d in lst]
        
        if as_wrapper:
            
            athletes = AthleteListDataWrapper(athletes_data)
            
            return athletes

        return athletes_data

    @calc_function_time
    def get_player_scores(self, as_df=True):
        
        lst = self.data
        
        pscores = []
        
        for item in lst:
            
            comp = GolfCompetitorDataWrapper(item)
            
            pscore = comp.get_player_score_data()
            pscores.append(pscore)
        
        if as_df:
            df = pd.DataFrame(pscores)
            return df
        
        return pscores        
        
if __name__ == "__main__":
    
    from devx.espn.golf_event_request import GolfEventRequester
    
    event_id = 401703504

    loader = GolfEventRequester(event_id=event_id)
    
    ged = loader.load_golf_event_data()
    
    comp_data = ged.get_competition_data()
    
    competitors = comp_data.get_competitors()
    
    # pscores = []
    # for data in competitors:
        
    #     comp = GolfCompetitorDataWrapper(data)
        
    #     pscore = comp.get_player_score_data()
    #     pscores.append(pscore)
        
    player_score_df = competitors.get_player_scores()
