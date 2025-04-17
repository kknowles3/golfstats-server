# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 10:16:58 2025

@author: kknow
"""

from dev_util.datetime_util import get_now
from dev_util.request_util import UrlRequester

from devx.espn.golf_event import GolfEventDataWrapper
from devx.espn.scoreboard import ScoreBoardDataWrapper

from components.app_logger import logger

from dev_util.gen_util import calc_function_time

class GolfEventRequester(UrlRequester):
    '''
    Class for downloading golf event json data from ESPN site.
    Does not currently save data.
    
    '''
    
    def __init__(self, event_id=None):
        
        self._event_id = event_id
        
        self.score_url_base = 'https://site.web.api.espn.com/apis/site/v2/sports/golf/leaderboard?league=pga&region=us&lang=en&event={}'
        
        super().__init__()
        
    def load_scoreboard_data(self, event_id=None)->ScoreBoardDataWrapper:
        '''
        Gets the scoreboard wrapper class for the golf event data.
        The current recommendation is to call the golf event data
        method directly, unless there is a need to debug or inspect
        the scoreboard wrapper data.

        Parameters
        ----------
        event_id : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        ScoreBoardDataWrapper
            DESCRIPTION.

        '''
        update_dt = get_now()
        
        event_id = self._event_id if event_id is None else event_id
        
        url = self.score_url_base.format(event_id)
        
        jdata = self.get_json_data(url)
        
        if jdata is None:
            logger.warn(f"No golf event data found for event id: {event_id}")
            return None
        
        # ged = GolfEventDataWrapper(jdata=jdata, last_update=update_dt)
        scoreboard = ScoreBoardDataWrapper(jdata, last_update=update_dt)
        
        return scoreboard

    @calc_function_time
    def load_golf_event_data(self, event_id=None, scoreboard=None)->GolfEventDataWrapper:
        
        scoreboard = self.load_scoreboard_data(event_id=event_id) if event_id is None else event_id
        
        if scoreboard is None:
            logger.warn(f"No scoreboard data found for event id: {event_id}")
            return None
        
        ged:GolfEventDataWrapper = scoreboard.get_golf_event_data()
        
        return ged
    
if __name__ == "__main__":
    ...
    
    event_id = 401703504

    loader = GolfEventRequester(event_id=event_id)
    
    # scoreboard = loader.load_scoreboard_data(event_id=event_id)
    
    ged = loader.load_golf_event_data()
    
    competition = ged.competition
    
    competitors = competition.get_competitors()
    
    athletes = competitors.get_athletes()
    
    athletes_df = athletes.to_df()
