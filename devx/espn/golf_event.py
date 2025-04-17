# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 10:00:25 2025

@author: kknow
"""

from dev_util.data_util import DictDataWrapper

from devx.espn.golf_competition import GolfCompetitionDataWrapper

class GolfTournamentDataWrapper(DictDataWrapper):

    def _get_cut_count(self):
        item_tag = 'cutCount'
        return self.get(item_tag)

    def _get_cut_round(self):
        item_tag = 'cutRound'
        return self.get(item_tag)

    def _get_cut_score(self):
        item_tag = 'cutScore'
        return self.get(item_tag)

    def _get_display_name(self):
        item_tag = 'displayName'
        return self.get(item_tag)
        
    # Class properties
    cutCount = property (fget=_get_cut_count)
    cutRound = property (fget=_get_cut_round)
    cutScore = property (fget=_get_cut_score)
    displayName = property (fget=_get_display_name)

class GolfEventDataWrapper(DictDataWrapper):
    '''
    Wrapper class for the full golf event data set, including:
    
    - Metadata for the tournament event, e.g., tournament status
    - Player details, scoring data, and summary statistics
    
    '''
    
    def __init__(self, jdata, last_update=None):
        
        self._last_update_dt = last_update
        
        super().__init__(data=jdata)
        
    def _get_tournament_data(self, as_data=False):
        
        item_tag = 'tournament'
        
        item_data = self.get(item_tag)
        
        if as_data:
            return item_data
        
        return GolfTournamentDataWrapper(item_data)
    
    def _get_tournament_name(self):
        item_tag = 'name'
        return self.get(item_tag)

    def get_competition_data(self, as_data=False)->GolfCompetitionDataWrapper:     
        
        item_tag = 'competitions'
        
        items = self.get(item_tag)
        
        if items is None:
            print(f"No {item_tag} data found. Unable to get golf competitor data")
            return None
        
        # Expect a list with one item
        if not isinstance(items, list):
            print(f"Missing or unexpected data type for {item_tag}")
            return None

        if len(items) != 1:
            print("Expected 1 {} item, got {}".format(item_tag, len(items)))
            
        item_data = items[0]
        
        if as_data:
            return item_data
        
        competition_dw = GolfCompetitionDataWrapper(item_data, last_update=self._last_update_dt)
        
        return competition_dw
    
    def _has_course_stats(self):
        item_tag = 'hasCourseStats'
        return self.get(item_tag)
    
    def _has_player_stats(self):
        item_tag = 'hasPlayerStats'
        return self.get(item_tag)

    def _is_complete(self):    
        keys = ['status', 'type', 'completed']
        return self.get_nested_item(keys=keys)
    
    def get_status(self):
        item_tag = 'status'
        return self.get(item_tag)
        
    # Class properties
    hasCourseStats = property(fget=_has_course_stats)
    hasPlayerStats = property(fget=_has_player_stats)
    
    # competition = property(fget=_get_competition)
    tournament = property(fget=_get_tournament_data)
    name = property(fget=_get_tournament_name)
    

            