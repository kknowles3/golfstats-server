# -*- coding: utf-8 -*-
"""
Created on Sat Apr  9 11:28:12 2022

@author: kknow
"""

# from bs4 import BeautifulSoup

# from components.data import EVENT_CONFIGS
# from components.data import rds, ege, pool
from dev.util.download_util import get_soup
import pandas as pd

# from dev.espn.espn_golf_event import EspnGolfEvent
# from dev.espn.pool_event import PoolEventScorer
# from dev.util.update_util import ScoreUpdater
# from dev.util.data_util import RemoteDataServer

# Test Class for downloading the ESPN golf event field
class EspnGolfField:
    
    def __get_soup_element(self, soup, tag, className=None):
        
        # el = soup.find_all(tag, class_=className)
        d = None
        if className is None:
            el = soup.find(tag)
        else:
            d = {'class': className}
            el = soup.find(tag, d)
        if el is None:
            raise Exception("Unable to find soup element: {}, tag: {}".format(tag, className))
        
        return el

    def __get_scores_tbl_soup(self, score_soup):
        
        # https://www.tutorialspoint.com/python/python_exceptions.htm
        competitors_div = self.__get_soup_element(score_soup, tag="div", className='competitors')
        
        score_div = self.__get_soup_element(competitors_div, "div", 'Table__Scroller')
        
        tbl_soup = self.__get_soup_element(score_div, "table")
        
        return tbl_soup
    
    # @calc_function_time()
    def __get_tbl_header_names(self, tbl_soup):
        
        thead = tbl_soup.find('thead')
        ths = thead.find_all('th')
        
        col_names = [th.text for th in ths]
        
        return col_names

    # @calc_function_time()
    def __get_tbl_row_data(self, tbl_soup):
        
        tbody = tbl_soup.find('tbody')
        trows = tbody.find_all('tr')
        row_data = []
        for row in trows:
            tds = row.find_all('td')
            row_data.append([td.text for td in tds])
            
        return row_data
    
    def __create_df_from_tbl_soup(self, tbl_soup):
        
        col_names = self.__get_tbl_header_names(tbl_soup)
        row_data = self.__get_tbl_row_data(tbl_soup)
        score_df = pd.DataFrame(row_data, columns=col_names)

        return score_df
    
    def get_event_roster(self, url):

        # Load player data
        
        # loader = UrlRequester()
        
        # req = loader.get_request(url)
        
        soup = get_soup(url)
        
        tbl_soup = self.__get_scores_tbl_soup(soup)
        score_df = self.__create_df_from_tbl_soup(tbl_soup)

        roster_df = score_df['PLAYER']
        
        return roster_df

if __name__ == "__main__":
    
    # event_tag = 'masters2022'
    # event_config = EVENT_CONFIGS[event_tag]

    # SITE_TITLE = event_config['site_title']
    # DB_NAME = event_config['db_name']
    # LOGO_URL = event_config['logo_url']
    # EVENT_TAG = event_config['event_tag']
    # EVENT_ID = event_config['event_id']
    # SCORE_URL = event_config['score_url'].format(EVENT_ID)
    
    # rds = RemoteDataServer(db_name=DB_NAME)
    # ege = EspnGolfEvent(rds, SCORE_URL)
    # pool = PoolEventScorer(rds)
    # updater = ScoreUpdater(rds, ege, pool)
    
    # Refresh player scores from ESPN site
    # transform_df = False
    # append_player_scores = True
    # player_score_data = ege.get_player_score_data(transform_df=True, refresh=True)
    # pool_score_data = pool.calc_pool_score_data(player_score_data, transform_df=transform_df, append_player_scores=append_player_scores)
    
    url = 'https://www.espn.com/golf/leaderboard?tournamentId=401353222'

    loader = EspnGolfField()
    player_list = loader.get_event_roster(url)