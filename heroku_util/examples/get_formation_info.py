# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 13:22:16 2025

@author: kknow
"""

if __name__ == "__main__":
    
    from dev_util.app_util import get_config_val
    
    from heroku_util.heroku_request import HerokuRequester

    api_key = get_config_val(
        config_data_key="HEROKU_API_KEY", 
        config_data_grp="HEROKU")
    
    loader = HerokuRequester(api_key=api_key)

    # app_name = "kenalytics-golfstats-server"
    
    # Get a list of all apps
    apps_list = loader.get_all_apps()
    
    if apps_list is not None:
        app_names = [d.get('name') for d in apps_list]
        print(f"Found {len(app_names)} apps:")
        for app_name in app_names:
            print(app_name)
            
    # Get info for one app
    app_name = "kenalytics-golfstats"
    app_info = loader.get_app_info(app_name=app_name)

    # Get the formation list
    formation_list = loader.get_formation_list(app_name)
