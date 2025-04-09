# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 10:21:00 2021

@author: kknow

Set of utility classes and methods for data-related components, including
dataframe and dictionary wrapper and conversion classes.

"""

# import os
# import json
import pandas as pd
from dev_util.gen_util import handle_exception, gen_handler
from dev_util.datetime_util import get_now
# from dev_util.app_util import get_config_val
# from timeit import default_timer as timer
from pandas.testing import assert_frame_equal

import requests
from json import dumps, loads
# from bson.json_util import dumps, loads

class RequestDataLoader():
    """ 
    Request-based data loader class for connecting to Mongo DB using the data API.  This is a read-only
    class that can load data from the remote server.  It has no write capabilities
    by design and by permissioning
    
    https://www.mongodb.com/docs/atlas/api/data-api-resources/#base-url
    
    """
    
    def __init__(self, db_name=None, cluster_name=None, api_key=None):

        # TODO Move to config data
        self.base_url =  "https://us-east-1.aws.data.mongodb-api.com/app/data-vpqyv/endpoint/data/v1/{}"

        self.db_name = db_name
        self.cluster_name = cluster_name
        # TODO Convert to property, so we can update headers if/when API key changes
        self.api_key = api_key
        self.content_type = 'application/json'
        
    def _get_headers(self):
        
        headers = {
              'Content-Type': self.content_type,
              # 'Access-Control-Request-Headers': '*',
              'api-key': self.api_key, 
            }
        
        return headers

    # @handle_exception(gen_handler, 'Unable to get dataframe from remote data:')            
    def get_df_from_data(self, data_dict):
        """
        Converts a single document into a dataframe.  Note that this
        currently includes some hard-coded assumptions about the document 
        structure.
        
        TODO Extract hard-coded assumptions into class and/or method parameters

        Parameters
        ----------
        data_dict : TYPE
            DESCRIPTION.

        Returns
        -------
        df : TYPE
            DESCRIPTION.

        """
        
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

    @handle_exception(gen_handler, 'Error loading remote data:')
    def _send_request(self, req_type, action_tag, req_body, headers=None):
        
        url = self.base_url.format(action_tag)
        
        headers = self._get_headers() if headers is None else headers

        response = requests.request(req_type, url, headers=headers, data=dumps(req_body))

        return response
    
    # Docs on find method for collections:
    # https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html
    @handle_exception(gen_handler, 'Error loading remote data:')
    def load_data_item(self, cname, db_name=None, filter_tags={}, projection_tags={}):
        """
        Generic method for loading a single data item from a remote MongoDB 
        source using the Data API.  This refactors the common logic for inserting data to promote
        reuse across different methods that save specialized data.  
        If find_tag is empty, then an arbitrary find_one call will be executed. 
        Should be fine if there is only one item in the collection.  
        
        Parameters
        ----------
        cname : TYPE
            Name of the collection.
        filter_tags : TYPE, optional
            DESCRIPTION. The default is {}.
        projection_tags : TYPE, optional
            DESCRIPTION. The default is {}.

        Returns
        -------
        data_item : TYPE
            DESCRIPTION.

        """

        action_tag = 'action/findOne'
        
        db_name = self.db_name if db_name is None else db_name
        
        if db_name is None:
            # TODO Convert to exception
            print("No database specified. Unable to load data.")
            return None
        
        req_body = {
            "dataSource": self.cluster_name,
            "database": db_name,
            "collection": cname,
            'filter': filter_tags,
            "projection": projection_tags,
        }

        response = self._send_request(req_type='POST', action_tag=action_tag, req_body=req_body)
        
        # Expect status code 200 for loading data
        if response.status_code == 200:
            data_item = loads(response.text)
            if isinstance(data_item, dict):
                doc = data_item.get('document')
                return doc
        else:
            print('Unable to get data item')
            return response.text
        
        return data_item

    # @handle_exception(gen_handler, 'Error loading remote data:')
    def load_data_items(self, cname, db_name=None, filter_tags={}, projection_tags={}, sort_tags={}, max_items=10, debug=False):
        """
        Generic method for loading multiple data items from a remote MongoDB 
        source.  This refactors the common logic for retrieval data to 
        promote reuse across different methods that save specialized data.
        If find_tag is empty, then all data items in the collection will be 
        returned.  
        
        Parameters
        ----------
        collection : TYPE
            DESCRIPTION.
        find_tag : TYPE, optional
            DESCRIPTION. The default is {}.
        debug : boolean, optional
            if true, print debug messages, else ignore.  The default is False.

        Returns
        -------
        data_items : TYPE
            returns a list of data items from the db.

        """
    
        action_tag = 'action/find'
        
        db_name = self.db_name if db_name is None else db_name

        if db_name is None:
            # TODO Convert to exception
            print("No database specified. Unable to load data.")
            return None
        
        req_body = {
            "dataSource": self.cluster_name,
            "database": db_name,
            "collection": cname,
            'filter': filter_tags,
            "projection": projection_tags,
            'limit': max_items,
            "sort": sort_tags,
        }

        response = self._send_request(req_type='POST', action_tag=action_tag, req_body=req_body)
        
        # Expext status code 200
        if response.status_code == 200:
            data_items = loads(response.text)
            if isinstance(data_items, dict):
                docs = data_items.get('documents')
                return docs
        else:
            print('Unable to get data items')
            return response.text

    def load_df(self, cname, db_name=None, filter_tags={}, projection_tags={}):
        
        data_item = self.load_data_item(cname, db_name=db_name, filter_tags=filter_tags, projection_tags=projection_tags)
        
        df = self.get_df_from_data(data_dict=data_item)
        
        return df
        
class RequestDataServer(RequestDataLoader):
    """ 
    Remote data server class for connecting to Mongo DB using the Data API. This class extends the 
    RemoteDataLoader class and add the ability to write data and modify existing
    data.
    
    """
    
    def __init__(self, db_name=None, cluster_name=None, api_key=None):
        super(RequestDataServer, self).__init__(db_name, cluster_name=cluster_name, api_key=api_key)

    @handle_exception(gen_handler, 'Error saving remote data:')
    def save_data(self, data, cname, db_name=None, filter_tag={}, overwrite=False, add_timestamp=True):
        """
        Generic method for inserting data into a remote MongoDB collection.  This refactors
        the common logic for inserting data to promote reuse across different 
        methods that save specialized data.
        
        Parameters
        ----------
        data : dictionary.
            Data to save remotely.  Should be complete data set to insert.
        cname : Name of a collection
            Collection where data will be stored.
        overwrite : TYPE, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        None.

        """

        # TODO Validate data to save before we overwrite existing data
        headers = self._get_headers()

        cluster_name = self.cluster_name
        if cluster_name is None:
            # TODO Convert to exception
            print("No cluster name specified. Unable to save data.")
            return None
        
        db_name = self.db_name if db_name is None else db_name

        if db_name is None:
            # TODO Convert to exception
            print("No database specified. Unable to save data.")
            return None

        if overwrite:
            
            # TODO Add method to delete items
            action_tag = 'action/deleteMany'
            url = self.base_url.format(action_tag)

            req_body = {
                "dataSource": cluster_name,
                "database": db_name,
                "collection": cname,
                "filter": filter_tag
            }

            # Clear existing data
            response = requests.request("POST", url, headers=headers, data=dumps(req_body))

            # TODO add check_response method for reuse
            # Validate that delete worked
            # Expect status code 200 for deleting data?
            if response.status_code == 200:
                result = loads(response.text)
                print("Deleted {} item(s)".format(result.get('deletedCount')))
            else:
                print('Unable to delete saved data')
                result = response.text

        # Save new data
        if add_timestamp:
            now = get_now()
            data.update({'save_timestamp': str(now)})
            
        action_tag = 'action/insertOne'        
        url = self.base_url.format(action_tag)
        
        req_body = {
            "dataSource": self.cluster_name,
            "database": db_name,
            "collection": cname,
            "document": data
        }

        response = requests.request("POST", url, headers=headers, data=dumps(req_body))
        
        # Validate request result
        # Expect status code 200 for deleting data?
        if response.status_code == 201:
            result = loads(response.text)
        else:
            print('Unable to save data item')
            result = response.text

        return result

    @handle_exception(gen_handler, 'Error saving dataframe remotely:')
    def save_df(self, df, cname, orient='list', meta_tags={}, overwrite=False, add_timestamp=True, validate=False):
        """
        Saves a dataframe to a remote MongoDB server using the Data API.  The 
        dataframe is converted to records.
        
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
        
        result = self.save_data(data, cname, overwrite=overwrite, add_timestamp=add_timestamp)

        if validate:
            
            # Load df to compare against what we saved
            load_df = self.load_df(cname=cname)
            
            try:
                assert_frame_equal(load_df, df)
                print('Dataframes are equivalent')
            except:  # appeantly AssertionError doesn't catch all
                print('Saved dataframe does not match input data')            
            
        return result

    # @handle_exception(gen_handler, 'Error saving remote data:')
    # def save_docs(self, docs, collection, overwrite=False):
    #     """
    #     Generic method for inserting a list of documents (in dictionary record format)
    #     into a remote MongoDb collection.  Each record in the list is
    #     saved a distinct document in collection (unlike nested formats used by other methods)
                                                          
        
    #     Parameters
    #     ----------
    #     docs : list.
    #         List of records (e.g., from converted dataframe) to save remotely.  
    #         Can be incremental or complete set to insert.
    #     collection : collection or name of a collection
    #         Collection where data will be stored.
    #     overwrite : TYPE, optional
    #         DESCRIPTION. The default is True.

    #     Returns
    #     -------
    #     None.

    #     """
        
    #     # TODO this needs some cleanup for better handling of capped vs. non-capped collections and overwrite settings
    #     db = self.db

    #     if db is None:
    #         # TODO Convert to exception
    #         print("No database specified. Unable to save dataframe.")
    #         return None

    #     save_data = docs

    #     if type(collection) is str:
    #         collection = db.get_collection(collection)
            
    #     if overwrite:
    #         # then assume for now that collection is not capped
    #         # TODO add validation check for capped collections
            
    #         # Start a transaction wrapper for overwrites in case we have a failure
    #         with self.client.start_session() as session:
    #             with session.start_transaction():
    #                 if collection.count_documents({}) > 0:
    #                     # drop existing table/collection
    #                     # db.drop_collection(collection, session=session)
    #                     # Clear all existing documents from collection
    #                     collection.delete_many({}, session=session)                    
    #                 res = collection.insert_many(save_data, session=session)
    #     else:
    #         # otherwise, we simply insert the transaction into the collection
    #         with self.client.start_session() as session:
    #             with session.start_transaction():
    #                 res = collection.insert_many(save_data, session=session)

    #     return res

    # @handle_exception(gen_handler, 'Error saving dataframe remotely:')
    # # def save_remote_df(self, df, collection, orient='list', meta_tags={}, overwrite=False, add_timestamp=True):
    # def save_df_as_docs(self, df, collection, meta_tags={}, overwrite=False, add_timestamp=False):
    #     """
    #     Saves a dataframe to a remote MongoDB server.  The dataframe is converted to
    #     records, and each record (i.e., row in the dataframe) corresponds
    #     to a separate document, which allows for saving large dataframes that exceed
    #     the BSON size constraint for single documents, and it allows for
    #     querying subsets of the remote dataset more easily.
        
    #     Parameters
    #     ----------
    #     df : TYPE
    #         DESCRIPTION.
    #     collection : collection or name of a collection
    #         Collection where dataframe will be stored.
    #     meta_tags : dictionary, optional
    #         DESCRIPTION. The default is {}.
    #     overwrite : boolean, optional
    #         Flag to determine whether to clear and replace any existing
    #         documents. The default is True.

    #     Returns
    #     -------
    #     a result set with information about the insert transaction.

    #     """

    #     if add_timestamp:
    #         now = get_now()
    #         # Need to copy if we're adding timestamp
    #         df = df.copy()
    #         df['save_timestamp'] = now
                
    #     # Convert dataframe to records
    #     docs = df.to_dict('records')
        
    #     # Save dataframe as docs
    #     self.save_remote_docs(docs, collection, overwrite=overwrite)
        
    #     return None
    
    # @handle_exception(gen_handler, 'Error saving dataframe remotely as json:')
    # def save_df_as_json(self, df, collection, orient='split', meta_tags={}, overwrite=False, add_timestamp=True):
    #     """
    #     Saves a dataframe to a remote MongoDB server.  The dataframe is converted to
    #     json format using the 'orient' input parameter.
        
    #     Parameters
    #     ----------
    #     df : TYPE
    #         DESCRIPTION.
    #     collection : collection or name of a collection
    #         Collection where dataframe will be stored.
    #     orient : string
    #         Format for the json conversion
    #     meta_tags : TYPE, optional
    #         DESCRIPTION. The default is {}.
    #     overwrite : TYPE, optional
    #         DESCRIPTION. The default is True.

    #     Returns
    #     -------
    #     None.

    #     """
        
    #     # Save dataframe
    #     # data_dict = df.to_dict("records")
    #     jdata = df.to_json(orient=orient)
    #     data = {**meta_tags, **{'orient':orient, "data": jdata}}
        
    #     self.save_remote_data(data, collection, overwrite=overwrite, add_timestamp=add_timestamp)
        
    #     return None
