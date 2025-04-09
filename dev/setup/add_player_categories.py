# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 17:43:49 2024

@author: kknow

Script to match pool category names to ESPN names for A,B type lists

"""

import os
import pandas as pd

from dev_util.pandas_util import save_df_to_csv, load_csv_as_df

def trim_names(df):
    
    df_obj = df.select_dtypes(['object'])
    
    df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())
    
    return df

def get_player_cats(cat_players, as_df=True):
    
    player_cats = []
    
    for cat, players_str in cat_players.items():
        
        # Convert players_str to a list of players
        player_lst = players_str.split(",")
        for player in player_lst:
            d = dict(
                Player = player.strip(),
                Category = cat                
                )
            player_cats.append(d)
        
    if as_df:
        df = pd.DataFrame(player_cats)
        return df
        
    return player_cats

def check_matching_names(check_players, ref_players):
    
    error_names = [player for player in list(check_players) if player not in list(ref_players)]
    
    return error_names

def find_closest_matching_names(
        error_names, 
        ref_names, 
        num_matches=2, 
        as_df=True):
    
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
    
    event_year = 2025
    event_tag = "masters"

    event_path = 'data/{}/{}'.format(event_year, event_tag)

    espn_fname = 'espn_field.csv'

    # From OMO email
    cat_players = {
        "A+": "Scottie Scheffler, Rory McIlroy",
        "A":  "Collin Morikawa, Brooks Koepka, Jon Rahm, Viktor Hovland",
        "B":  "Patrick Cantlay, Xander Schauffele, Ludvig Aberg, Justin Thomas, Bryson DeChambeau, Shane Lowry"
        }
    
    # Get a df of players and categories
    player_cat_df = get_player_cats(cat_players,as_df=True)
    
    espn_df = load_csv_as_df(
        path=event_path,
        fname=espn_fname,
        index_col=False
        )
    espn_df = trim_names(espn_df)

    src_names = player_cat_df['Player']
    ref_names = espn_df['Player']
    
    # Check for errors and name mismatches between player_cats and ESPN
    error_names = check_matching_names(src_names, ref_names)
    if len(error_names) > 0:
        print("There are {} names with matching errors".format(len(error_names)))
        print("\n".join(error_names))    
    
    # Find closest player name matches in ESPN list
    matches_df = find_closest_matching_names(
        error_names, 
        ref_names=ref_names, 
        num_matches=2)

    print(matches_df[['name', 'bestMatch', 'bestScore']])
    
    # Check for user confirmation to save best matches
    choice = input('Apply best match name corrections? Press Y or y to confirm: ')
    if choice.upper() == 'Y':

        # Apply name corrections
        print("Applying {} name corrections".format(len(matches_df)))
        player_cat_df = apply_name_mods(
            mod_df=player_cat_df, 
            matches_df=matches_df)

        # Re-check for mismatches
        error_names = check_matching_names(player_cat_df['EspnPlayer'], espn_df['Player'])
        if len(error_names) > 0:
            print("There are {} names with matching errors".format(len(error_names)))
            print("\n".join(error_names))
    
        else:    
            print('No name matching errors found after modifications')

            # Add categories to ESPN df
            print("Adding categories to ESPN player data")
            name_cat = dict(zip(player_cat_df['EspnPlayer'], player_cat_df['Category']))
            espn_df['Category'] = espn_df['Player'].map(name_cat)
            
            # Save the modified ESPN dataframe
            mod_espn_df = save_and_reload_df(
                df=espn_df,
                fname='espn_field_cats.csv',
                path=event_path)