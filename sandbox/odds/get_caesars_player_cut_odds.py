# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 14:21:31 2023

@author: kknow
"""

import pandas as pd
import os

from dev_util.download_util import UrlRequester
from dev_util.data_util import get_nested_item, set_nested_item

# Test Class for downloading the ESPN golf event field
class SportsbookCutOdds(UrlRequester):
    
    def __init__(self, event_tag, event_id):
        
        # self.odds_div_class = "sportsbook-event-accordion__children-wrapper"
        # self.event_div_class = "game_category_Make/Miss Cut"
        
        # self.event_tag = 'div'
        # self.event_keys = {
        #     # 'aria-labelledby':"game_category_Make/Miss Cut",
        #     'class': "sportsbook-responsive-card-container__card selected"
        #     }
        # self.event_aria_tag = "game_category_Make/Miss Cut"
        
        # self.player_cell_tag = 'div'
        # self.player_cell_keys = 'sportsbook-outcome-cell'
        
        # self.player_name_tag = 'span'
        # self.player_name_keys = {
        #     'class': 'sportsbook-outcome-cell__label'
        #     }
        
        # self.player_odds_tag = 'span'
        # self.player_odds_keys = {
        #     'class': 'sportsbook-odds'
        #     }

        # TODO Do we need these? Might only need event id
        # self.event_tag = 'uspga-championship'
        # self.event_id = 92694
        self.event_tag = event_tag
        self.event_id = event_id
        
        self.url_base = 'https://sportsbook-us-ny.draftkings.com//sites/US-NY-SB/api/v5/eventgroups/{}'.format(self.event_id) + '/categories/{}/subcategories/{}?format=json'
        self.subcat_key = 'offerSubcategoryDescriptors'

        self.win_cat_id = 484
        # self.win_cat_name = 'Tournament Lines'
        self.win_subcat_id = 4508
        
        self.cut_cat_id = 699
        self.cut_subcat_id = 6022
        # self.cut_cat_name = 'Make/Miss Cut'
        
        self.odds_df_col_configs = [
            # {'col': 'participant', 'label': 'player'},
            # {'col': 'oddsAmerican', 'label': 'odds'},
            {'col': 'To Make the Cut', 'label': 'MakeCut'},
            {'col': 'Winner', 'label': 'Winner'},
            {'col': 'Top 5', 'label': 'Top5'},
            {'col': 'Top 10', 'label': 'Top10'},
            ]
    
        super().__init__()
        
        return None
    
    # def __get_soup_element(self, soup, tag, className=None):
        
    #     # el = soup.find_all(tag, class_=className)
    #     d = None
    #     if className is None:
    #         el = soup.find(tag)
    #     else:
    #         d = {'class': className}
    #         el = soup.find(tag, d)
    #     if el is None:
    #         raise Exception("Unable to find soup element: {}, tag: {}".format(tag, className))
        
    #     return el

    def __get_odds_soup(self, page_soup):
        
        # https://www.tutorialspoint.com/python/python_exceptions.htm
        # odds_soup = self.__get_soup_element(odds_soup, tag="div", className=self.odds_div_class)
        
        odds_soup = page_soup.find_all(
            tag=self.event_tag,
            attrs=self.event_keys
            )
        
        return odds_soup
    
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

    def get_player_odds_data(self, player_odds_cell):
        
        # Get player name
        player_name_data = player_odds_cell.find(
            tag=self.player_name_tag,
            attrs= self.player_name_keys
            )
        
        if player_name_data is None:
            print('Unable to get player name')
            return None
        
        player_name = player_name_data.value
        
        # Get player odds
        player_odds_data = player_odds_cell.find(
            tag=self.player_odds_tag,
            attrs= self.player_odds_keys
            )
        
        if player_odds_data is None:
            print('Unable to get odds for player: {}'.format(player_name))
            return None
        
        player_odds = player_odds_data.value
        
        d = {
            'name': player_name,
            'odds': player_odds
            }
        
        return d
    
    def _get_odds_data(self, cat_id, subcat_id):
        
        url_base = self.url_base
        url = url_base.format(cat_id, subcat_id)
        
        jdata = self.get_json_data(url)

        # win_data = None

        keys = ['eventGroup', 'offerCategories']
        offer_cats_data = get_nested_item(d=jdata, keys=keys)
        
        odds_data = {}
        for di in offer_cats_data:
            if di.get('offerCategoryId') == cat_id:
                offer_subcat_key = self.subcat_key
                subcat_data = di.get(offer_subcat_key)
                
                for dj in subcat_data:
                    if dj.get('subcategoryId') == subcat_id:
                        offer_subcat_data = dj.get('offerSubcategory')
                        offers = offer_subcat_data.get('offers')
                        for offer in offers[0]:
                            outcomes = offer.get('outcomes')
                            if outcomes is None:
                                continue
                            label = offer.get('label')
                            odds_data[label] = outcomes
                        break                        
                break                        
        
        return odds_data

    def _get_win_odds(self):

        cat_id = self.win_cat_id
        subcat_id = self.win_subcat_id

        win_data = self._get_odds_data(cat_id=cat_id, subcat_id=subcat_id)
        
        # url_base = self.url_base
 
        # url = url_base.format(cat_id, subcat_id)
        
        # jdata = self.get_json_data(url)

        # # win_data = None

        # keys = ['eventGroup', 'offerCategories']
        # offer_cats_data = get_nested_item(d=jdata, keys=keys)
        
        # win_data = {}
        # for di in offer_cats_data:
        #     if di.get('offerCategoryId') == cat_id:
        #         offer_subcat_key = self.subcat_key
        #         subcat_data = di.get(offer_subcat_key)
                
        #         for dj in subcat_data:
        #             if dj.get('subcategoryId') == subcat_id:
        #                 offer_subcat_data = dj.get('offerSubcategory')
        #                 offers = offer_subcat_data.get('offers')
        #                 for offer in offers[0]:
        #                     outcomes = offer.get('outcomes')
        #                     if outcomes is None:
        #                         continue
        #                     label = offer.get('label')
        #                     win_data[label] = outcomes
        #                 break                        
        #         break                   
        
        return win_data
        
    def _get_cut_odds(self):

        cat_id = self.cut_cat_id
        subcat_id = self.cut_subcat_id

        cut_data = self._get_odds_data(cat_id=cat_id, subcat_id=subcat_id)

        # url_base = self.url_base
 
        # url = url_base.format(cat_id, subcat_id)
        
        # jdata = self.get_json_data(url)

        # # win_data = None

        # keys = ['eventGroup', 'offerCategories']
        # offer_cats_data = get_nested_item(d=jdata, keys=keys)
        
        # cut_data = None
        # for di in offer_cats_data:
        #     if di.get('offerCategoryId') == cat_id:
        #         offer_subcat_key = self.subcat_key
        #         subcat_data = di.get(offer_subcat_key)
                
        #         for dj in subcat_data:
        #             if dj.get('subcategoryId') == subcat_id:
        #                 offer_subcat_data = dj.get('offerSubcategory')
        #                 offers = offer_subcat_data.get('offers')
        #                 cut_data = offers[0][0].get('outcomes')
        #                 break
                        
        #         break                        
        
        return cut_data
    
    def get_event_odds_for_players(self, url):

        # Load player data
        
        # loader = UrlRequester()
        
        # req = loader.get_request(url)
        
        # response = self.get_response(url)

        # # soup = BeautifulSoup(response,"html5lib")
        # soup = BeautifulSoup(response.text,"lxml")
        
        # soup = self.get_soup(url)
        
        # jdata = self.get_json_data(url)

        odds_data = {}

        win_data = self._get_win_odds()
        if len(win_data) > 0:
            odds_data.update(win_data)
            
        cut_data = self._get_cut_odds()
        if len(cut_data) > 0:
            odds_data.update(cut_data)
        
        return odds_data
    
    def get_player_odds_df(self, url):
        
        odds_data = self.get_event_odds_for_players(url)
        
        # Transform the odds table into a flat structure per player
        # flat_key_sets = {
        #     'To Make The Cut': 'MakeCut',
        #     'Winner': 'Winner',
        #     'Top 5': 'Top5',
        #     'Top 10': 'Top10',
        #     }
        
        player_odds = {}
        # for k,flat_key in flat_key_sets.items():
        for odds_cat,dlist in odds_data.items():
            # dlist = odds_data.get(k)
            if dlist is not None:
               for di in dlist:
                   # player = di.get('label')
                   player = di.get('participant')
                   if player is None:
                       print("Found None player")
                   odds = di.get('oddsAmerican')
                   keys = [player, odds_cat]
                   set_nested_item(d=player_odds, keys=keys, val=odds)
        
        df = pd.DataFrame(player_odds).transpose()

        col_configs = self.odds_df_col_configs
        
        df_cols = [d.get('col') for d in col_configs if d.get('col') is not None]
        
        # Filter columns
        df = df[df_cols]
        
        # Rename columns
        df_col_names = {d.get('col'):d.get('label') for d in col_configs if d.get('label') is not None}
        df = df.rename(columns=df_col_names)
        
        return df
        
    # def get_event_odds_df(self, url):
        
    #     df = self.__create_df_from_odds_soup(odds_soup)

    #     df = score_df[['PLAYER']].copy()
        
    #     # Drop amateur tags
    #     df['PLAYER'] = df['PLAYER'].str.replace("(a)", "", regex=False).str.strip()
        
        
    #     roster_df = self.add_roster_columns(df)
        
    #     return roster_df

if __name__ == "__main__":
    
    save_data = False
    path = 'data/2023/pga'
    fname = 'sportsbook_cut_odds.csv'
    event_tag = "uspga-championship"
    event_id = 79720
    
    # url_base = 'https://sportsbook.draftkings.com/leagues/golf/{}?category=make/miss-cut&subcategory=to-make-the-cut'
    # url = url_base.format(event_tag)

    # Found this
    # See notes in OneNote for how to locate this url for the event
    # url = 'https://sportsbook-us-ny.draftkings.com//sites/US-NY-SB/api/v5/eventgroups/{}/categories/699/subcategories/6022?format=json'.format(event_id)
    url = 'https://api.americanwagering.com/regions/us/locations/oh/brands/czr/sb/v3/sports/golf/events/futures'
    loader = SportsbookCutOdds(event_tag=event_tag, event_id=event_id)
    
    # players_odds = loader.get_event_odds_for_players(url)
    # player_odds_df = pd.DataFrame(players_odds)
    player_odds_df = loader.get_player_odds_df(url)
    
    if save_data:
        player_odds_df.to_csv(os.path.join(path, fname))
    