# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 10:21:00 2021

@author: kknow
"""

import os
import json
import pandas as pd
from pymongo import MongoClient
from dev.util.gen_util import handle_exception, gen_handler
from dev.util.app_util import get_now
import certifi

class RemoteDataLoader():
    """ 
    Remote data loader class for connecting to Mongo DB.  This is a read-only
    class that can load data from the remote server.  It has no write capabilities
    by design and by permissioning
    
    """
    
    def __init__(self, db_name=None, connect_str=None):
        self.connect_str = connect_str
        self.client = None
        self.dbName = db_name
        self.db = None
        
        self.__initialize()
        
    def __initialize(self):
        if self.connect_str is None:
            self.connect_str = self.__get_connect_string() 
        # self.client = MongoClient(self.connect_str)
        # self.db = None if self.dbName is None else self.client.get_database(self.dbName)
        
        # https://stackoverflow.com/questions/68123923/pymongo-ssl-certificate-verify-failed-certificate-verify-failed-unable-to-ge
        # self.client = MongoClient(self.connect_str)
        self.client = MongoClient(self.connect_str, tlsCAFile=certifi.where())
        # self.client = MongoClient(self.connect_str)
        
        self.db = None if self.dbName is None else self.client.get_database(self.dbName)

    # Utility method to get the default connection string for the remote data server
    # TODO Consider where to put this, refactor, and cleanup
    # TODO Convert this to use the app_util method
    def __get_connect_string(self):
        fname = "config.json"
        config_data_grp = 'GSD_Server'
        config_data_key = 'GSD_Connect'
        env_var_name = config_data_key
        connect_str = None
        
        # Check if file exists
        file_exists = os.path.isfile(fname)
        if file_exists:
            with open(fname, "r") as jsonfile:
                data = json.load(jsonfile) # Reading the file
                # print("Read successful")
                jsonfile.close()
                
                d = data.get(config_data_grp, None)
                
                if d is not None:
                    connect_str = d.get(config_data_key, None)
        else:
            # If not, check environment config
            # print("File: {} not found".format(fname))
            # print("Checking for configuration variables")
            connect_str = os.getenv(env_var_name, None)
    
        return connect_str 
    
    # @handle_exception(gen_handler, 'Unable to get dataframe from remote data:')            
    def get_df_from_data(self, data_dict):
        
        if data_dict is None:
            print('Missing or empty data dictionary.  Unable to create dataframe.')
            return None
        
        df = None
        dd_data = data_dict.get('data', None)
        if dd_data is None:
            # Check for dataframe key
            df = dd_data.get('df', None)
            if df is None:
                print('Data dictionary contains no dataframe data.')
                return None
        else:
            # Check for records and orient
            df_orient = data_dict.get('orient', None)        
            if df_orient == 'split':
                df = pd.DataFrame(**dd_data)
            else:
                df = pd.DataFrame(dd_data)
                
        return df

    # Docs on find method for collections:
    # https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html
    # @handle_exception(gen_handler, 'Error loading remote data:')
    def load_remote_data_item(self, collection, filter_tag={}, find_kwargs={}):
        """
        Generic method for loading a single data item from a remote MongoDB 
        source.  This refactors the common logic for inserting data to promote
        reuse across different methods that save specialized data.  
        If find_tag is empty, then an arbitrary find_one call will be executed. 
        Should be fine if there is only one item in the collection.  
        
        Parameters
        ----------
        collection : TYPE
            DESCRIPTION.
        find_tag : TYPE, optional
            DESCRIPTION. The default is {}.

        Returns
        -------
        data_item : TYPE
            DESCRIPTION.

        """
    
        db = self.db
        
        if db is None:
            # TODO Convert to exception
            print("No database specified. Unable to save dataframe.")
            return None
        
        if type(collection) is str:
            collection = db.get_collection(collection)
        
        # Reload dataframe
        data_item = collection.find_one(filter_tag, **find_kwargs)
        
        # TODO There is a major bug here where this value goes to None when the result is passed back
        # Note: it appears that the handoff bug for the return value is related to the exception handler wrapper
        # val = list(data_from_db.keys())[0]
        # val = 'Test'
    
        return data_item

    # @handle_exception(gen_handler, 'Error loading remote data:')
    def load_remote_data_items(self, collection, filter_tag={}, find_kwargs={}):
        """
        Generic method for loading multiple data items from a remote MongoDB 
        source.  This refactors the common logic for inserting data to promote
        reuse across different methods that save specialized data.
        If find_tag is empty, then all data items in the collection will be 
        returned.  
        
        Parameters
        ----------
        collection : TYPE
            DESCRIPTION.
        find_tag : TYPE, optional
            DESCRIPTION. The default is {}.

        Returns
        -------
        data_items : TYPE
            returns a list of data items from the db.

        """
    
        db = self.db
        
        if db is None:
            # TODO Convert to exception
            print("No database specified. Unable to save dataframe.")
            return None
        
        if type(collection) is str:
            collection = db.get_collection(collection)
        
        # Reload dataframe
        data_from_db = collection.find(filter_tag, **find_kwargs)
        
        data_items = [doc for doc in data_from_db]
        
        # TODO There is a major bug here where this value goes to None when the result is passed back
        # Note: it appears that the handoff bug for the return value is related to the exception handler wrapper
        # val = list(data_from_db.keys())[0]
        # val = 'Test'
    
        return data_items

    # @handle_exception(gen_handler, 'Error loading remote dataframe:')
    def load_remote_df(self, collection, find_kwargs={}):
        """
        Loads a dataframe from a remote MongoDB source, assuming that the dataframe
        was saved in dictionary format using to_dict() method on the dataframe.  If find_tag
        is empty, then an arbitrary find_one call will be executed. Should
        be fine if there is only one item in the collection.
        
        Parameters
        ----------
        collection : TYPE
            DESCRIPTION.
        find_tag : TYPE, optional
            DESCRIPTION. The default is {}.

        Returns
        -------
        df2 : TYPE
            DESCRIPTION.

        """

        # Reload dataframe
        data_from_db = self.load_remote_data_item(collection, find_kwargs)
        df = self.get_df_from_data(data_from_db)
    
        return df

    @handle_exception(gen_handler, 'Error loading remote dataframe as json:')
    def load_remote_df_from_json(self, collection, find_kwargs={}):
        """
        Loads a dataframe from a remote MongoDB source.  If find_tag
        is empty, then an arbitrary find_one call will be executed. Should
        be fine if there is only one item in the collection.
        
        Parameters
        ----------
        collection : TYPE
            DESCRIPTION.
        find_tag : TYPE, optional
            DESCRIPTION. The default is {}.

        Returns
        -------
        df2 : TYPE
            DESCRIPTION.

        """
    
        # Reload dataframe
        data_from_db = self.load_remote_data(collection, find_kwargs)
        df = pd.read_json(data_from_db["data"], orient=data_from_db['orient'])
    
        return df

class RemoteDataServer(RemoteDataLoader):
    """ 
    Remote data server class for connecting to Mongo DB. This class extends the 
    RemoteDataLoader class and add the ability to write data and modify existing
    data.
    
    """
    
    def __init__(self, db_name=None, connect_str=None):
        super(RemoteDataServer, self).__init__(db_name, connect_str)

    @handle_exception(gen_handler, 'Error saving remote data:')
    def save_remote_data(self, data, collection, overwrite=False, add_timestamp=True):
        """
        Generic method for inserting data into a remote MongoDB collection.  This refactors
        the common logic for inserting data to promote reuse across different 
        methods that save specialized data.
        
        Parameters
        ----------
        data : dictionary.
            Data to save remotely.  Should be complete data set to insert.
        collection : collection or name of a collection
            Collection where data will be stored.
        overwrite : TYPE, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        None.

        """
        
        # TODO this needs some cleanup for better handling of capped vs. non-capped collections and overwrite settings
        db = self.db

        if db is None:
            # TODO Convert to exception
            print("No database specified. Unable to save dataframe.")
            return None

        if add_timestamp:
            now = get_now()
            data.update({'save_timestamp': now})
            # save_data.update(data)

        save_data = data

        # if type(collection) is str:
        if isinstance(collection, str):
            collection = db.get_collection(collection)
            
        if overwrite:
            # then assume for now that collection is not capped
            # TODO add validation check for capped collections
            
            # Start a transaction wrapper for overwrites in case we have a failure
            with self.client.start_session() as session:
                with session.start_transaction():
                    if collection.count_documents({}) > 0:
                        # drop existing table/collection
                        # db.drop_collection(collection, session=session)
                        # Clear all existing documents from collection
                        collection.delete_many({}, session=session)                    
                    res = collection.insert_one(save_data, session=session)
        else:
            # we simply insert the transaction into the collection
            # Updated for pymongo 4.1
            res = collection.insert_one(save_data)

        return res

    @handle_exception(gen_handler, 'Error saving dataframe remotely:')
    def save_remote_df(self, df, collection, orient='list', meta_tags={}, overwrite=False, add_timestamp=True):
        """
        Saves a dataframe to a remote MongoDB server.  The dataframe is converted to
        records.
        
        Parameters
        ----------
        df : TYPE
            DESCRIPTION.
        collection : collection or name of a collection
            Collection where dataframe will be stored.
        orient : string
            Format for the json conversion
        meta_tags : TYPE, optional
            DESCRIPTION. The default is {}.
        overwrite : TYPE, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        None.

        """

        # Convert dataframe to dictionary
        data_dict = df.to_dict(orient)
        
        # Save dataframe
        data = {**meta_tags, **{'orient':orient, "data": data_dict}}
        
        self.save_remote_data(data, collection, overwrite=overwrite, add_timestamp=add_timestamp)
        
        return None
    
    @handle_exception(gen_handler, 'Error saving dataframe remotely as json:')
    def save_remote_df_json(self, df, collection, orient='split', meta_tags={}, overwrite=False, add_timestamp=True):
        """
        Saves a dataframe to a remote MongoDB server.  The dataframe is converted to
        json format using the 'orient' input parameter.
        
        Parameters
        ----------
        df : TYPE
            DESCRIPTION.
        collection : collection or name of a collection
            Collection where dataframe will be stored.
        orient : string
            Format for the json conversion
        meta_tags : TYPE, optional
            DESCRIPTION. The default is {}.
        overwrite : TYPE, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        None.

        """
        
        # Save dataframe
        # data_dict = df.to_dict("records")
        jdata = df.to_json(orient=orient)
        data = {**meta_tags, **{'orient':orient, "data": jdata}}
        
        self.save_remote_data(data, collection, overwrite=overwrite, add_timestamp=add_timestamp)
        
        return None
