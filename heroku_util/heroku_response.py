# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 12:45:23 2025

@author: kknow
"""

from requests.models import Response

from dev_util.config.app_logger import init_app_logger

logger = init_app_logger(app_name='HEROKU_UTIL')

# Heroku response wrapper class - gets relevant info from
#  the respons, such as number of requests remaining and
# any status codes, etc.
class HerokuResponse():
    
    def __init__(self, resp:Response):
        
        self._resp:Response = resp
        
        self._status_code = None if resp is None else resp.status_code
        self._reason = None if resp is None else resp.reason
        self._text = None if resp is None else resp.text
        
        self._resp_jdata = None
        
        self.__init_resp_jdata__()
        
    def __get_json_data_from_response(self, r):
        
        try:
            jdata = r.json()
        except ValueError: # includes simplejson.decoder.JSONDecodeError
            logger.error('Error decoding response as JSON data')
            jdata = None
        except:
            logger.error('Encountered some other error decoding JSON data: {}'.format(r.status_code))
            jdata = None

        return jdata
        
    def __init_resp_jdata__(self):
        
        # TODO Check status and whether this is json convertible
                
        resp_jdata = self.__get_json_data_from_response(self.response)
        self._resp_jdata = resp_jdata
                        
    def _get_error_data(self):
        
        edata = self.jdata
        
        if edata is None:
            edata = self._resp.text
            
        return edata

    def _get_jdata(self):
        
        jdata = self._resp_jdata
            
        return jdata

    def _get_reason(self):
        return self._reason

    # TODO this is extraneous
    def _get_response(self):
        return self._resp
    
    def _get_response_headers(self):
        
        d = dict(self.response.headers)
        
        return d
        
    def _get_status_code(self):
        return self._status_code
    
    def _get_text(self):
        return self._text
            
    errorData = property(fget=_get_error_data)
    jdata = property(fget=_get_jdata)
    reason = property(fget=_get_reason)
    response = property(fget=_get_response)
    responseHeaders = property(fget=_get_response_headers)
    status_code = property(fget=_get_status_code)
    text = property(fget=_get_text)

