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
        
        # self.url_base = 'https://sportsbook-us-ny.draftkings.com//sites/US-NY-SB/api/v5/eventgroups/{}'.format(self.event_id) + '/categories/{}/subcategories/{}?format=json'
        # self.url_base = 'https://sportsbook-us-ny.draftkings.com//sites/US-NY-SB/api/v5/eventgroups/{}'.format(self.event_id) + '/categories/{}/subcategories/{}?format=json'
        self.url_base = 'https://sportsbook-nash-usny.draftkings.com/sites/US-NY-SB/api/v5/eventgroups/{}'.format(self.event_id) + '?format=json&categoryId={}'

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
            # {'col': 'To Make the Cut', 'label': 'MakeCut'},
            {'col': 'To Make The Cut', 'label': 'MakeCut'},
            {'col': 'Winner', 'label': 'Winner'},
            # {'col': 'Top 5', 'label': 'Top5'},
            # {'col': 'Top 10', 'label': 'Top10'},
            {'col': 'Top 5 (Including Ties)', 'label': 'Top5'},
            {'col': 'Top 10 (Including Ties)', 'label': 'Top10'},
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
        # url = url_base.format(cat_id, subcat_id)
        url = url_base.format(cat_id, subcat_id)
        
        jdata = self.get_json_data(url)

        # win_data = None
        
        if jdata is None:
            print("No odds data found for url: {}".format(url))
            return None

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
        if cut_data is None:
            print("No cut odds found for event")
        else:
            if len(cut_data) > 0:
                odds_data.update(cut_data)
        
        return odds_data
    
    def get_player_odds_json(self, url):
        
        jdata = self.get_json_data(url)
        
        return jdata
    
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
        df_cols = [df_col for df_col in df_cols if df_col in df.columns.values]
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
    
    # Find this info from this site:
    # https://sportsbook.draftkings.com/leagues/golf
    # https://sportsbook.draftkings.com/leagues/golf/us-open?category=make%2Fmiss-cut&subcategory=to-make-the-cut
    # Need to inspect page and look at Network tab to find details:
    save_data = True
    path = 'data/2025/masters'
    fname = 'sportsbook_cut_odds.csv'
    event_tag = "masters2025"
    # event_id = 24222
    # event_id = 92694
    # event_id = 79720
    # event_id = 42731
    event_id = 92694
    
    # url_base = 'https://sportsbook.draftkings.com/leagues/golf/{}?category=make/miss-cut&subcategory=to-make-the-cut'
    # url = url_base.format(event_tag)

    # Found this
    # See notes in OneNote for how to locate this url for the event
    # url = 'https://sportsbook-us-ny.draftkings.com//sites/US-NY-SB/api/v5/eventgroups/{}/categories/699/subcategories/6022?format=json'.format(event_id)
    url = "https://sportsbook-nash-usny.draftkings.com/sites/US-NY-SB/api/v5/eventgroups/{}?format=json".format(event_id)
    
    # TO Get the make/miss cut odds
    # "https://sportsbook-nash-usny.draftkings.com/sites/US-NY-SB/api/v5/eventgroups/79720?format=json&categoryId=699"
    
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        # "Cache-Control": "max-age=0",
        "Cache-Control": "no-cache",
        # "Cookie": '_csrf=368e1317-d0c6-483c-b3e5-6752fe1eaaf1; STIDN=eyJDIjoxMjIzNTQ4NTIzLCJTIjo2ODc2ODU3NDM5NSwiU1MiOjcyMzk5MTM1NzQ0LCJWIjo0NDQ4NjE2NjE0NiwiTCI6MSwiRSI6IjIwMjQtMDUtMTVUMjI6MzQ6MjguNjg0Mjk0MVoiLCJTRSI6IlVTLURLIiwiVUEiOiJRTFdOc0FhZEduUHVuU1A2VklkR0ZVdXZETmRQcnNpaUVCa21EMFV5RU5rPSIsIkRLIjoiZjFiZGU0NjQtODA5Yi00ZDQ0LTk2ZTAtOWRiOTVmMTE0OWI3IiwiREkiOiIxNzdiMzI3MC0yYTU3LTRjNGUtYjFmNS02ZmZmNTc1MGU2ZjUiLCJERCI6NDI4NTM0NzE1NDB9; STH=85944cd08a78b63ff6b10d6b0add01f05f91544de1606f7177f79bb6254a0040; ak_bmsc=F3EF2C0797BBBA5D3DB5B5FC125F9C61~000000000000000000000000000000~YAAQzgLEF7z9VVSPAQAAwhNJfhd3nlSHNdeMCUulatnWeZcJlx1EV09SEiazjurEXOkcPCPtrLW/Rn33VK0CF8UdtJgH0bBLSkmlIzjsHd121YXHJ8me4yVt0GgNLDYS6uu9tlcpOM+GPUYpvAAfuRYM61p+9nAFaAtD4bb2H1skWw/AORQuhmUMBbZKFeO96L+WMX6TpSP/9iUIemVs0x5RzDoVE0a4NAh+yeIupMuE+kRWKp02GOLZtf715Ls1H4bujZGuKgihi8pDc0kHC2wjay/cWdCxRTiwoTK96Q8bnBk4V8YMoyD4bEs3Y55okmaTVk6k4CYxvV6stpw462Okfkgx4ugQm0bqkUtOSZeYaFFYWPJYCq8N3LqqimNIFUSgJGuIzfhKDCB01/3I; _gcl_au=1.1.474362510.1715810674; _ga=GA1.1.1172170308.1715810674; _tguatd=eyJzYyI6ImR1Y2tkdWNrZ28uY29tIn0=; _tgpc=a5a646ac-89ce-5dfa-a383-e7d7be952005; _tgidts=eyJzaCI6ImQ0MWQ4Y2Q5OGYwMGIyMDRlOTgwMDk5OGVjZjg0MjdlIiwiY2kiOiI1M2UwOWM2MC1mYTA3LTVkNTUtYTU5Zi1iMDcyYTE3OGExOTgiLCJzaSI6Ijg3OGU0OGMyLWQyZGMtNWUxNC1hMTJjLWQ0NzVkMmE2MmZjZiJ9; _scid=8df1df2b-a472-44e0-9a73-3ca68dba644c; ab.storage.deviceId.b543cb99-2762-451f-9b3e-91b2b1538a42=%7B%22g%22%3A%226529a6e4-f28d-0b7b-50e7-218ee7d4988b%22%2C%22c%22%3A1715810674637%2C%22l%22%3A1715810674637%7D; __ssid=c1b44729d7ef2e904cb58a64e751d2a; _sp_srt_ses.16f4=*; _sctr=1%7C1715745600000; _abck=719AADE5BFA8A1655C876AD2DE52A21E~0~YAAQzgLEF9YLVlSPAQAAvIBJfgvzZUeYwvilrh0t7AhVoqv8tAyxirE+b9kvrJM9lDYp4njnHZVeFWgGCneOnwcTDoP3gvBMVl+Az4Q68DgyYBUydTBu+FT2vQRmppp/oIVDs7yG/1/o22+AW9yEHHTrwYUL+oaFtmfhA/e5sdpeU9cNBbBJblRPLc6RiOuZVi/AMbi8tZMQEkBMlez1h75oz0Wto6uXEZ3e2cCbHoGkwQqPLstSf8vULdOPWt7QpQr+l0knxTbjivrXHXaZqYyo9ZG8iJm3Hc1uHKWIzpvDRJkbTd1Z3mY6SdhlQbrPApNMor6RoSTjsEEIgOrTX1FUJ2rmJL8WfRzeuc1grVOeyKUQPZHWseaYC+fHsbvRY+g7hrAErpmDIogZ//mOoFhqwp+SC1r9PwNuNrVoh1sifWy2A+YatA/5CM0MQKBApZG1PAUTkePXMaICBBE=~-1~||0||~-1; _tglksd=eyJzIjoiODc4ZTQ4YzItZDJkYy01ZTE0LWExMmMtZDQ3NWQyYTYyZmNmIiwic3QiOjE3MTU4MTA2NzQ1OTcsInNvZCI6ImR1Y2tkdWNrZ28uY29tIiwic29kdCI6MTcxNTgxMDY3NDU5Nywic29kcyI6ImMiLCJzb2RzdCI6MTcxNTgxMDcxODkyNH0=; _scid_r=8df1df2b-a472-44e0-9a73-3ca68dba644c; _tgsid=eyJscGQiOiJ7XCJscHVcIjpcImh0dHBzOi8vc3BvcnRzYm9vay5kcmFmdGtpbmdzLmNvbSUyRmxlYWd1ZXMlMkZnb2xmJTJGdXNwZ2EtY2hhbXBpb25zaGlwXCIsXCJscHRcIjpcIkdvbGYlMjBCZXR0aW5nJTIwT2RkcyUyMCUyNiUyMExpbmVzJTNBJTIwUEdBJTIwQ2hhbXBpb25zaGlwJTIwLSUyMFRpZ2VyJTIwU3BlY2lhbHMlMjAlN0MlMjBEcmFmdEtpbmdzJTIwU3BvcnRzYm9va1wiLFwibHByXCI6XCJodHRwczovL2R1Y2tkdWNrZ28uY29tXCJ9IiwicHMiOiI1MWI1MjVmNS1jMDkwLTQ3MWItOTcyZi1mOTliM2Q3YjBiZTYiLCJwdmMiOiI0Iiwic2MiOiI4NzhlNDhjMi1kMmRjLTVlMTQtYTEyYy1kNDc1ZDJhNjJmY2Y6LTEiLCJlYyI6IjciLCJwdiI6IjEiLCJ0aW0iOiI4NzhlNDhjMi1kMmRjLTVlMTQtYTEyYy1kNDc1ZDJhNjJmY2Y6MTcxNTgxMDY3Nzk2NDotMSJ9; _uetsid=1e268bc0130711efa6d3e542cbdd2685; _uetvid=1e26b110130711ef899381ee03e6d9a5; _sp_srt_id.16f4=77278889-d193-4ad9-8651-4ea5a9174dc4.1715810677.1.1715810810..e73525e7-6ee4-45ba-8a13-0b60fa510c91....0; RoktSessionId-2658406244650637672=b171016b-cef1-4637-adbd-6741607f0000|false|1715812612318; _rdt_uuid=1715810674564.55e67e80-ea89-4df0-b0de-c26ea14a1e1c; ab.storage.sessionId.b543cb99-2762-451f-9b3e-91b2b1538a42=%7B%22g%22%3A%223da4152d-cff7-a7ef-3d7d-9d9e2a243fb1%22%2C%22e%22%3A1715812743117%2C%22c%22%3A1715810674634%2C%22l%22%3A1715810943117%7D; _ga_QG8WHJSQMJ=GS1.1.1715810674.1.1.1715810943.59.0.0; bm_sz=024304F357FA9F3C47CB1C3868397C04~YAAQ35QzuPQluEyPAQAAz39OfhcO5BxJw29I+jzrVIMOmK7PGt16otgZBPgl3J43iMeZ/u+p4qW3styKSDFvaqFyHF3UZey6LiNnE0PCMZVwqPYtzGdcJf2thyT0JsZVDUwW61C4/YWmbrD/VcZ9T18aJs3kHHVaZhcTShIFv5QU04UjZsoBnQaP18LqLmyN8GhI8e3gvkV3vWJXhLFeZCgJ93lbu4PPhPkzxLBNK5P/sRD1F9fjNHt08+XSup5Zcb49xd4B8osB31tqhhAwuUfkptGdkBKCG1ZwxpB4fj9PUC9bs4jYNcTpu3qvfYF337c1KMTjk+A7jCak+55huryqU3WufXnZTfoQbkZHm+uUr4F2EXfxghK85+SWdh12pWuV20j1gc7M/+j3EGvp0ZXixOCG9GeYyKzhdNIWZd9Fst3B/BmH/rXLK6pJP2c8U1prGSVBKew=~3158578~4404546; hgg=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aWQiOiI0NDQ4NjE2NjE0NiIsImRraC0xMjYiOiI4MzNUZF9ZSiIsImRrZS0xMjYiOiIwIiwiZGtlLTIwNCI6IjcxMCIsImRrZS0yODgiOiIxMTI4IiwiZGtlLTMxOCI6IjEyNjEiLCJka2UtMzQ1IjoiMTM1MyIsImRrZS0zNDYiOiIxMzU2IiwiZGtlLTQyOSI6IjE3MDUiLCJka2UtNzAwIjoiMjk5MiIsImRrZS03MzkiOiIzMTQwIiwiZGtlLTc1NyI6IjMyMTIiLCJka2gtNzY4IjoicVNjQ0VjcWkiLCJka2UtNzY4IjoiMCIsImRrZS04MDYiOiIzNDI1IiwiZGtlLTgwNyI6IjM0MzciLCJka2UtODI0IjoiMzUxMSIsImRrZS04MjUiOiIzNTE0IiwiZGtlLTgzNiI6IjM1NzAiLCJka2gtODk1IjoiOGVTdlpEbzAiLCJka2UtODk1IjoiMCIsImRrZS05MDMiOiIzODQ4IiwiZGtlLTkxNyI6IjM5MTMiLCJka2UtOTQ3IjoiNDA0MiIsImRrZS05NzYiOiI0MTcxIiwiZGtlLTEyNzciOiI1NDExIiwiZGtlLTEzMjgiOiI1NjUzIiwiZGtlLTE1NjEiOiI2NzMzIiwiZGtlLTE1ODEiOiI2ODI5IiwiZGtoLTE2NDEiOiJSMGtfbG1rRyIsImRrZS0xNjQxIjoiMCIsImRrZS0xNjUzIjoiNzEzMSIsImRrZS0xNjU2IjoiNzE1MSIsImRrZS0xNjg2IjoiNzI3MSIsImRrZS0xNjg5IjoiNzI4NyIsImRrZS0xNjk1IjoiNzMyOSIsImRrZS0xNzA5IjoiNzM4MyIsImRrZS0xNzIyIjoiNzQ1NiIsImRrZS0xNzQwIjoiNzUyNiIsImRrZS0xNzQyIjoiNzUzNiIsImRrZS0xNzUxIjoiNzU4MCIsImRrZS0xNzU0IjoiNzYwNSIsImRrZS0xNzYwIjoiNzY0OSIsImRrZS0xNzY2IjoiNzY3NSIsImRrZS0xNzcwIjoiNzY5MiIsImRrZS0xNzc0IjoiNzcxMCIsImRrZS0xNzc4IjoiNzcyNSIsImRrZS0xNzgwIjoiNzczMSIsImRrZS0xNzg5IjoiNzc3MCIsImRrZS0xNzkzIjoiNzc5NiIsImRrZS0xNzk0IjoiNzgwMSIsImRrZS0xODAxIjoiNzgzOCIsImRraC0xODA1IjoiT0drYmxrSHgiLCJka2UtMTgwNSI6IjAiLCJka2UtMTgyMiI6Ijc5MjMiLCJka2UtMTgyOCI6Ijc5NTYiLCJka2UtMTgyOSI6Ijc5NjYiLCJka2gtMTgzMiI6ImFfdEFzODZmIiwiZGtlLTE4MzIiOiIwIiwiZGtlLTE4NDEiOiI4MDI1IiwiZGtlLTE4NDYiOiI4MDU3IiwiZGtlLTE4NTEiOiI4MDk3IiwiZGtlLTE4NTQiOiI4MTE4IiwiZGtlLTE4NTUiOiI4MTI0IiwiZGtlLTE4NTYiOiI4MTM2IiwiZGtoLTE4NTciOiJhVldzVTBDTCIsImRrZS0xODU3IjoiMCIsImRrZS0xODU4IjoiODE0NyIsImRrZS0xODYxIjoiODE1NyIsIm5iZiI6MTcxNTgxMTM1MCwiZXhwIjoxNzE1ODExNjUwLCJpYXQiOjE3MTU4MTEzNTAsImlzcyI6ImRrIn0.utRnOTct_EtMrK9XaONNHKid2Mvi00quSJjW3g1Gcig; STE="2024-05-15T22:49:28.5609071Z"; bm_sv=68E0046285E9E71439AE293B2C1238CB~YAAQwQLEF2a7xl2PAQAA9MtWfherly98vCA7pHU+sR2F1I0KkLu0QKwyWPgHr8pR9ffR1pfhnlIsCBAajQ+XjOrevDMSwPvqmNZZSzho0ABWb6IgtHS5wCKKgWE2u5/hxDvvow8Mwe32VstwA9GR4I0eB5chm083lZpwaFOnGRJvFt86UetjN66/LgDdeCI6av/TMS1MLLAGIZeW0XERe3Ct/6Z6Oj73run3Nt8JgdMarqpUvDpehfa36mvf1wDbj67aUSU=~1',
        "Dnt": "1",
        "Pragma": "no-cache",
        "Priority": "u=0, i",
        "Sec-Ch-Ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "Sec-Ch-Ua-Mobile": "?1",
        "Sec-Ch-Ua-Platform": "Android",
        # Sec-Fetch-Dest: "document",
        # Sec-Fetch-Mode: "navigate"
        # Sec-Fetch-Site: "none"
        # Sec-Fetch-User: "?1"
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36'
        }
    
    loader = SportsbookCutOdds(event_tag=event_tag, event_id=event_id)
    
    loader.headers = headers
    
    # player_odds_data = loader.get_player_odds_json(url=url)
    
    # players_odds = loader.get_event_odds_for_players(url)
    # player_odds_df = pd.DataFrame(players_odds)
    player_odds_df = loader.get_player_odds_df(url)
    
    if save_data:
        player_odds_df.to_csv(os.path.join(path, fname))
    