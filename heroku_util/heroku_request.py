# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 12:43:57 2025

@author: kknow
"""

from timeit import default_timer as timer

from dev_util.request_util import UrlRequester

from dev_util.config.app_logger import init_app_logger

from heroku_util.heroku_response import HerokuResponse

logger = init_app_logger(app_name='HEROKU_UTIL')

class HerokuRequester(UrlRequester):
    
    def __init__(self, api_key, as_jdata=True, kwargs={}):
        
        self._base_url = "https://api.heroku.com"
        self.as_jdata = as_jdata
        
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {api_key}",
            'Content-Type': 'application/json'
            }
        
        super().__init__(headers=headers, **kwargs)
        
    def get_heroku_response(
            self,
            url,
            req_type='get',
            path_params=None, 
            qry_params=None, 
            jdata=None, 
            auto_refresh=True, 
            headers=None,
            timeout=None):
        
        start = timer()
        response = self.send_request(
            req_type=req_type, 
            url=url, 
            path_params=path_params, 
            qry_params=qry_params, 
            jdata=jdata, 
            headers=headers,
            timeout=timeout
            )
        end = timer()
        
        status_code = response.status_code

        if status_code == 200: # Valid response
            ...
        elif status_code == 201: # created
            logger.info('New item created')
        elif status_code == 202:
            logger.debug('Request accepted for processing')
        elif status_code == 504:
            logger.error("Gateway timeout error after {:.2f} seconds".format(end-start))
            logger.error(response.reason)
            logger.error(response.text)
        else:
            logger.error("Unexpected status code: {}, unable to get Heroku API Response data".format(status_code))
            logger.error(response.reason)
            logger.error(response.text)

        heroku_response = HerokuResponse(response)
        
        return heroku_response

    def get_result(
            self, 
            url, 
            req_type='get', 
            jdata=None,
            as_jdata=None,
            ):
        
        as_jdata = self.as_jdata if as_jdata is None else as_jdata
        
        hresp = self.get_heroku_response(
            url,
            req_type=req_type,
            jdata=jdata
            )
        
        if as_jdata:
            return hresp.jdata
        
        return hresp
        
    def get_all_apps(self, as_jdata=None):
        
        url = "https://api.heroku.com/apps"
        
        result = self.get_result(url, as_jdata=as_jdata)
        
        return result
    
    def get_app_info(self, app_name, as_jdata=None):

        url = f"https://api.heroku.com/apps/{app_name}"
        
        result = self.get_result(url, as_jdata=as_jdata)
        
        return result
    
    def get_dyno_list(self, app_name, as_jdata=None):
        
        url = f"https://api.heroku.com/apps/{app_name}/dynos"
        
        result = self.get_result(url, as_jdata=as_jdata)
        
        return result
    
    def get_dyno_sizes(self, app_name, as_jdata=None):
        
        url = f"https://api.heroku.com/apps/{app_name}/available-dyno-sizes"

        result = self.get_result(url, as_jdata=as_jdata)
        
        return result

    def get_formation_list(self, app_name, as_jdata=None):
        
        url = f"https://api.heroku.com/apps/{app_name}/formation"

        result = self.get_result(url, as_jdata=as_jdata)
        
        return result
    
    def get_formation_for_type(self, app_name, formation_type='web', as_jdata=None):
        
        url = f"https://api.heroku.com/apps/{app_name}/formation/{formation_type}"

        result = self.get_result(url, as_jdata=as_jdata)
        
        return result
    
    def restart_all_dynos(self, app_name, as_jdata=False):
        
        req_type = 'delete'
        
        url = f"https://api.heroku.com/apps/{app_name}/dynos"
        
        result = self.get_result(
            url=url,
            req_type=req_type,
            as_jdata=as_jdata)
        
        return result
    
    def stop_dyno_formation(
            self, 
            app_name, 
            formation_type='web', 
            as_jdata=False):
        
        req_type = 'post'
        
        url = f"https://api.heroku.com/apps/{app_name}/formations/{formation_type}/actions/stop"

        result = self.get_result(
            url=url,
            req_type=req_type,
            as_jdata=as_jdata)
        
        return result
    
    # Generic method for updating app data.
    # Specific app updates should use call this method
    def update_app(
            self, 
            app_name, 
            req_data:dict, 
            as_jdata=None):
        
        req_type = 'patch'
        
        url = f"https://api.heroku.com/apps/{app_name}/formation"
        
        # Validate req_data
        if ( not isinstance(req_data, dict)) or (req_data is None) or (len(req_data) == 0):
            logger.warn("Empty of missing update data. Nothing to update.")
            return None

        result = self.get_result(
            url=url,
            req_type=req_type,
            jdata=req_data,
            as_jdata=as_jdata)
        
        return result
    
    # Generic method for updating app formation data.
    # Specific app formation updates should use call this method
    def update_app_formation(
            self,
            app_name,
            req_data,
            formation_type='web',
            as_jdata=None):

        req_type = 'patch'
        
        url = f"https://api.heroku.com/apps/{app_name}/formation"

        result = self.get_result(
            url=url,
            req_type=req_type,
            jdata=req_data,
            as_jdata=as_jdata)
        
        result = self.update_app(app_name=app_name, req_data=jdata)
        
        return result
    
    def update_app_formation_quantity(
            self,
            app_name,
            quantity,
            formation_type='web',
            as_jdata=None
            ):

        jdata = {
            "updates": [
                {
                    'quantity': quantity,
                    'type': formation_type
                    }
                ]
            }
        
        result = self.update_app_formation(
            app_name,
            req_data=jdata,
            formation_type=formation_type,
            as_jdata=as_jdata)
        
        return result

if __name__ == "__main__":
    
    from dev_util.app_util import get_config_val
    
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
            
    # Get info for one app
    app_name = "kenalytics-golfstats-server"
    app_info = loader.get_app_info(app_name=app_name)
    
    # # Get Heroku response headers
    # hresp = loader.get_all_apps(as_jdata=False)
    # d = hresp.responseHeaders

    # # Get dyno list
    # dyno_list = loader.get_dyno_list(app_name)
    
    # # Get dyno sizes for app
    # dyno_sizes = loader.get_dyno_sizes(app_name)
    
    # # Restart all dynos
    # hresp = loader.restart_all_dynos(app_name)
    
    # # Get the formation info
    # formation_type = 'web'
    
    # formation_list = loader.get_formation_list(app_name)
    # formation_info = loader.get_formation_for_type(app_name, formation_type=formation_type)
    
    # # # # *** This doesn't work
    # # Stop dyno formation
    # jdata = loader.stop_dyno_formation(
    #     app_name=app_name, 
    #     formation_type=formation_type, 
    #     as_jdata=True)
    
    # # # *** This doesn't work
    # Scale formation to zero
    qty = 0
    jdata = loader.update_formation_quantity(
        app_name=app_name,
        quantity=qty
        )
