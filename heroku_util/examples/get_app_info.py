# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 16:18:06 2025

@author: kknow
"""

import pandas as pd

def simplify_key_field(
        app_data,
        key_name,
        keep_field_name='name'):
    
    d = app_data.get(key_name)
    
    if d is None:
        return None
    
    keep_val = d.get(keep_field_name)
    app_data[key_name] = keep_val
    
    return app_data

def simplify_key_fields(
        app_data,
        key_field_configs
        ):
    
    for config in key_field_configs:
        app_data = simplify_key_field(
            app_data, **config)
        
    return app_data

def simplify_app_list(
        app_list,
        key_field_configs=None):
    
    if key_field_configs is None:
        
        key_field_configs = [
            {'key_name': 'build_stack'},
            {'key_name': 'generation'},
            {'key_name': 'owner', 'keep_field_name': 'email'},
            {'key_name': 'region'},
            {'key_name': 'stack'},
            ]
    
    for app_data in app_list:
        app_data = simplify_key_fields(
            app_data=app_data,
            key_field_configs=key_field_configs)
        
    return app_list

def add_mb_sizes_to_app_data(app_data, size_keys):
    
    factor = 1024 * 1024
    
    for key in size_keys:

        size_b = app_data.get(key)

        if size_b is not None:

            mb_col = f"{key}_mb"
            app_data[mb_col] = size_b / factor
            
    return app_data

def add_mb_sizes_to_app_list(app_list, size_keys=None):
    
    if size_keys is None:
        size_keys = [
            'repo_size',
            'slug_size'
            ]
    app_list = [add_mb_sizes_to_app_data(app_data, size_keys) for app_data in app_list]
                
    return app_list

def get_app_list_df(
        app_list,
        simplify_keys=True,
        add_mb_sizes=True):
    
    if simplify_keys:
        app_list = simplify_app_list(app_list=app_list)
        
    if add_mb_sizes:
        app_list = add_mb_sizes_to_app_list(app_list)
        
    df = pd.DataFrame(app_list)
    
    return df

if __name__ == "__main__":

    from dev_util.app_util import get_config_val
    
    from heroku_util.heroku_request import HerokuRequester
    
    api_key = get_config_val(
        config_data_key="HEROKU_API_KEY", 
        config_data_grp="HEROKU")
    
    loader = HerokuRequester(api_key=api_key)

    app_name = "kenalytics-golfstats-server"

    # Get a list of all apps
    app_list = loader.get_all_apps()
    
    if app_list is not None:
        app_names = [d.get('name') for d in app_list]
        print(f"Found {len(app_names)} apps:")
        for app_name in app_names:
            print(app_name)

    app_list_df = get_app_list_df(app_list)