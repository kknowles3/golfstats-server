# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 10:57:28 2025

@author: kknow
"""

from dev_util.data_util import DictDataWrapper

from devx.espn.competitor import GolfCompetitorListDataWrapper

class GolfCompetitionDataWrapper(DictDataWrapper):
    
    def __init__(self, jdata, last_update=None):
        
        self._last_update_dt = last_update
        
        super().__init__(data=jdata)
        
    def get_current_period(self):
        keys = ['status', 'period']
        return self.get_nested_item(keys=keys)

    def get_competitors(self, as_data=False):
        
        item_tag = 'competitors'
        
        items_data = self.get(item_tag)
        
        if as_data:
            return items_data
        
        items = GolfCompetitorListDataWrapper(items_data)
        
        return items
        
    def get_status(self):
        item_tag = 'status'
        return self.get(item_tag)