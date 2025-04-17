# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 09:54:59 2025

@author: kknow
"""

from dev_util.data_util import DictDataWrapper

from devx.espn.golf_event import GolfEventDataWrapper

# TOOD Implement logger

class ScoreBoardDataWrapper(DictDataWrapper):
    
    def __init__(self, jdata, last_update=None):
        '''
        This is essentially a wrapper class scoreboard data
        for a list of events. In this context, we expect the list
        of events to have one item for a specific golf event, and
        that assumption is currently hard-coded into the method to
        get the golf event data.
        
        Parameters
        ----------
        jdata : TYPE
            DESCRIPTION.
        last_update : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        '''
        
        self._last_update_dt = last_update

        super().__init__(data=jdata)
        
    def get_golf_event_data(self, as_data=False)->GolfEventDataWrapper:
        
        data = self.data
        
        # Expect this to be a dictionary with 
        # - one key: events
        # - a list with one item
        
        events = data.get('events')
        
        if events is None:
            print("No events data found. Unable to get golf event data")
            return None
        
        # Expect a list with one item
        if not isinstance(events, list):
            print("Missing or unexpected data type for events")
            return None

        if len(events) != 1:
            print("Expected 1 event item, got {}".format(len(events)))
            
        event_data = events[0]
        
        if as_data:
            return event_data
        
        event_dw = GolfEventDataWrapper(event_data, last_update=self._last_update_dt)
        
        return event_dw
            