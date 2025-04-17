# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 12:42:11 2025

@author: kknow
"""

if __name__ == "__main__":
    
    from dev_util.app_util import get_config_val
    
    from heroku_util.heroku_request import HerokuRequester
    
    api_key = get_config_val(
        config_data_key="HEROKU_API_KEY", 
        config_data_grp="HEROKU")
    
    loader = HerokuRequester(api_key=api_key)

    app_name = "kenalytics-golfstats-server"
    
    # # Get a list of all apps
    # apps_list = loader.get_all_apps()
    
    # if apps_list is not None:
    #     app_names = [d.get('name') for d in apps_list]
    #     print(f"Found {len(app_names)} apps:")
    #     for app_name in app_names:
    #         print(app_name)
            
    # # Get info for one app
    # app_info = loader.get_app_info(app_name=app_name)

    #########################################################
    # To scale formation to zero, which also forces shutdown
    # of running processes
    #########################################################
    
    qty = 0
    jdata = loader.update_formation_quantity(
        app_name=app_name,
        quantity=qty
        )

    ##############################
    # To re-scale formation to 1
    ##############################
    
    qty = 1
    jdata = loader.update_formation_quantity(
        app_name=app_name,
        quantity=qty
        )
