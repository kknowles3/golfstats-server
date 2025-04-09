# -*- coding: utf-8 -*-
"""
Created on Tue May 18 10:33:30 2021

@author: kknow

Site with overview of ESPN apis:

http://www.espn.com/apis/devcenter/overview.html

STATUS CODE	DESCRIPTION
200 (OK)	Request was successful.
400 (Bad Request)	Invalid format for your request. Make sure you're passing in the correct parameters.
401 (Unauthorized)	Not authorized to make this request. Check the API documentation to be sure that you have access to the API or portion of the API you're making a request to.
403 (Account Over Rate Limit)	You have exceeded the allowable number of API queries for your access level.
404 (Not Found)	The requested resource could not be found. Check spelling and review feed docs.
500 (Internal Server Error)	Server side error processing request. Please try again later.
504 (Gateway Timeout)	Server timed out trying to fulfill your request. Please try again later.

"""

from dev.util.download_util import UrlRequester
from dev.util.app_util import get_now

import pandas as pd

class PgaEventDataLoader():
    """
    Class for loading PGA data from ESPN site
    """
    
    def __init__(self):
        
        # TODO notice league=pga tag in query string.  Check to see if this consistent across events.  If so, find other event tags
        # self.__query_str = 'sport=golf&league=pga&region=us&lang=en&contentorigin=espn&buyWindow=1m&showAirings=buy%2Clive%2Creplay&showZipLookup=true&tz=America/New_York'
        # self.__query_str = 'sport=golf&league=pga&region=us&lang=en&contentorigin=espn&tz=America/New_York'
        # self.__scoreboard_url = 'https://site.web.api.espn.com/apis/v2/scoreboard/header?{}'.format(self.__query_str)
        self.__scoreboard_url = 'https://api.pga.com/graphql'

        self.__last_update = None        
        self.__scoreboard_json = None
        self.__event_json = None

        self.__headers = { 
            
            # :authority: api.pga.com
            # :method: POST
            # :path: /graphql
            # :scheme: https
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'content-length': '1397',
            'content-type': 'application/json',
            'dnt': '1',
            'origin': 'https://www.pga.com',
            'pragma': 'no-cache',
            'referer': 'https://www.pga.com/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'

            }

        self.__requester = UrlRequester(self.__headers)

    def refresh_scoreboard(self):
        """
        Loads scoreboard data from ESPN site

        Returns
        -------
        None.

        """

        # TODO find last ESPN update within scoreboard data
        self.__last_update = get_now()
        # self.__scoreboard_json = self.__requester.get_json_data(self.__scoreboard_url)
        self.__scoreboard_json = self.__requester.post(url=self.__scoreboard_url)
        
        return None
        
    def get_scoreboard_json(self, refresh=False):
        """
        Gets the most recent scoreboard json

        Parameters
        ----------
        refresh : TYPE, optional
            Triggers a reload of the data from ESPN site. The default is False.

        Returns
        -------
        TYPE
            The full scoreboard json data set from ESPN site.

        """
        if refresh:
            self.refresh_scoreboard()
        
        return self.__scoreboard_json
    
    def get_event_json(self, refresh=False):
        """
        The event data is buried deep within the scoreboard data set.  For now, 
        using a methodical approach to drill into each level

        Parameters
        ----------
        refresh : TYPE, optional
            Triggers a reload of the data from ESPN site. The default is False.

        Returns
        -------
        JSON
            The event data in json format

        """
        
        scoreboard_json = self.get_scoreboard_json(refresh=refresh)
        
        # TODO Add null checking and error logging
        if scoreboard_json is None:
            return None
        
        sports_json = scoreboard_json.get('sports', None)
        if sports_json is None:
            return None
        
        if len(sports_json) < 1:
            return None
        
        leagues_json = sports_json[0].get('leagues', None)
        if leagues_json is None:
            return None

        if len(leagues_json) < 1:
            return None
        
        events_json = leagues_json[0].get('events', None)
        if events_json is None:
            return None

        if len(events_json) < 1:
            return None
        
        self.__event_json = events_json[0]
        
        return self.__event_json

    def get_player_list_json(self, refresh=True):
        
        event_json = self.get_event_json(refresh=refresh)
        
        if event_json is None:
            return None
        
        player_json = event_json.get('competitors', None)
        
        return player_json
        
# For testing
if __name__ == '__main__': 
    
    pdl = PgaEventDataLoader()
    scoreboard_json = pdl.get_scoreboard_json(refresh=True)
    
    event_json = pdl.get_event_json()
    player_json = pdl.get_player_list_json()
    
    df = pd.DataFrame(player_json)
    
    print(pdl.__scoreboard_url)