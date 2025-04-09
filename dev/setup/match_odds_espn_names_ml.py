# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 12:52:04 2024

@author: kknow
"""

import os
import pandas as pd

from dev_util.pandas_util import save_df_to_csv, load_csv_as_df

def load_espn_field():
    
    fname = os.path.join(event_path, espn_fname)
    espn_df = pd.read_csv(fname, index_col=False, skiprows=espn_skip_rows)

    return espn_df

def load_odds():
    
    fname = os.path.join(event_path, odds_fname)
    odds_df = pd.read_csv(fname, index_col=0, skiprows=espn_skip_rows)

    odds_df.index.name = 'Player'
    
    odds_df = odds_df.reset_index()
    
    return odds_df

def trim_names(df):
    
    df_obj = df.select_dtypes(['object'])
    
    df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())
    
    return df

def check_matching_names(check_players, ref_players):
    
    # # Get distinct list of pool players
    # odds_players = odds_df['Player']
        
    # Check for matching names
    # player_id_map = dict(zip(espn_df['Player'], espn_df['ID']))
    # odds_player_ids = odds_players.map(player_id_map)
    # check_df = pd.DataFrame(data={'odds_player':odds_players, 'espn_id': odds_player_ids})
    
    # error_names = check_df[check_df['espn_id'].isnull()]['odds_player']
    
    # error_names = [player for player in check_players if player not in ref_players]
    error_names = [player for player in list(check_players) if player not in list(ref_players)]
    
    return error_names

def find_closest_matching_names(error_names, ref_names, num_matches=2, as_df=True):
    
    # https://pypi.org/project/fuzzywuzzy/
    from thefuzz import process

    # espn_players = espn_df['Player'].values
    
    error_matches = {}
    
    for error_name in error_names:
        matches = process.extract(error_name, ref_names, limit=num_matches)
        error_matches[error_name] = matches
        
    if as_df:
        
        df_rows = []
        for name, matches in error_matches.items():
            
            row = {
                'name': name,
                'bestMatch': matches[0][0],
                'bestScore': matches[0][1]
                }
            
            i = 1
            for match_item in matches[1:]:
                row.update({
                    'nextMatch{}'.format(i): match_item[0],
                    'nextScore{}'.format(i): match_item[1]                    
                    })
            df_rows.append(row)
            
        df = pd.DataFrame(df_rows)
        
        df = df.sort_values(by=['bestScore', 'name'], ascending=False, ignore_index=True)
        
        return df
        
    return error_matches

def apply_name_mods(mod_df, matches_df, src_col='Player', dest_col='EspnPlayer'):
    
    name_mods = dict(zip(matches_df['name'], matches_df['bestMatch']))

    mod_df.insert(1, dest_col, mod_df[src_col].values)
    mod_df[dest_col] = mod_df[dest_col].replace(name_mods)
    
    return mod_df

def save_and_reload_df(df, fname, path=""):

    # save df locally
    save_df_to_csv(
        df=df,
        path=path,
        fname=fname)

    # Reload saved df
    df2 = load_csv_as_df(path=path, fname=fname)
    
    # Check if saved and reload match
    if df.equals(df2):
        print("Saved data matches reloaded data")
    else:
        print("Saved and reloaded data have differences, possibly different data types")
    
    return df2

if __name__ == "__main__":
    
    from dev.util.app_util import APP_PATH
    
    event_year = 2025
    event_tag = "masters"
    
    event_path = os.path.join(APP_PATH, 'data/{}/{}'.format(event_year, event_tag))
    
    espn_fname = 'espn_field.csv'
    odds_fname = 'sportsbook_cut_odds.csv'
    name_corrections_fname = 'odds_name_corrections.csv'
    
    mod_odds_fname = 'sportsbook_cut_odds_mod.csv'
    
    espn_skip_rows = 0 # Number of import rows to skip

    save_data = True
    
    espn_df = load_espn_field()
    espn_df = trim_names(espn_df)
    
    odds_df = load_odds()
    odds_df = trim_names(odds_df)   
    
    # Check for errors and name mismatches
    error_names = check_matching_names(odds_df['Player'], espn_df['Player'])
    if len(error_names) > 0:
        print("There are {} names with matching errors".format(len(error_names)))
        print("\n".join(error_names))    
        
    # Find closest player name matches in ESPN list
    matches_df = find_closest_matching_names(
        error_names, 
        espn_df['Player'], 
        num_matches=2)

    print(matches_df[['name', 'bestMatch', 'bestScore']])
    
    # Check for user confirmation to save best matches
    choice = input('Apply best match name corrections? Press Y or y to confirm: ')
    if choice.upper() == 'Y':

        # Apply name corrections
        print("Applying {} name corrections".format(len(matches_df)))
        mod_odds_df = apply_name_mods(
            mod_df=odds_df, 
            matches_df=matches_df)

        # Re-check for mismatches
        error_names = check_matching_names(odds_df['EspnPlayer'], espn_df['Player'])
        if len(error_names) > 0:
            print("There are {} names with matching errors".format(len(error_names)))
            print("\n".join(error_names))
    
        else:    
            print('No name matching errors found after modifications')

    if save_data:
        
        # Check for user confirmation to save best matches
        choice = input('Save best match name corrections? Press Y or y to confirm: ')
        if choice.upper() == 'Y':

            print("Saving {} name corrections locally".format(len(matches_df)))

            # Save locally
            # save_df_to_csv(
            #     df=matches_df,
            #     path=event_path,
            #     fname=name_corrections_fname)
            matches_df2 = save_and_reload_df(
                df=matches_df, 
                fname=name_corrections_fname,
                path=event_path)

            print('Saving odds for {} players'.format(len(mod_odds_df)))
            
            # Save locally
            # save_df_to_csv(
            #     df=mod_odds_df,
            #     path=event_path,
            #     fname=mod_odds_fname)
            mod_odds_df2 = save_and_reload_df(
                df=mod_odds_df, 
                fname=mod_odds_fname,
                path=event_path)
            
            # # Check if saved and reload match
            # if df.equals(df1):
            #     print("Saved data matches reloaded data")
            # else:
            #     print("Saved and reloaded data have differences, possibly different data types")
            
            # Apply name corrections
            
            # with open(os.path.join(path, fname), 'wb') as output_file:
            #     pickle.dump(obj, output_file, pickle.HIGHEST_PROTOCOL)   
        else:
            print('Save cancelled by user')
            # return False
