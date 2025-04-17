# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 13:01:18 2025

@author: kknow
"""

if __name__ == "__main__":
    ...
    
    from dev_util.app_util import get_config_val
    
    from heroku_util.heroku_request import HerokuRequester
    
    api_key = get_config_val(
        config_data_key="HEROKU_API_KEY", 
        config_data_grp="HEROKU")
    
    loader = HerokuRequester(api_key=api_key)

    # app_name = "kenalytics-golfstats-server"
    app_name = "kenalytics-golfstats"
    

    #########################################################
    # To scale formation to zero, which also forces shutdown
    # of running processes
    #########################################################
    
    qty = 0
    jdata = loader.update_formation_quantity(
        app_name=app_name,
        quantity=qty
        )

