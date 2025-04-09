# -*- coding: utf-8 -*-
"""
Created on Wed Dec  1 17:01:03 2021

@author: kknow
"""

import abc
import pandas as pd
import io

from dev_util.data_util import RemoteDataLoader
from dev_util.gen_util import handle_exception, gen_handler
from dev_util.pandas_util import load_csv_as_df, save_df_to_csv
from dev_util.download_util import UrlRequester
from config.app_config import app_data_configs

from timeit import default_timer as timer

def get_config_data_for_loader(config_name, loader_mode='local'):

    config = app_data_configs.get(config_name, None)
    if config is None:
        print("Unable to get configuration data for {}".format(config_name))
        return None
    config_data = config.get(loader_mode, None)
    if config_data is None:
        print("Unable to get {} configuration data for {}".format(loader_mode, config_name))
        return None

    return config_data

# Abstract class for retrieving saved result data
class AbstractResultDataLoader(abc.ABC):

    # TODO Consider renaming this to load_dataset to support broader formats
    @abc.abstractclassmethod
    def load_dataset_as_df(self, config_name, debug=False):
        raise NotImplementedError("Must implement load_dataset_as_df method")

    @abc.abstractclassmethod
    def save_df_as_dataset(self, df, config_name, debug=False):
        raise NotImplementedError("Must implement save_df_as_dataset method")

# Class for retrieving saved result data stored in the local file system
# This version splits out the local functionality that was initially 
# implemented as part of the ResultDataLoader
class LocalResultDataLoader(AbstractResultDataLoader):
    
    def __init__(self, log_load_times=False):
        self.log_load_times = log_load_times
        # self.result_data_configs = app_data_configs
        
    @handle_exception(gen_handler, 'Error loading dataset:')
    def load_dataset_as_df(self, config_name, debug=None):

        debug = self.log_load_times if debug is None else debug
        
        df = None

        # Get configuration data for the loader mode 
        config = get_config_data_for_loader(config_name, loader_mode='local')
        if config is None:
            print("Unable to get local configuration data for {}".format(config_name))
            return None
        
        # Load dataset from local storage
        if debug:
            msg = 'Loading {} from local store'.format(config_name)
            print(msg)
            start = timer()
        # df = load_csv_as_df(path=config.get('path'), fname=config.get('fname'), prepend_app_path=False)
        df = load_csv_as_df(path=config.get('path'), fname=config.get('fname'))
        if debug:
            end = timer()
            msg = 'Completed loading {} from local store in {:.2f} seconds'.format(config_name, end - start)
            print(msg)

        return df

    # TODO Consider moving to a read-write class
    @handle_exception(gen_handler, 'Error saving dataset:')
    def save_df_as_dataset(self, df, config_name, debug=None):

        debug = self.log_load_times if debug is None else debug

        # Get configuration data for the loader mode 
        config = get_config_data_for_loader(config_name, loader_mode='local')
        if config is None:
            print("Unable to get local configuration data for {}".format(config_name))
            return None
        
        # Save dataset to local storage
        if debug:
            msg = 'Saving {} to local store'.format(config_name)
            print(msg)
            start = timer()
        # df = save_df_to_csv(df, local_path=config.get('path'), local_fname=config.get('fname'), prepend_app_path=False)
        df = save_df_to_csv(df, local_path=config.get('path'), local_fname=config.get('fname'))
        if debug:
            end = timer()
            msg = 'Completed saving {} to local store in {:.2f} seconds'.format(config_name, end - start)
            print(msg)

        return None

# Class for retrieving saved result data stored in a remote MongoDB server
# This version splits out the remote functionality that was initially 
# implemented as part of the ResultDataLoader
class RemoteResultDataLoader(AbstractResultDataLoader):

    def __init__(self, rdl:RemoteDataLoader=None, log_load_times=False):
        
        # TODO Enhance to take db_name as option instead of rdl to streamline usual initialization pattern
        self.rdl = rdl
        self.log_load_times = log_load_times
        self.result_data_configs = app_data_configs
        # # self.find_kwargs = {}
        # # https://kb.objectrocket.com/mongo-db/how-to-sort-mongodb-documents-in-a-collection-using-python-373
        # self.sort_order = -1 # Default sort order for retrieving documents
        # self.find_kwargs = {'sort': [(self.update_key, 1)]} # By default, retrieve datasets in ascending order

        # TODO Add caching flag for holding large datasets
        # Note: cached datasets are not going to work well in multi-tenant dash apps

    @handle_exception(gen_handler, 'Error loading dataset:')
    def load_dataset_as_df(self, config_name, debug=None):

        debug = self.log_load_times if debug is None else debug

        df = None
        
        # Get configuration data for the loader mode 
        config = get_config_data_for_loader(config_name, loader_mode='remote')
        if config is None:
            print("Unable to get remote configuration data for {}".format(config_name))
            return None
        
        # Load dataset from remote server
        # TODO Validate config settings
        cname = config.get('cname')
        if debug:
            msg = 'Loading {} from remote store'.format(config_name)
            print(msg)
            start = timer()
        df = self.rdl.load_remote_df_from_docs(cname, find_kwargs={'projection':{'_id':False}}, debug=True)
        if debug:
            end = timer()
            msg = 'Completed loading {} from remote store in {:.2f} seconds'.format(config_name, end - start)
            print(msg)

        return df

    # TODO Consider moving to a read-write class
    @handle_exception(gen_handler, 'Error saving dataset:')
    def save_df_as_dataset(self, df, config_name, debug=None):

        debug = self.log_load_times if debug is None else debug

        # # TODO Validate that data_config exists
        # config = self.result_data_configs.get(config_name, None)
        # if config is None:
        #     print("Unable to get configuration data for {}".format(config_name))
        #     return None
        
        raise NotImplementedError("Currently unable to save {} to remote server.".format(config_name))
    
        # return None    

# Class for retrieving csv result data through a url request
class UrlResultDataLoader(AbstractResultDataLoader):
    
    def __init__(self, log_load_times=False):
        self.log_load_times = log_load_times
        # self.result_data_configs = app_data_configs
        self.rq = None

    @handle_exception(gen_handler, 'Error loading dataset:')
    def load_dataset_as_df(self, config_name, debug=None):

        debug = self.log_load_times if debug is None else debug
        
        if self.rq is None:
            self.rq = UrlRequester()    
        rq = self.rq
        
        end = timer()

        df = None

        # Get configuration data for the loader mode 
        config = get_config_data_for_loader(config_name, loader_mode='url')
        if config is None:
            print("Unable to get url loader configuration data for {}".format(config_name))
            return None

        path_tag = config.get('path', None)
        if path_tag is None:
            print("Url path tag missing or invalid for {}".format(config_name))
            return None

        fname_tag = config.get('fname', None)
        if fname_tag is None:
            print("Url filename tag missing or invalid for {}".format(config_name))
            return None

        url_csv = "{}{}".format(path_tag,fname_tag)

        # Load csv dataset from url
        if debug:
            msg = 'Loading {} from remote url'.format(config_name)
            print(msg)
            start = timer()
        # TODO check that response is valid
        # TODO Consider moving this to an encapsulated method
        # r = rq.get_request(url_csv)
        resp = rq.get_response(url_csv)
        df = pd.read_csv(io.StringIO(resp.content.decode("utf-8")), index_col=False)
        if debug:
            end = timer()
            msg = "Completed loading {} from remote url in {:.2f} seconds".format(config_name, end - start)
            print(msg)

        return df

    # TODO Consider moving to a read-write class
    @handle_exception(gen_handler, 'Error saving dataset:')
    def save_df_as_dataset(self, df, config_name, debug=None):        
        raise NotImplementedError("Currently unable to save {} to remote server.".format(config_name))

# # Composite class for retrieving saved market data stored on a remote data server
# # TODO Consider whether this should extend the RemoteDataLoader
# # This does not do any caching for now
# class ResultDataLoader():
    
#     def __init__(self, rdl:RemoteDataLoader=None, loader_mode='local', log_load_times=False):
        
#         # TODO Enhance to take db_name as option instead of rdl to streamline usual initialization pattern
#         self.rdl = rdl
#         self.loader_mode = loader_mode # 'local', 'remote', (future) 'incremental'
#         self.app_data_configs = app_data_configs
#         self.log_load_times = log_load_times
#         # # self.find_kwargs = {}
#         # # https://kb.objectrocket.com/mongo-db/how-to-sort-mongodb-documents-in-a-collection-using-python-373
#         # self.sort_order = -1 # Default sort order for retrieving documents
#         # self.find_kwargs = {'sort': [(self.update_key, 1)]} # By default, retrieve datasets in ascending order

#         # TODO Add caching flag for holding large datasets
#         # Note: cached datasets are not going to work well in multi-tenant dash apps

#     @handle_exception(gen_handler, 'Error loading dataset:')
#     def load_dataset_as_df(self, config_name, debug=None):

#         df = None

#         if debug is None:
#             debug = self.log_load_times
        
#         # TODO Validate that data_config exists
#         config = self.app_data_configs.get(config_name, None)
#         if config is None:
#             print("Unable to get configuration data for {}".format(config_name))
#             return None

#         if self.loader_mode == 'local':
#             # Load dataset from local storage
#             if debug:
#                 msg = 'Loading {} from local store'.format(config_name)
#                 print(msg)
#                 start = timer()
#             df = load_local_csv_data(local_path=config.get('path'), local_fname=config.get('fname'))
#             if debug:
#                 end = timer()
#                 msg = 'Completed loading {} from local store in {:.2f} seconds'.format(config_name, end - start)
#                 print(msg)
#         else:
#             # Load dataset from remote server
#             # TODO Validate config settings
#             cname = config.get('cname')
#             if debug:
#                 msg = 'Loading {} from remote store'.format(config_name)
#                 print(msg)
#                 start = timer()
#             df = self.rdl.load_remote_df_from_docs(cname, find_kwargs={'projection':{'_id':False}}, debug=True)
#             if debug:
#                 end = timer()
#                 msg = 'Completed loading {} from remote store in {:.2f} seconds'.format(config_name, end - start)
#                 print(msg)

#         return df
            