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
import os

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
    
    def add_roster_columns(self, df):
        
        first_last_df = df['PLAYER'].str.split(" ", n=1, expand=True)
        df = pd.concat([df, first_last_df], ignore_index=True, axis=1)
        
        df.columns = ['Player', 'first_name', 'last_name']
        
        df = df.sort_values(by=['last_name', 'first_name']).reset_index(drop=True)
        
        df.index.name = 'ID'
        
        return df

    def get_event_roster_df(self, url, drop_amateur_tags=True):

        # Load player data
        
        # loader = UrlRequester()
        
        # req = loader.get_request(url)
        
        soup = get_soup(url)
        
        tbl_soup = self.__get_scores_tbl_soup(soup)
        score_df = self.__create_df_from_tbl_soup(tbl_soup)

        df = score_df[['PLAYER']].copy()
        
        # Drop amateur tags
        if drop_amateur_tags:
            df['PLAYER'] = df['PLAYER'].str.replace("(a)", "", regex=False).str.strip()
        
        roster_df = self.add_roster_columns(df)
        
        return roster_df
    
if __name__ == "__main__":
    
    save_data = True
    path = 'data/2025/masters'
    fname = 'espn_field.csv'
    
    event_id = 401703504
    url = 'https://www.espn.com/golf/leaderboard?tournamentId={}'.format(event_id)

    loader = EspnGolfField()
    
    roster_df = loader.get_event_roster_df(
        url, 
        drop_amateur_tags=False)
    
    if save_data:
        roster_df.to_csv(os.path.join(path, fname))
    