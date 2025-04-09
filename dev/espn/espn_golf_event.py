# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 13:36:15 2021

@author: kknow
"""

from dev.util.download_util import get_soup
import pandas as pd

from dev.util.data_util import RemoteDataLoader
from dev.util.app_util import get_now

# Class that represents a single golf event with data retrieved from ESPN site
class EspnGolfEvent():
    
    def __init__(self, rdl:RemoteDataLoader, score_url):
        
        # self.player_list_path = os.path.join(APP_PATH, 'data')
        # self.player_list_fname = 'espn_list2.csv'
        
        self.rdl = rdl        
        self.score_url = score_url
        
        self.player_list_collection = 'espn_pool_player_list' # TODO Move to app config data
        self.player_score_collection = 'player_score'
        self.espn_player_col = 'EspnPlayer'
        self.espn_id_col = 'ID'
        self.espn_player_score_col = 'SCORE'
        
        self.__score_soup = None
        self.__status_tag = None
        self.eventId = None
        self.status_tag = None
        self.scores_df = None
        self.last_update = None
        self.update_fmt_string = "%m/%d/%y %I:%M:%S %p"
        self.player_list_df = None
        # self.pool_espn_map = None
        self.player_id_map = None
        self.cut_score = None
        
        self.__initialize()
    
    def __initialize(self):
        
        # Load the player list
        # df = self.__load_player_list()
        # self.player_list_df = df
        # self.pool_espn_map = dict(zip(df['PoolName'], df['PLAYER']))
        df = self.__load_player_list()
        self.player_id_map = dict(zip(df[self.espn_player_col], df[self.espn_id_col]))
        
        return None

    def __load_player_list(self):
        
        rdl = self.rdl
        collection = self.player_list_collection
        
        # Throw exception if rds isn't valid
        if rdl is None:
            raise Exception("Unable to load player list. Missing or uninitialized RemoteDataServer.")

        # TODO retrieve data and get last udpate tag
        # nonsense = rdl.test_method()
        
        # player_list_data = self.rdl.load_remote_data(self.player_list_collection)
        player_list_df = rdl.load_remote_df(collection)
        
        return player_list_df

    # def __load_player_list(self):
        
    #     fname = os.path.join(self.player_list_path, self.player_list_fname)
    #     player_list_df = pd.read_csv(fname, index_col=False)
        
    #     return player_list_df
    
    # TODO Add flag for whether to throw exception
    # TODO consider moving to soup utility class
    # @calc_function_time()
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

    def __get_status_tag(self, score_soup):
        
        status_div = self.__get_soup_element(score_soup, 'div', className="status")
        spans = status_div.find_all("span")
        
        status_tag = spans[0].text
        
        return status_tag
        
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
    
    def __calc_par_score(self, x):
        
        if x is None:
            return x

        d = {'-':'0', 'E':'0', 'DQ':'999', 'CUT':'999', 'WD':'999'}
        val = d.get(x,x)
        
        if val.isnumeric():
            val = int(val)
            
        return val
        
    def refresh_scores(self):
        """
        Refreshes and loads player scores from ESPN website.

        Returns
        -------
        df : TYPE
            returns a dataframe of current player scores.

        """
        
        self.last_update = get_now()
        # dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        
        score_soup = get_soup(self.score_url)
        self.__score_soup = score_soup
        
        self.status_tag = self.__get_status_tag(score_soup)
        
        # ****************************************************************
        # TODO Add check_status_tag method to handle various status events
        # Tournament Field - Tournament has not started, so we can't get scores
        
        tbl_soup = self.__get_scores_tbl_soup(score_soup)
        df = self.__create_df_from_tbl_soup(tbl_soup)
        
        # Drop None rows
        df = df.dropna()
        
        df_cols = df.columns.values

        if 'PLAYER' in df_cols:
            df['PlayerId'] = df['PLAYER'].map(self.player_id_map)
        
        # Check whether scoring columns exist
        # if 'TO PAR' in df_cols:
        score_col = self.espn_player_score_col
        if score_col in df_cols:            
            # d = {'E':0}
            # df['ParScore'] = df['TO PAR'].map(lambda x: int(d.get(x, x))).astype(int)
            df['ParScore'] = df[score_col].map(lambda x: self.__calc_par_score(x))
            
            # 6/13/214 KK: TOODO Add handling of players who haven't started
            df['Rank'] = df['ParScore'].astype(int).rank(method='min', na_option='bottom')
            df['MadeCut'] = df['ParScore'] != 999
            self.cut_score = df[df['Rank'] <= 50]['ParScore'].astype(int).max()
            
            # TODO check to see if TOT column exists
            # Add rank from prior day and today's ranking change
            if 'TOT' in df.columns.values:
                df['RankPrior'] = df.loc[(df['TOT'] != "--") & (df['MadeCut'] == True)]['TOT'].rank(method='min', na_option='bottom')
                df['RankChg'] = df['Rank'] - df['RankPrior']

        # Remove columns with blank labels
        col_names = [col for col in df.columns.values if col != ""]
        df = df[col_names]
            
        self.scores_df = df
        
        return df
    
    def get_last_update_tag(self):
        """
        Gets a formatted string with the last update time. The format
        is set by the update_fmt_string parameter

        Returns
        -------
        update_tag : TYPE
            DESCRIPTION.

        """
        
        update_tag = None if self.last_update is None else self.last_update.strftime(self.update_fmt_string)
        
        return update_tag

    # def load_player_scores(self):
    #     '''
    #     Refreshes and loads player scores from ESPN website.
    
    #     Returns
    #     -------
    #     player_score_df : TYPE
    #         returns a dataframe of current player scores.
    
    #     '''
        
    #     self.refresh_scores()
    #     player_score_df = self.scores_df
        
    #     return player_score_df

    # TODO consider a better way to handle the df transformation step
    def get_player_score_data(self, transform_df=False, orient='split', refresh=True):
        '''
        Refreshes and loads player score data, including the scores for each player, plus some additional
        metadata describing the update.  Includes an option to transform the score df into 
        record format for remote data storage.
    
        Parameters
        ----------
        ege : EspnGolfEvent
            DESCRIPTION.
        transform_df : TYPE, optional
            choose whether to convert score df to record format. The default is True.
        orient : TYPE, optional
            format for transforming df to records, if transforming. The default is 'split'.
        refresh : boolean, optional
            choose whether to refresh player scores.  The default is True.
    
        Returns
        -------
        score_data : TYPE
            returns a dictionary of player score data.
    
        '''
        
        if refresh:
            df = self.refresh_scores()
        else:
            df = self.scores_df
    
        score_data = {
            'last_update': self.last_update,
            'status_tag': self.status_tag,
            }
        
        if transform_df:
            score_data['orient'] = orient
            score_data['data'] = df.to_dict(orient)
        else:
            score_data['df'] = df
            
        return score_data    
