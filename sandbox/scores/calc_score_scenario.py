# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 18:36:38 2023

@author: kknow
"""

import pandas as pd

from dev_util.gen_util import calc_function_time
from sandbox.scores.calc_score_distribution import ScoreStatsLoader

from dev.espn.pool_event import PoolEventScorer
from dev_util.mongo_util import MongoDataServer
from dev_util.data_util import get_nested_item

from components.app_data import EVENT_CONFIGS

import numpy as np

def load_all_player_scores(rds):
    
    cname = 'player_score'
    
    player_score_sets = rds.load_remote_data_items(collection=cname)
    
    return player_score_sets

# def get_espn_player_ids(player_score_data):
#     '''
#     Gets a dictionary of ESPN player names and ids

#     Parameters
#     ----------
#     player_score_data : TYPE
#         DESCRIPTION.

#     Returns
#     -------
#     d : TYPE
#         DESCRIPTION.

#     '''
    
#     d = {di.get('displayName'):di.get('id') for di in player_score_data.get('leaderboard')}
    
#     return d

# For testing a consolidated class for prior score scenarios
class PriorPoolScoreScenario():
        
    def __init__(self, pool_score_df, pool_player_score_df):
        
        self.pool_score_df = pool_score_df
        self.pool_player_score_df = pool_player_score_df
        
        self.player_scorecards = None
        self.player_round_info_df = None
        
        
        ...



# Pro forma rollback class that resets player scores back to a prior point in time.
# This is useful for re-running scoring simulations from prior tournaments.
# Review methods to see which belong on the ScoreResetter vs. the base ScoreStats class.
# TODO Consider whether to have a PriorScoreScenario result class that gets generated
# with access to information that is needed for the simulation. PriorScoreScenario
# could be derived from a ScoreScenario base class to standardize what gets used with
# active scoring scenarios during a live pool.
class ScoreResetter(ScoreStatsLoader):

    def __init__(self, event_id):
        
        # player_scorecard_url_base = "https://site.web.api.espn.com/apis/site/v2/sports/golf/pga/leaderboard/401465533/competitorsummary/11119?region=us&lang=en&season=2023"
        self.player_scorecard_url_base = "https://site.web.api.espn.com/apis/site/v2/sports/golf/pga/leaderboard/{}/competitorsummary/{}?region=us&lang=en&season=2023"
        self.espn_player_ids = None # Lazy load
        self.espn_id_players = None # Lazy load
        self.max_workers = 20 # For parallel requests
        
        super().__init__(event_id)

    # TODO Consider whether to move some of these methods to EspnGolfEvent
    def get_espn_player_ids(self, player_score_data=None):
        '''
        Gets a dictionary of ESPN player names and ids
    
        Parameters
        ----------
        player_score_data : TYPE
            DESCRIPTION.
    
        Returns
        -------
        d : TYPE
            DESCRIPTION.
    
        '''
        
        d = self.espn_player_ids
        
        if d is None:
            
            if player_score_data is None:
                player_score_data = self.get_player_score_data()
                
            d = {di.get('displayName'):di.get('id') for di in player_score_data.get('leaderboard')}
        
        return d
    
    def get_espn_id_players(self, player_score_data=None):
        '''
        Gets a dictionary of ESPN player ids and names

        Parameters
        ----------
        player_score_data : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        d : TYPE
            DESCRIPTION.

        '''
        
        d = self.espn_id_players
        
        if d is None:
            
            espn_player_ids = self.get_espn_player_ids(player_score_data=player_score_data)
            
            d = {v:k for k,v in espn_player_ids.items()}
            
        return d

    def get_scorecard_by_id(self, espn_player_id):
        '''
        Gets tournament scorecard data, including hole by hole data by round for
        a particular player's ESPN id

        Parameters
        ----------
        espn_player_id : TYPE
            DESCRIPTION.

        Returns
        -------
        jdata : TYPE
            DESCRIPTION.

        '''
        
        event_id = self.event_id
        
        url = self.player_scorecard_url_base.format(event_id, espn_player_id)
        
        jdata = self.get_json_data(url)
        
        return jdata

    def get_scorecard(self, espn_player_name):
        '''
        Gets tournament scorecard data, including hole by hole data by round for
        a particular player's ESPN name

        Parameters
        ----------
        espn_player_name : TYPE
            DESCRIPTION.

        Returns
        -------
        scorecard : TYPE
            DESCRIPTION.

        '''

        espn_player_ids = self.get_espn_player_ids()
        
        espn_player_id = espn_player_ids.get(espn_player_name)
        if espn_player_id is None:
            print("Unable to get id for player: {}".format(espn_player_name))
            return None
        
        scorecard = self.get_scorecard_by_id(espn_player_id)
        
        return scorecard

    @calc_function_time            
    def get_player_scorecards(self, espn_player_names, multi_request=True, max_workers=None):
        '''
        Retrieve a list of scorecards based on an input list of ESPN player names.
        Each player scorecard is retrieved in a single request. This method has the
        option of executing the scorecard retrieval requests in parallel to reduce
        overall retrieval time.

        Parameters
        ----------
        espn_player_names : TYPE
            DESCRIPTION.
        multi_request : TYPE, optional
            DESCRIPTION. The default is True.
        max_workers : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        player_scorecards : TYPE
            DESCRIPTION.

        '''

        # TODO Consolidate multi and single request utility methods, or set workers
        # to 1 for serial requests.
        if multi_request:
            
            event_id = self.event_id
            
            espn_player_ids = self.get_espn_player_ids()
            
            max_workers = min(len(espn_player_names), self.max_workers)
            
            # Create a list of requests to execute in parallel
            req_configs = []
            for player_name in espn_player_names:
                player_id = espn_player_ids.get(player_name)
                
                if player_id is None:
                    print("Unable to get id for player: {}".format(player_name))
                    continue
                
                url = self.player_scorecard_url_base.format(event_id, player_id)
                
                req_configs.append({'req_type': 'get', 'url': url})
            
            # Execute multi-request
            # TODO Extract max_workers parameters to class property
            scorecard_resps = self.send_request_configs(
                request_configs=req_configs, 
                max_workers=max_workers
                )
            
            # TODO Add validation and error handling in case there are errors or
            # unexpected response codes and format
            # Convert to JSON
            scorecards_jdata = [r.json() for r in scorecard_resps]
            player_scorecards = {get_nested_item(d, ['competitor', 'id']):d for d in scorecards_jdata}
            
        else:
            
            player_scorecards = {player: self.get_scorecard(espn_player_name=player) for player in espn_player_names}

        return player_scorecards        
    
    def get_player_round_info(self, scorecard, round_num):
        '''
        Retrieve scorecard details for a single round.

        Parameters
        ----------
        scorecard : TYPE
            DESCRIPTION.
        round_num : TYPE
            DESCRIPTION.

        Returns
        -------
        round_info : TYPE
            DESCRIPTION.

        '''
        
        player_id = get_nested_item(scorecard, ['competitor','id'])
        rounds = scorecard.get('rounds')
        
        round_info = {'espnId':player_id}
        round_info.update(rounds[round_num-1])
        
        return round_info
    
    def get_players_round_info(self, player_scorecards, round_num):
        '''
        Retrieves a set of scorecard details for a single round.

        Parameters
        ----------
        player_scorecards : TYPE
            DESCRIPTION.
        round_num : TYPE
            DESCRIPTION.

        Returns
        -------
        players_round_info : TYPE
            DESCRIPTION.

        '''
        
        players_round_info = {player:self.get_player_round_info(scorecard=scorecard, round_num=round_num) for player, scorecard in player_scorecards.items()}
        
        return players_round_info
    
    # Multi-player
    def get_players_round_info_df(self, player_scorecards, round_num, pop_cols=['linescores', 'statistics']):
        '''
        Retrieves a set of scorecard details for a single round and converts results
        to a dataframe. The resulting table is sorted by starting position and 
        tee time for the round.

        Parameters
        ----------
        player_scorecards : TYPE
            DESCRIPTION.
        round_num : TYPE
            DESCRIPTION.
        pop_cols : TYPE, optional
            DESCRIPTION. The default is ['linescores', 'statistics'].

        Returns
        -------
        round_info_df : TYPE
            DESCRIPTION.

        '''
        
        players_round_info = self.get_players_round_info(player_scorecards=player_scorecards, round_num=round_num)

        if pop_cols is not None:
            for round_info in players_round_info.values():
                for col in pop_cols:
                    round_info.pop(col)
        
        round_info_df = pd.DataFrame(players_round_info.values())
        
        # Sort by startPosition and tee time
        sort_cols = ['startPosition', 'teeTime']
        round_info_df = round_info_df.sort_values(by=sort_cols).reset_index(drop=True)
        
        return round_info_df
    

# *****************************************************************************
# Testing score scenario creator
# *****************************************************************************

    # Get player hole scores for round
    def get_hole_scores_for_round(self, espn_player_id, player_round_info, as_df = True):
        
        # round_info = players_round_info.get(espn_player_id)
        hole_scores = player_round_info.get('linescores')
        
        if as_df:
            df = pd.DataFrame(hole_scores)
            return df
        
        return hole_scores

    @calc_function_time
    def add_last_completed_hole(self, players_round_info_df, final_grp_prior_hole, round_num, hole_stats_df):
        '''
        Adds a lastCompletedHole column to players_round_info_df. This implementation
        makes some simplifying assumptions and assigns the remaining holes based
        on the assumption that the active pool players are the only active players
        in the tournament. Note that this is only used in simulating prior periods.
        Live scoring inputs will reflect actual remaining holes for each player.
        
        TODO Enhance this based on actual starting positions of the field on the day.

        Parameters
        ----------
        players_round_info_df : TYPE
            DESCRIPTION.
        final_grp_prior_hole : TYPE
            Last completed hole for the final group to start the round.
        round_num : TYPE
            DESCRIPTION.
        hole_stats_df : TYPE
            DESCRIPTION.

        Returns
        -------
        players_round_info_df : TYPE
            DESCRIPTION.

        '''
    
        players_per_hole = {3: 2, 4: 4, 5:4}
        
        num_players = len(players_round_info_df)
    
        remaining_holes_df = hole_stats_df[hole_stats_df['holeNumber'] > final_grp_prior_hole]
        # display(remaining_holes_df)
    
        hole_par = dict(zip(remaining_holes_df['holeNumber'], remaining_holes_df['holePar']))
        # print(hole_par)
    
        last_completed_holes = []
        for i in range(final_grp_prior_hole, 18):
        
            next_hole_par = hole_par.get(i+1)
            last_completed_holes += [i] * players_per_hole.get(next_hole_par)
    
        if len(last_completed_holes) < num_players:
            last_completed_holes += [18] * (num_players - len(last_completed_holes))
        else:
            last_completed_holes = last_completed_holes[:num_players]
        
        # print(last_completed_holes)
        # print(len(last_completed_holes))
    
        # Add last completed hole data
        players_round_info_df['lastCompletedHole'] = last_completed_holes
        # players_round_info_df['remainingRounds'] = 5 - round_num

        # Insert player name
        players_round_info_df.insert(loc=0, column='playerName', value=players_round_info_df['espnId'].map(self.get_espn_id_players()))
    
        return players_round_info_df
    
    # # TODO Change this to use player's scorecard
    # # Calculate the player's actual score on the remaining holes
    # # @calc_function_time
    # def calc_remaining_player_score(self, espn_player_id, last_completed_hole, player_round_info, hole_stats_df):
        
    #     hole_scores_df = self.get_hole_scores_for_round(espn_player_id=espn_player_id, player_round_info=player_round_info)
        
    #     remaining_player_score = hole_scores_df[hole_scores_df['period'] > last_completed_hole]['value'].sum()
        
    # #     remaining_net_score = remaining_player_score - remaining_par_score
        
    #     return remaining_player_score
    
    # # Calculate the player's net score relative to par on the remaining holes
    # def calc_remaining_net_score(self, espn_player_id, last_completed_hole, players_round_info, players_round_info_df, hole_stats_df):
        
    #     remaining_par_score = hole_stats_df[hole_stats_df['holeNumber'] > last_completed_hole]['holePar'].sum()
        
    #     remaining_player_score = calc_remaining_player_score(espn_player_id, last_completed_hole, players_round_info, players_round_info_df, hole_stats_df)
        
    #     remaining_net_score = remaining_player_score - remaining_par_score
        
    #     return remaining_net_score
    
    # Calculate the player's par and net scores on the remaining holes
    # @calc_function_time
    def calc_remaining_player_scores(self, espn_player_id, last_completed_hole, player_round_info, hole_stats_df):
        
        remaining_par_score = hole_stats_df[hole_stats_df['holeNumber'] > last_completed_hole]['holePar'].sum()
        
        # remaining_player_score = self.calc_remaining_player_score(espn_player_id, last_completed_hole, player_round_info.get(espn_player_id), hole_stats_df)
        hole_scores_df = self.get_hole_scores_for_round(espn_player_id=espn_player_id, player_round_info=player_round_info)
        
        remaining_player_score = hole_scores_df[hole_scores_df['period'] > last_completed_hole]['value'].sum()
        
        remaining_net_score = remaining_player_score - remaining_par_score
        
        return remaining_player_score, remaining_net_score
    
    # @calc_function_time
    def add_remaining_player_scores(self, players_round_info_df, players_round_info, hole_stats_df):
        
        # Add remaining par scores
        players_round_info_df[['remainingScore','remainingNetScore']] = players_round_info_df.apply(lambda row: self.calc_remaining_player_scores(row['espnId'], row['lastCompletedHole'], players_round_info.get(row['espnId']), hole_stats_df), axis='columns', result_type='expand')
        
        return players_round_info_df
    
    # @calc_function_time
    def reset_remaining_round_scores(self, pool_player_score_df, round_num):
        
        # Clear active and future rounds
        df = pool_player_score_df

        # TODO Refactor - not recommended due to slow performance
        # Note: performance is fine for a small number of rows (e.g., < 100)
        for idx, row in df.iterrows():
            if row['MadeCut']:

                if row['R{}'.format(round_num)] == '--':
                    continue
                
                thru = int(row['THRU'])
                
                if thru < 18:
                    # row['R{}'.format(round_num)] = "--"
                    df.at[idx,'R{}'.format(round_num)] = "--"
                
                nxt_round_num = round_num + 1
                while nxt_round_num <= 4:
                    # row['R{}'.format(nxt_round_num)] = "--"
                    df.at[idx,'R{}'.format(nxt_round_num)] = "--"
                    nxt_round_num += 1

        # Not working alternative to iterrows
        # # Current round
        # round_col = 'R{}'.format(round_num)
        # conditions = [df['MadeCut'] == True, df['THRU'] < 18]
        # df[round_col] = np.where(((df['MadeCut'] == True) and (df['THRU'] < 18)), "--", df[round_col])

        # # Subsequent rounds
        # nxt_round_num = round_num + 1
        # nxt_round_col = 'R{}'.format(nxt_round_num)
        # while nxt_round_num <= 4:
        #     df[nxt_round_col] = np.where(df['MadeCut'] and (df['THRU'] < 18), "--", df[nxt_round_col])
        #     nxt_round_num += 1

        return df
    
    @calc_function_time
    def apply_scoring_adjustments(self, pool_player_score_df, round_num, players_round_info_df):
        '''
        Applies scoring adjustments to reset pool player scores to an earlier point in time.

        Parameters
        ----------
        pool_player_score_df : TYPE
            DESCRIPTION.
        players_round_info_df : TYPE
            DESCRIPTION.

        Returns
        -------
        pool_player_score_df : TYPE
            DESCRIPTION.

        '''

        # Create dictionaries for mapping score columns        
        player_thru_d = dict(zip(players_round_info_df['playerName'], players_round_info_df['lastCompletedHole']))
        player_adj_d = dict(zip(players_round_info_df['playerName'], players_round_info_df['remainingScore']))
        player_net_d = dict(zip(players_round_info_df['playerName'], players_round_info_df['remainingNetScore']))
        # player_rounds_left_d = dict(zip(players_round_info_df['playerName'], players_round_info_df['remainingRounds']))
        
        # Add columns
        na_val = "--"
        pool_player_score_df['THRU'] = pool_player_score_df['PLAYER'].map(player_thru_d).fillna(na_val)
        pool_player_score_df['ScoreAdj'] = pool_player_score_df['PLAYER'].map(player_adj_d).fillna(na_val)
        pool_player_score_df['ParAdj'] = pool_player_score_df['PLAYER'].map(player_net_d).fillna(na_val)
        # pool_player_score_df['RoundsLeft'] = pool_player_score_df['PLAYER'].map(player_rounds_left_d).fillna(na_val)
        
        # TODO Add error handling for various conditions (e.g., WD, "--" values)
        # Apply scoring adjustment
        # pool_player_score_df['R{}'.format(round_num)] = np.where(pool_player_score_df['R{}'.format(round_num)] == "--", "--", (pool_player_score_df['R{}'.format(round_num)].astype(int, errors='ignore') - pool_player_score_df['ScoreAdj']).astype(int, errors='ignore'))
        # pool_player_score_df['TOT'] = (pool_player_score_df['TOT'].astype(int) - pool_player_score_df['ScoreAdj'].map({"--":"0"})).astype(int, errors='ignore')
        # pool_player_score_df['ParScore'] = (pool_player_score_df['ParScore'].astype(int, errors='ignore') - pool_player_score_df['ParAdj']).astype(int)
        # pool_player_score_df['ParScore'] = np.where(pool_player_score_df['ParScore'] == "--", "--", (pool_player_score_df['ParScore'].astype(int, errors='ignore') - pool_player_score_df['ParAdj']).astype(int, errors='ignore'))

        round_col = 'R{}'.format(round_num)
        pool_player_score_df[round_col] = pool_player_score_df.apply(lambda row: na_val if row[round_col] == na_val else int(row[round_col]) - int(row['ScoreAdj']), axis=1)
        pool_player_score_df['TOT'] = pool_player_score_df.apply(lambda row: row['TOT'] if row['ScoreAdj'] == na_val else int(row['TOT']) - int(row['ScoreAdj']), axis=1)
        pool_player_score_df['ParScore'] = pool_player_score_df.apply(lambda row: row['ParScore'] if row['ParAdj'] == na_val else int(row['ParScore']) - int(row['ParAdj']), axis=1)

        # Clear active and future rounds
        pool_player_score_df = self.reset_remaining_round_scores(pool_player_score_df, round_num)
        
        return pool_player_score_df

    # TODO Consider a get_score_scenario method for ScoreStats
    # Worker method for creating the prior score scenario
    @calc_function_time
    def create_prior_score_scenario(self, round_num, final_grp_prior_hole, pool_player_score_df, player_scorecards=None, hole_stats_df=None, filter_cuts=True):
        '''
        Catch-all method to create a prior scoring scenario for the pool_player_score_df.
        For now, this has only been tested on round 4.
        
        # TODO Test for earlier rounds.

        Parameters
        ----------
        round_num : TYPE
            DESCRIPTION.
        final_grp_prior_hole : TYPE
            Last completed hole for the final group to start the round.
        pool_player_score_df : TYPE
            DESCRIPTION.
        player_scorecards : TYPE, optional
            DESCRIPTION. The default is None.
        hole_stats_df : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        pool_player_score_df : TYPE
            DESCRIPTION.

        '''
        
        # Filter for those who made cut
        if filter_cuts:
            pool_player_score_df = pool_player_score_df[pool_player_score_df['MadeCut'] == True].reset_index(drop=True)

        # Get active pool players
        active_pool_players = pool_player_score_df[pool_player_score_df['MadeCut'] == True]['PLAYER'].reset_index(drop=True)
        print("There are {} active pool players.".format(len(active_pool_players)))
        
        # Get player scorecards (Seperate request per player)
        if player_scorecards is None:
            max_workers = 20
            player_scorecards = self.get_player_scorecards(espn_player_names=active_pool_players, multi_request=True, max_workers=max_workers)
            print("Got scorecards for {} players.".format(len(player_scorecards)))

        # Player_round_info
        players_round_info = self.get_players_round_info(player_scorecards=player_scorecards, round_num=round_num)
        players_round_info_df = self.get_players_round_info_df(player_scorecards=player_scorecards, round_num=round_num)        

        # Get scoring statistics for each hole
        if hole_stats_df is None:
            hole_stats_df = self.get_hole_stats_df()
        
        # Add last completed hole scenario
        players_round_info_df = self.add_last_completed_hole(
            players_round_info_df=players_round_info_df, 
            final_grp_prior_hole=final_grp_prior_hole,
            round_num=round_num,
            hole_stats_df=hole_stats_df
        )
        
        # Add remaining par scores
        # players_round_info_df[['remainingScore','remainingNetScore']] = players_round_info_df.apply(lambda row: self.calc_remaining_scores(row['espnId'], row['lastCompletedHole'], players_round_info, players_round_info_df, hole_stats_df), axis='columns', result_type='expand')
        players_round_info_df = self.add_remaining_player_scores(
            players_round_info_df=players_round_info_df,
            players_round_info=players_round_info,
            hole_stats_df=hole_stats_df
            )
        
        # Apply scoring adjustment to pool player scores
        pool_player_score_df = self.apply_scoring_adjustments(pool_player_score_df, round_num, players_round_info_df)

        return pool_player_score_df
        
if __name__ == '__main__':
    
    # Url base for the json data
    # course_stats_url_base = 'https://site.web.api.espn.com/apis/site/v2/sports/golf/pga/leaderboard/course?region=us&lang=en&event={}'
    # player_scorecard_url_base = "https://site.web.api.espn.com/apis/site/v2/sports/golf/pga/leaderboard/401465533/competitorsummary/11119?region=us&lang=en&season=2023"

    multi_request = True
    
    event_tag = 'usopen2023'
    event_config = EVENT_CONFIGS.get(event_tag)
    # ref_datestr = dtbase_str = "06/18/23 09:00:00 PM EDT"

    # event_id = 401465533
    event_id = event_config['event_id']
    db_name = event_config['db_name']

    stats = ScoreResetter(event_id)
    
    # player_score_data = stats.get_player_score_data()

    # # Get ESPN Player IDs
    # espn_player_ids = stats.get_espn_player_ids(player_score_data)
    
    mds = MongoDataServer(db_name=db_name)

    # pool = PoolEventScorer(rds, ref_datestr=ref_datestr)
    pool = PoolEventScorer(mds)

    # Get the player scores for the pool
    pool.load_pool_scores()
    pool_player_score_df = pool.pool_player_score_df

    # # Loader all player score sets
    # player_score_sets = load_all_player_scores(rds)
    
    # Get player scorecards for pool players who made cut
    active_pool_players = pool_player_score_df[pool_player_score_df['MadeCut'] == True]['PLAYER'].reset_index(drop=True)
    
    # Execute requests using different woker sizes for testing
    # max_workers_sets = [5, 10, 15, 20, 25, 50]
    max_workers_sets = [20]
    
    for max_workers in max_workers_sets:
        max_workers = min(len(active_pool_players), max_workers)
        print('Getting player scorecards in parallel using {} workers'.format(max_workers))
        player_scorecards = stats.get_player_scorecards(espn_player_names=active_pool_players, multi_request=True, max_workers=max_workers)

    # Get the fourth round info for the players
    round_num = 4
    # players_round_info_dfs = [stats.get_player_round_info_df(player_scorecard=scorecard, round_num=round_num) for scorecard in player_scorecards]
    # players_round_info_df = pd.concat(players_round_info_dfs)
    players_round_info = stats.get_players_round_info(player_scorecards=player_scorecards, round_num=round_num)
    players_round_info_df = stats.get_players_round_info_df(player_scorecards=player_scorecards, round_num=round_num)
    
    # players_round_info_df.insert()
        
    # Figure out tee position at start of round
    # I think we can derive this from start position and tee time
    # Start position tells us the score at the start of round, tee time can be used to sort the tie scores
    # This is just for a simulation and doesn't need to be perfect. During a live
    # pool event, we'll have the actual holes left for each player.
    
    # # Sort by startPosition and tee time
    # sort_cols = ['startPosition', 'teeTime']
    # players_round_info_df = players_round_info_df.sort_values(by=sort_cols).reset_index(drop=True)

    #######################
    # Add scoring scenario
    #######################
    
    round_num = 4
    leader_prior_hole = 9

    scen_pool_player_score_df = stats.create_prior_score_scenario(
        round_num=round_num, 
        final_grp_prior_hole=leader_prior_hole, 
        pool_player_score_df=pool_player_score_df,
        player_scorecards=player_scorecards
        )
    
    ###########################
    # Recalculate pool scores
    ###########################
    
    pool_scores_df = pool.calc_pool_scores_df(player_scores_df=scen_pool_player_score_df)
    