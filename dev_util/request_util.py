# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 10:15:04 2025

@author: kknow
"""

import requests
# import urllib
from bs4 import BeautifulSoup
import os

# from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor

from dev_util.config.app_logger import logger

class RequestAuthorizationError(Exception):
    """ Raised when authorization is denied for a request """
    """ Request status code 401 """
    pass

class UrlRequester():
    """
    Newish class that was introduced in the mktstats project.  This class allows
    for more complex url requests with specialized header data and results returned
    in json format.  A primary goal of this class is to go directly to the json 
    provider instead of extracting data from html-formatted pages.  In theory,
    this approach is more robust, provides access to a richer underlying dataset,
    and is less impacted by changes to output page formatting that often
    require restructuring of the implicit data extraction.
    
    If access to the page's source data is not available, then fallback to the 
    BeautifulSoup request approach.
    
    """
    
    def __init__(self, headers=None, verify=None, log_errors=True):

        # self.values = {}
        # default headers
        self.base_headers = {
            # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
            # TODO Move this to BaseChromeDriver?
            # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
            }
        self.headers = self.base_headers if headers is None else headers
        # These next two parameters can be used to check last call
        self._last_request = None
        self._last_response = None
        self.log_errors = log_errors
        self.verify = None if verify is None else verify
        # self.verify = verify
        self.timeout_secs = 120 # Default request timeout in seconds
        
        # Dictionary of methods to execute for each request type
        self.req_methods = {
            'get': requests.get,
            'post': requests.post,
            'put': requests.put,
            'delete': requests.delete,
            'patch': requests.patch,
            # 'head': requests.head,
            }

    def get_last_request(self, include_headers=False):
        
        d = self._last_request
        
        if isinstance(d, dict):
            
            d = d.copy()
            d.pop('headers')
            
            return d
        
        return d

    def get_last_response(self):
        return self._last_response
    
    def send_request(
            self, 
            req_type, 
            url, 
            path_params=None, 
            qry_params=None, 
            jdata=None, 
            headers=None, 
            timeout=None):
        '''
        Generic method for executing a request with optional support for various input
        parameters.

        Parameters
        ----------
        req_type : string
            A string label matching the type of the request (e.g., 'get', 'put', 'post', ...).
        url : string
            URL for the request.  The url can contain named {} tag, where the 
            path_params will be mapped to define the fully-specified url.
        path_params : dict, optional
            Dictionary containing a format string mapping to named {} tags in the 
            url.  The default is None.
        qry_params : dict, optional
            Dictionary containing a dictionary of query parameters for the request.  
            The default is None.
        jdata : dict, optional
            Dictionary containing the request body data in json/dict format. 
            The default is None.
        headers : dict, optional
            DESCRIPTION. The default is None.
        timeout : dict, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        r : TYPE
            DESCRIPTION.

        '''

        if headers is None:
            headers = self.headers
            
        if timeout is None:
            timeout = self.timeout_secs
            # print("Timeout = {} seconds".format(timeout))

        # if isinstance(data, dict):
        #     data = json.dumps(data)

        args = {
            'headers': headers,
            # 'verify': verify,
            # *** Testing
            # 'verify': verify,
            # "cert": "C:/Users/kknow/Downloads/Lucido Software Self CA.crt",
            # 'cert': "C:/Users/kknow/OneDrive/Documents/Analytics/dev/trm-api/data/xtrm-beta/cert/Lucido Software Self CA.p7c",
            'timeout': timeout
            }
        
        verify = self.verify
        if verify is not None:
            args['verify'] = verify
        

        # TODO Add validation and error handling
        # Get method_url with path params added
        method_url = url if path_params is None else url.format(**path_params)
        
        # Add query params
        if qry_params is not None:
            args['params'] = qry_params
        
        if req_type in ['post', 'put', 'patch']:
            # args['data'] = data
            args['json'] = jdata

        # Execute the request
        req_method = self.req_methods.get(req_type)
        if req_method is None:
            logger.error('Unknown or unsupported request type: {}'.format(req_type))
            return None            

        # https://realpython.com/python-requests/#the-get-request
        r = req_method(method_url, **args)
        # print(args)
        
        d = {
            'req_type': req_type,
            'url': url,
            'headers': headers
            }

        if path_params is not None:
            d['path_params'] = path_params
            
        if qry_params is not None:
            # 8/28/23 KK: Remove empty parameters, because some service methods don't handle
            qry_params_adj = {k:v for k,v in qry_params.items() if v is not None}
            
            d['qry_params'] = qry_params_adj
            
        # # Convert to python format to obviate downstream conversion
        # if data is not None:
        #     d['data'] = json.loads(data)
        if jdata is not None:
            d['json'] = jdata
            
        self._last_request = d
        self._last_response = r
        
        # self.status_code = r.status_code
        # if r.status_code not in [200, 201, 404]:
        #     logger.error('Unexpected request status code: {}'.format(r.status_code))

        return r
    
################################
# Begin Parallel request testing
################################

    def send_request_config(
            self, 
            request_config:dict, 
            headers:dict=None, 
            timeout:int=None):
        '''
        Method for sending a single url request, where request_configs is a 
        dictionary containing the named arguments for the send_request method.

        Parameters
        ----------
        request_config : TYPE
            Dictionary of the named arguments for the send request method.
        headers : TYPE, optional
            Dictionary of optional headers that are included with each request. The 
            default is None.

        Returns
        -------
        resp : requests.models.Response
            DESCRIPTION.

        '''
        
        resp = self.send_request(**request_config, headers=headers, timeout=timeout)
        
        return resp

    # TODO Not sure on method naming conventions
    # @calc_function_time
    def send_request_configs(
            self, 
            request_configs:list[dict],
            headers:dict=None,
            max_workers:int=100,
            timeout:int=None):
        '''
        Method for sending url requests in parallel based on a list of request_confgs,
        where each item in the list is a dictionary containing the named arguments for the
        send_request method.

        Parameters
        ----------
        request_configs : Dict
            List of dictionaries, each containing the arguments for the send_request method.
        headers : Dict, optional
            Set of optional headers that are included with each request. The default is None.
        max_workers : int, optional
            Maximum number of worker threads to process parallel requests. The default is 100.
        timeout : int, optional
            Maximum number of seconds per request before a timeout error is raised. The default is 30.

        Returns
        -------
        responses : list[requests.models.Response]
            DESCRIPTION.

        '''

        max_workers = len(request_configs) if len(request_configs) < max_workers else max_workers

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            responses = [resp for resp in executor.map(self.send_request_config, request_configs)]
        
        return responses

##############################
# End Parallel request testing
##############################
             
    def get_response(self, url, headers=None):
        '''
        Convenience method for get requests

        Parameters
        ----------
        url : TYPE
            DESCRIPTION.
        headers : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        r : TYPE
            DESCRIPTION.

        '''
        r = self.send_request(req_type='get', url=url, headers=headers)

        return r

    def get_soup(self, url, headers=None):
        
        response = self.get_response(url, headers)
        
        soup = BeautifulSoup(response.text,"lxml")

        return soup

    def get_json_data(self, url):
        """
        Simple url request for getting json data, based on assumption that the url
        returns data in json format.  This is convenient for direct data requests.

        Parameters
        ----------
        url : TYPE
            DESCRIPTION.

        Returns
        -------
        jdata : TYPE
            DESCRIPTION.

        """

        r = self.get_response(url)
        if r.status_code == 200:
            try:
                jdata = r.json()
            except ValueError: # includes simplejson.decoder.JSONDecodeError
                print('Error decoding response as JSON data')
                jdata = None
            except:
                print('Some other error decoding JSON data')
                jdata = None
        else:
            jdata = None
    
        return jdata

    def post_response(self, url, data, headers=None):
        '''
        Simple url request for posting json data, based on the assumption that the 
        url returns data in json format.

        Parameters
        ----------
        url : TYPE
            DESCRIPTION.
        data : TYPE
            DESCRIPTION.
        headers : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        r : TYPE
            DESCRIPTION.

        '''

        r = self.send_request(req_type='post', url=url, data=data, headers=headers)
        
        return r

    # TODO refactor response methods to reuse common portions
    def put_response(self, url, data, headers=None):
        '''
        Simple url request for putting json data, based on the assumption that the 
        url returns data in json format.

        Parameters
        ----------
        url : TYPE
            DESCRIPTION.
        data : TYPE
            DESCRIPTION.
        headers : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        r : TYPE
            DESCRIPTION.

        '''

        r = self.send_request(req_type='put', url=url, data=data, headers=headers)

        return r
    
    def download_url(
            self, 
            url, 
            save_fname, 
            save_path=None, 
            chunk_size=128):
        '''
        Downloads a file from a url and saves locally based on
        a filename and optional path location.

        Parameters
        ----------
        url : TYPE
            DESCRIPTION.
        save_fname : TYPE
            DESCRIPTION.
        save_path : TYPE, optional
            DESCRIPTION. The default is None.
        chunk_size : TYPE, optional
            DESCRIPTION. The default is 128.

        Returns
        -------
        None.

        '''
        # https://stackoverflow.com/questions/9419162/download-returned-zip-file-from-url
        
        if save_path is not None:
            path_fname = os.path.join(save_path, save_fname)
        else:
            path_fname = save_fname
            
        r = requests.get(url, stream=True)
        with open(path_fname, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)    
        
        return None
