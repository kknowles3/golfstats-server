# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 09:08:20 2022

@author: kknow
"""

import pandas as pd
import numpy as np

from dev_util.download_util import UrlRequester
# from dev.util.pandas_util import expand_dict_column

# from components.loaders import pool
# from dev.espn.espn_golf_event import EspnGolfEvent
# from dev.util.data_util import RemoteDataServer
from dev.espn.pool_event import PoolEventScorer

from dev_util.gen_util import calc_function_time

class ScoreStatsLoader(UrlRequester):
    
    def __init__(self, event_id):
        
        self.event_id = event_id

        self.player_score_url_tag = "https://site.web.api.espn.com/apis/v2/scoreboard/header?sport=golf&league=pga&region=us&lang=en&contentorigin=espn&buyWindow=1m&showAirings=buy%2Clive%2Creplay&showZipLookup=true&tz=America%2FNew_York"
        self.player_score_stats_url_tag = "https://site.web.api.espn.com/apis/site/v2/sports/golf/pga/leaderboard/players?region=us&lang=en&event={}"
        self.hole_scole_url_tag = "https://site.web.api.espn.com/apis/site/v2/sports/golf/pga/leaderboard/course?region=us&lang=en&event={}"
        
        super().__init__()
        
        return None

    def get_hole_score_data(self):
        
        course_url = self.hole_scole_url_tag.format(self.event_id)
        
        hole_score_data = self.get_json_data(course_url)
        
        courses_data = hole_score_data.get('courses')
        course_data = courses_data[0]
        
        hole_score_data = course_data.get('holes')

        return hole_score_data
    
    def get_metric_info(self, hole_score_data=None):

        hole_score_data = self.get_hole_score_data() if hole_score_data is None else hole_score_data.copy()

        # Get the first hole statistics and get the metric info
        one_hole_stats = hole_score_data[0].get('holeStatistics').copy()
        # info_df = pd.DataFrame(one_hole_stats)
        
        metric_info = {}
        skip_keys = ['displayValue', 'value']
        # info_keys = [k for k in list(one_hole_stats[0].keys()) if k not in skip_keys]
        
        for d in one_hole_stats:
            info_d = {k:v for k,v in d.items() if k not in skip_keys}
            metric_info[d['name']] = info_d

        return metric_info

    def get_hole_metrics(self, hole_score_data=None):
        
        hole_score_data = self.get_hole_score_data() if hole_score_data is None else hole_score_data.copy()

        hole_metrics = {}
        for hole in hole_score_data.copy():
            # hole_stats = hole.pop()
            hole_stats = hole.get('holeStatistics')
            d = hole.copy()
            d.pop('holeStatistics')
            for hole_stat in hole_stats:
                d[hole_stat.get('name')] = hole_stat['value']
        
                # Add the total number of holes
                cols = ['eagles', 'birdies', 'pars', 'bogeys', 'dBogey', 'dBogeyPlus']
            d['numHoles'] = sum([int(d.get(col, 0)) for col in cols])
        
            hole_metrics[d.get('holeNumber')] = d
        
        return hole_metrics

    def get_hole_stats_df(self, hole_score_data=None):
        
        hole_score_data = self.get_hole_score_data() if hole_score_data is None else hole_score_data.copy()

        hole_metrics = self.get_hole_metrics(hole_score_data)
        
        hole_stats_df = pd.DataFrame(hole_metrics.values())
        
        hole_stats_df = hole_stats_df.sort_values(by='holeNumber').reset_index(drop=True)
        
        return hole_stats_df

    @calc_function_time        
    def get_hole_score_stats(self, hole_score_data=None):

        stats = {}
        
        hole_score_data = self.get_hole_score_data() if hole_score_data is None else hole_score_data.copy()
        
        # Get the descriptive info for each scoring metric
        metric_info = self.get_metric_info(hole_score_data)        
        stats['metric_info'] = metric_info
        
        # Get the scoring metrics for each hole
        hole_metrics = self.get_hole_metrics(hole_score_data)
        stats['metric_vals'] = hole_metrics
        
        return stats

    def get_player_score_data(self):
        
        player_score_url = self.player_score_url_tag.format(self.event_id)

        player_score_data = self.get_json_data(player_score_url)
        
        return player_score_data
        
    def get_player_score_stats_data(self):
        
        player_score_stats_url = self.player_score_stats_url_tag.format(self.event_id)

        player_score_stats_data = self.get_json_data(player_score_stats_url)
        
        return player_score_stats_data
    

# TODO Move to dev.espn or some other dev package
# TOOD Consider adding pool event object as part of initialization
class GolfScoreSimulator():
    '''
    Class for simulating golf scores based on the hole-by-hole scoring distribution 
    and the remaining holes for each player
    
    TODO Consider performance optimization to pre-generate discrete scoring 
    frequencies from a remaining set of holes. This way, we can pre-compute and 
    simulate a single remaining score variable.  We could also periodically 
    recalculate the scoring frequencies as the rounds progress, but we likely 
    don't need to do this during each calculation cycle.
    
    '''
    
    def __init__(self, score_stats_loader:ScoreStatsLoader, pool_event_scorer:PoolEventScorer=None):
        
        self.pool = pool_event_scorer
        self.score_stats_loader = score_stats_loader

        self.hole_score_stats = None
        self.hole_freq_dist = None
        
        self.scores = {
            'eagles': -2, 
             'birdies': -1, 
             'pars': 0, 
             'bogeys': 1, 
             'dBogey': 2, 
             'dBogeyPlus': 3
            }
        self.percentiles = [.1, .25, .5, .75, .9]

        # if hole_score_stats is not None:
        #     self.__initialize_dist_data__(hole_score_stats)
        
        return None
    
    def __update_dist_data__(self):

        hole_score_stats = self.score_stats_loader.get_hole_score_stats()
        self.hole_score_stats = hole_score_stats
        
        # Calculate frequency distributions by hole
        stats = hole_score_stats
        
        metric_vals = stats.get('metric_vals')
        
        score_dist = {}
        for hole, stats in metric_vals.items():
            # Calculate the probs and scores by hole
            num_holes = stats.get('numHoles')
            probs = [stats.get(k, 0)/num_holes for k in self.scores.keys()]
            scores = list(self.scores.values())
            score_dist[hole] = {
                'probs': probs,
                'scores': scores
                }

        self.hole_freq_dist = score_dist
        
        return None
    
    # def set_hole_score_stats(self, hole_score_stats):        
    #     self.__initialize_dist_data__(hole_score_stats)

    # TODO Enhance to handle time for today's rounds that haven't started yet
    def calc_prior_hole(self, player_score_df):
        
        df = player_score_df

        # Players who haven't started current round
        # df.loc[df['THRU'].str.contains(":"), 'THRU'] = 0
        df['THRU'] = df['THRU'].apply(lambda x: 0 if (":" in str(x)) else x)
        
        # Players who have finished current round
        # prior_hole = df['THRU'].replace({'F': 0}).astype(int)
        prior_hole = df['THRU'].replace({'F': 0})
        
        return prior_hole
    
    def add_prior_holes(self, player_score_df):
        
        player_score_df['priorHole'] = self.calc_prior_hole(player_score_df)
        
        return player_score_df
    
    # def add_hole_by_round(self, player_score_df):
        
    #     score_cols = ['R1', 'R2', 'R3', 'R4']

    #     found_current = False
    #     for col in score_cols:
    #         ...
    #     ...
        
    def calc_remaining_rounds_for_player(self, player_row):
        
        row = player_row
        
        round_cols = ['R1', 'R2', 'R3', 'R4']
        
        remaining_rounds = 4
        
        for col in round_cols:
            if row[col] == '--':
                break
            remaining_rounds += -1

        return remaining_rounds

    def add_remaining_rounds(self, player_score_df):
        
        player_score_df['numRounds'] = player_score_df.apply(lambda row : self.calc_remaining_rounds_for_player(row), axis = 1)
        
        return player_score_df            

    # def calc_remaining_holes(self, player_score_df):
        
    #     df = player_score_df
    #     df['CurrentHole'] = self.calc_current_hole(df)
        
    #     return df

    def calc_random_scores_for_player(self, player_row, num_trials=1000, thru_round=4):
        
        row = player_row

        current_score = int(row['ParScore'])
        
        prior_hole = row['priorHole']
        num_rounds = row['numRounds'] - (4 - thru_round) # Adjust for partial rounds
        
        hole_probs = self.hole_freq_dist
        
        next_hole = int(prior_hole) + 1
        player_samples = []
        for r in range(num_rounds):
            for hole in range(next_hole, 19):
                hole_dist = hole_probs.get(hole)
                
                # Draw a weighted sample
                samples = np.random.choice(hole_dist.get('scores'), num_trials, p=hole_dist.get('probs'))
                
                player_samples.append(samples)
                
            next_hole = 1

        # Aggregate the samples to compute the total scores for each trial
        if len(player_samples) > 0:
            player_tot_scores = np.array(player_samples).sum(axis=0)

        else:
            # return zeroes to streamline aggregations
            player_tot_scores = np.zeros(num_trials)

        player_tot_scores += current_score
            
        return player_tot_scores
        
    # https://compucademy.net/discrete-probability-distributions-with-python/
    @calc_function_time
    def calc_random_player_scores(self, player_score_df, num_trials=1000, thru_round=4, refresh_hole_stats=False):

        if refresh_hole_stats or (self.hole_freq_dist is None):
            self.__update_dist_data__()

        df = player_score_df
        
        # Testing
        # TODO Consider where this belongs
        # Filter for active players who made the cut
        df = df[player_score_df['MadeCut'] == True].reset_index(drop=True)
        
        # Add some enrichment columns
        df_cols = df.columns
        if 'priorHole' not in df_cols:
            df = self.add_prior_holes(df)
        if 'numRounds' not in df_cols:
            df = self.add_remaining_rounds(df)
        
        random_player_scores = {}
        for idx, row in df.iterrows():
            pid = row['PlayerId']
            scores = self.calc_random_scores_for_player(row, num_trials=num_trials, thru_round=thru_round)
            if scores is not None:
                random_player_scores[pid] = scores

        return random_player_scores
    
    def calc_random_scores_for_team(self):
        ...
        
    # TODO Add support for tiebreaker in rendom scoring
    @calc_function_time
    def calc_random_team_scores(self, random_player_scores, pool_id_df):
        
        tid_col = 'team_id'
        pid_cols = ['P1_ID', 'P2_ID', 'P3_ID', 'P4_ID']
        tb_col = 'TB_ID'
        
        # Loop through teams
        random_team_scores = {}
        for idx, row in pool_id_df.iterrows():
            
            tid = row[tid_col]
            tbid = row[tb_col]
            
            # Get the team's player scores
            team_player_scores = [random_player_scores.get(pid) for pid in row[pid_cols]]
            
            # Calculate the team's total scores
            if len(team_player_scores) > 0:
                team_tot_scores =  np.array(team_player_scores).sum(axis=0)
            
            # Get the tiebreaker scores
            tb_scores = random_player_scores.get(tbid)
        
            random_team_scores[tid] = {
                'team_scores': team_tot_scores,
                'tb_scores': tb_scores
            }

        return random_team_scores
    
    @calc_function_time
    def calc_team_summary_stats(self, random_team_scores, pool_id_df, num_places=5):
        
        tid_col = 'team_id'
        tname_col = 'TEAM NAME'
        
        tid_names = dict(zip(pool_id_df[tid_col], pool_id_df[tname_col]))
        
        
        tscore_data = {tid: d.get('team_scores') for tid,d in random_team_scores.items()}
        
        rand_tscore_df = pd.DataFrame(data=tscore_data)
        
        tbscore_data = {tid: d.get('tb_scores') for tid,d in random_team_scores.items()}

        rand_tbscore_df = pd.DataFrame(data=tbscore_data)
        
        # Calculate the net score by incorporating tiebreaker
        tscore_net_df = rand_tscore_df + (rand_tbscore_df / 100.)
        
        # Calculate score ranks by row (i.e., for each trial)
        tscore_ranks_df = tscore_net_df.rank(method='min', na_option='bottom', axis=1)
        
        # Calculate summary statistics        
        tscore_stats_df = tscore_ranks_df.describe(percentiles=self.percentiles).transpose()

        # # Calculate win probabilities (based on frequence among trials)
        # win_probs = (tscore_ranks_df == 1).sum(axis=0) / len(tscore_ranks_df)
        # tscore_stats_df['WinProb%'] = win_probs

        # Calculate the place probs:
        # places = [1,2,3,4,5]
        places = range(1, num_places + 1)
        for place in places:
            place_probs = (tscore_ranks_df == place).sum(axis=0) / len(tscore_ranks_df)
            tscore_stats_df['Place{}Pct'.format(place)] = place_probs
        
        # Calculate the money probs (i.e., prob of winning any money)
        place_probs = (tscore_ranks_df <= num_places).sum(axis=0) / len(tscore_ranks_df)
        tscore_stats_df['PlaceProbPct'] = place_probs
        
        # # ******** Note this needs to be adjusted for ties, where payout is split
        # # Calc unit payouts
        # payouts = [2150, 1150, 675, 425, 200]
        
        # payoffs = 1.0
        # for place, payoff in zip(places, payouts):
        #     payoffs += tscore_stats_df['Place{}%'.format(place)] * payoff

        # tscore_stats_df['ExpUnits'] = payoffs
        
        # Add the team name column
        tscore_stats_df['Team'] = tscore_stats_df.index.map(tid_names)
        # tscore_stats_df.insert(0, "Team", tscore_stats_df.index.map(tid_names))
        
        tscore_stats_df = tscore_stats_df.sort_values(by='PlaceProbPct', ascending=False)
        
        return tscore_stats_df
    
    # # TODO Under construction, needs a lot of cleanup
    # # Do a full/partial recalc
    # def recalc_team_score_stats(self, stats=None, num_trials=1000, num_places=7):
        
    #     pool = self.pool_event_scorer
    #     if pool is None:
    #         print("Unitialized Pool Event Scorer. Unable to calculate team stats")
    #         return None
        
    #     # Get the data sets
    #     if stats is not None:            
    #         hole_score_data = stats.get_hole_score_data()
    #         self.hole_score_stats = stats.get_hole_score_stats(hole_score_data)
        
    #     # Get the scoring data for the pool
    #     # Load Pool Scores
    #     pool.load_pool_scores()
    #     pool_score_df = pool.pool_score_df
    
    #     # Filter for made cut
    #     pool_score_df = pool_score_df[pool_score_df['MadeCut']].reset_index(drop=True)
    
    #     # Get the pool player score data
    #     pool_player_score_df = pool.pool_player_score_df
    
    #     # Filter for those who made cut
    #     pool_player_score_df = pool_player_score_df[~pool_player_score_df['THRU'].isin(['CUT', 'WD'])].reset_index(drop=True)
        
    #     # Calculate remaining holes
    #     pool_player_score_df = self.add_prior_holes(pool_player_score_df)
    #     pool_player_score_df = self.add_remaining_rounds(pool_player_score_df)
        
    #     # Calculate random trials for each player's score
    #     rand_player_scores = self.calc_random_player_scores(pool_player_score_df, num_trials=num_trials)
        
    #     # Calculate random scores for each team
    
    #     # Get the ids still in the pool
    #     team_made_cut_ids = pool_score_df['team_id']
    
    #     # Filter pool_id_df for teams who made cut
    #     pool_id_df = pool.pool_id_df
    #     pool_id_df = pool_id_df[pool_id_df['team_id'].isin(team_made_cut_ids)].copy()
    
    #     # Convert pool id columns to int
    #     pid_cols = ['P1_ID', 'P2_ID', 'P3_ID', 'P4_ID', 'TB_ID']
    #     pool_id_df[pid_cols] = pool_id_df[pid_cols].astype(int)
        
    #     rand_team_scores = self.calc_random_team_scores(rand_player_scores, pool_id_df)
        
    #     team_score_stats = self.calc_summary_stats(rand_team_scores, pool_id_df)
        
    #     return team_score_stats

    @calc_function_time
    def recalc_team_stats_df(self, num_trials, num_places):
        
        pool:PoolEventScorer = self.pool
        
        #######################################################
        # Get the input data we need for each calculation cycle
        #######################################################
        
        # Load most recent pool scores from remote data service
        pool.load_pool_scores()
        
        # Get the player scores for active pool teams who made the cut
        # pool_player_score_df = pool.load_pool_player_scores_df()
        pool_player_score_df = pool.pool_player_score_df
        
        # Recalc team scores
        # pool_score_df = pool.calc_pool_scores_df(player_scores_df=pool_player_score_df, exclude_cut_teams=True)
        pool_score_df = pool.pool_score_df
    
        # Get team ids that are still active in pool
        team_player_id_df = pool.get_team_player_id_df(pool_score_df=pool_score_df, exclude_cut_teams=True)
    
        # # Get the latest hole scoring stats
        # hole_score_stats = stats_loader.get_hole_score_stats()
    
        #########################
        # Generate Random Scores
        #########################
        
        rand_player_scores = self.calc_random_player_scores(pool_player_score_df, num_trials=num_trials, refresh_hole_stats=True)
    
        #####################################################
        # Generate random team scores and summary statistics
        #####################################################
        
        rand_team_scores = self.calc_random_team_scores(rand_player_scores, team_player_id_df)
        
        team_score_stats_df = self.calc_team_summary_stats(rand_team_scores, team_player_id_df, num_places=num_places)
    
        return team_score_stats_df

    def recalc_team_stats_data(self, num_trials, num_places, transform_df=True, orient='split'):
        
        df = self.recalc_team_stats_df(num_trials=num_trials, num_places=num_places)

        pool:PoolEventScorer = self.pool
        
        stats_data = {
            'last_update': pool.last_update,
            'status_tag': pool.status_tag,
            'num_trials': num_trials,
            'num_places': num_places
            }
        
        if transform_df:
            stats_data['orient'] = orient
            stats_data['data'] = df.to_dict(orient)
        else:
            stats_data['df'] = df        
            
        return stats_data
        
    @calc_function_time
    def add_final_score_stats(self, team_score_stats_df, start_pool_score_df, final_pool_score_df):
        
        # Add actual finish for events that have completed
        start_rank_d = dict(zip(start_pool_score_df['team_id'], start_pool_score_df['Rank']))
        team_score_stats_df['StartRank'] = team_score_stats_df.index.to_series().map(start_rank_d)

        # Actual finish from the initial pool score
        act_finish_d = dict(zip(final_pool_score_df.index.to_series(), final_pool_score_df['Rank']))
        team_score_stats_df['ActFinish'] = team_score_stats_df.index.to_series().map(act_finish_d)
        
        team_score_stats_df['FinishDiff'] = team_score_stats_df['StartRank'] - team_score_stats_df['ActFinish']
        team_score_stats_df['StdDevDiff'] = team_score_stats_df['FinishDiff'] / team_score_stats_df['std']

        return team_score_stats_df
        
# if __name__ == "__main__":

#     # Refresh golfer scores
#     # ege.refresh_scores()
#     event_config = {
#         'site_title': "The Open Championship Pool 2022",
#         'event_tag': "The Open Championship Pool 2022",
#         'event_id': '401353217',
#         'db_name': 'ukopen2022',
#         'logo_url': '/assets/img/2022_usopen_logo.jpg',
#         'score_url': "https://www.espn.com/golf/leaderboard/_/tournamentId/{}"
#         }

#     event_id = event_config.get('event_id')
    
#     stats = ScoreStats(event_id)
    
#     # Get the data sets
#     hole_score_data = stats.get_hole_score_data()
    
#     hole_score_stats = stats.get_hole_score_stats(hole_score_data)
    
#     # Get the course stats as a dataframe
#     hole_stats_df = stats.get_hole_stats_df(hole_score_data)
    
#     # Get the scoring data for the pool
#     # Load Pool Scores
#     pool.load_pool_scores()

#     pool_score_df = pool.pool_score_df

#     # Filter for made cut
#     pool_score_df = pool_score_df[pool_score_df['MadeCut']].reset_index(drop=True)

#     # Get the pool player score data
#     pool_player_score_df = pool.pool_player_score_df

#     # Filter for those who made cut
#     pool_player_score_df = pool_player_score_df[~pool_player_score_df['THRU'].isin(['CUT', 'WD'])].reset_index(drop=True)
    
#     # Calculate remaining holes
#     gss = GolfScoreSimulator(hole_score_stats)
#     pool_player_score_df = gss.add_prior_holes(pool_player_score_df)
#     pool_player_score_df = gss.add_remaining_rounds(pool_player_score_df)
    
#     # Calculate random trials for each player's score
#     rand_player_scores = gss.calc_random_player_scores(pool_player_score_df)
    
#     # Calculate random scores for each team

#     # Get the ids still in the pool
#     team_made_cut_ids = pool_score_df['team_id']

#     # Filter pool_id_df for teams who made cut
#     pool_id_df = pool.pool_id_df
#     pool_id_df = pool_id_df[pool_id_df['team_id'].isin(team_made_cut_ids)].copy()

#     # Convert pool id columns to int
#     pid_cols = ['P1_ID', 'P2_ID', 'P3_ID', 'P4_ID', 'TB_ID']
#     pool_id_df[pid_cols] = pool_id_df[pid_cols].astype(int)
    
#     rand_team_scores = gss.calc_random_team_scores(rand_player_scores, pool_id_df)
    
#     team_score_stats = gss.calc_summary_stats(rand_team_scores, pool_id_df)
        