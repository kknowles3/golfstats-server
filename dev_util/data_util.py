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

import abc
from typing import Dict

# # Test for set mapping function
# def f(x):
#     return x

# TODO Add to advanced dictionary class
# TODO Consider a dictionary wrapper class with additional utility methods
def get_nested_item(d, keys):
    '''
    Gets a nested item within a dictionary by traversing a list of keys

    Parameters
    ----------
    d : dict
        DESCRIPTION.
    keys : list
        DESCRIPTION.

    Returns
    -------
    dn : TYPE
        Nested item within dictionary.

    '''
    dn = d
    for key in keys:
        dn = dn.get(key)
        if dn is None:
            # TODO Covert to logger
            # TODO Consider implementing exception
            print("Unable to find key: {} in keys: {}".format(key, ":".join(keys)))
            return None
        
    return dn

def set_nested_item(d, keys, val):
    '''
    Sets a value nested within a dictionary by traversing a list of keys. The
    nesting structure will be created, as needed, if any of the nested keys
    are missing.

    Parameters
    ----------
    d : dict
        DESCRIPTION.
    keys : list
        ordered list of nesting keys.
    val : Type
        Value to set within the nested keys

    Returns
    -------
    dn : TYPE
        Nested item within dictionary.

    '''
    di = d
    
    # loop through n-1 keys
    for key in keys[:-1]:
        dj = di.get(key)
        if dj is None:
            di[key] = {}
            dj = di.get(key)
            di = dj
            
    # Set the nth nested key's value
    dj[keys[-1]] = val
    
    return d

# TODO Rename to get_flattened_dict and add to advanced dictionary wrapper class
def flatten_nested_dict(d:dict, sep=":"):
    '''
    Flattens a dictionary with nested data into one with a single level of
    keys.  Nested keys are concatenated by the "sep" parameter (e.g., "key1:key2:...")

    Parameters
    ----------
    d : dict
        DESCRIPTION.
    sep : TYPE, optional
        DESCRIPTION. The default is ":".

    Returns
    -------
    dflat : TYPE
        DESCRIPTION.

    '''
    
    dflat = {}
    
    for k,v in d.items():
        
        if isinstance(v, dict):
            di = flatten_nested_dict(v)
            for ki,vi in di.items():
                dflat["{}{}{}".format(k, sep, ki)] = vi
        elif isinstance(v, list):
            for i,x in enumerate(v):
                if isinstance(x, dict):
                    xi = flatten_nested_dict(x)
                    for j,xj in xi.items():
                        dflat["{}{}{}{}{}".format(k, sep, i, sep, j)] = xj
                else:
                    dflat["{}{}{}".format(k, sep, i)] = x
        else:
            dflat[k] = v
            
    return dflat

# Base class for dictionary conversion
class DictConvertible(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def to_dict(self, kwargs={})->Dict:
        raise NotImplementedError

# Base class for dataframe conversion
class DataFrameConvertible(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def to_df(self, kwargs={})->pd.DataFrame:
        raise NotImplementedError

# Base class for list conversion
class ListConvertible(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def to_list(self, kwargs={})->list:
        raise NotImplementedError

class ListDataWrapper(ListConvertible):
    
    def __init__(self, data, kwargs={}):
        
        self._data = data
    
    def __iter__(self):
        return iter(self.data)
    
    def __len__(self):
        return len(self.data)

    def _get_data(self):
        return self._data
    
    def __getitem__(self, arg):
        return self.data[arg]
    
    def to_list(self, kwargs={})->list:
        return self.data
    
    # Class Properties
    data = property(fget=_get_data)
    
# TODO Add ListDataWrapper class
class DataFrameConvertibleList(ListDataWrapper, DataFrameConvertible):

    def __init__(self, data:list, kwargs={}):
        
        # super().__init__(d)
        # Dict.__init__(d)
        # self._data = data
        
        super().__init__(data)

    def _get_data(self):
        return self._data
    
    def _get_num_items(self):
        
        data = self.data
        
        if data is None:
            return None
        
        return len(data)

    def to_df(self, **kwargs)->pd.DataFrame:
        return pd.DataFrame(self._data)

    # Class Properties
    data = property(fget=_get_data)
    numItems = property(fget=_get_num_items)

# Base class for wrapped dictionaries
class DictDataWrapper(DictConvertible):

    def __init__(self, data, kwargs={}):
        
        # super().__init__(d)
        # Dict.__init__(d)
        self._data = data
    
    def _get_data(self):
        return self._data

    def _get_item(self, key, item_type, varname, init_params={}):
        
        _item = getattr(self, varname)
        
        if _item is None:
            
            item_data = self.get(key)
            _item = item_type(item_data, **init_params)
            
            setattr(self, varname, _item)
            
        return _item

    def _get_nested_item(self, keys, item_type, varname, init_params={}):
        
        _item = getattr(self, varname)
        
        if _item is None:
            
            item_data = self.get_nested_item(keys=keys)
            _item = item_type(item_data, **init_params)
            
            setattr(self, varname, _item)
            
        return _item
    
    def _get_key_value(self, key, varname):
        '''
        Get a class attribute value that is simply a value
        within the wrapped dictionary data. This approach is
        intended to be used by data elements that are frequently
        accessed, such as standard reference data.

        Parameters
        ----------
        key : TYPE
            DESCRIPTION.
        varname : TYPE
            DESCRIPTION.

        Returns
        -------
        _val : TYPE
            DESCRIPTION.

        '''
        
        _val = getattr(self, varname)
        
        if _val is None:
            _val = self.get(key)
            setattr(self, varname, _val)
            
        return _val

    def _get_nested_key_value(self, keys:list, varname):
        '''
        Get a class attribute value that is simply a nested value
        within the wrapped dictionary data. This approach is
        intended to be used by data elements that are frequently
        accessed, such as standard reference data.

        Parameters
        ----------
        keys : list
            List of nested keys within the class data dict.
        varname : TYPE
            Name of the private member variable for storing the value.

        Returns
        -------
        _val : TYPE
            DESCRIPTION.

        '''
        
        _val = getattr(self, varname)
        
        if _val is None:
            _val = self.get_nested_item(keys)
                
            setattr(self, varname, _val)
            
        return _val

    # TODO Consider refactoring to remove this method
    # Accessor method for getting dictionary data
    def get(self, key_val, default=None):
        return self.data.get(key_val, default)
    
    def get_nested_item(self, keys):
        return get_nested_item(self.data, keys)
    
    def set_nested_item(self, keys, val):
        return set_nested_item(self.data, keys, val)

    def to_dict(self, kwargs={})->Dict:
        return self.data
        
    # Class Properties
    data = property(fget=_get_data)
    
# TODO Consder whether this should be Dict or DictConvertible
# Base class for dataframe-convertible wrapper   
class DataFrameConvertibleDict(DictDataWrapper, DataFrameConvertible):

    def __init__(self, data):
        
        # super().__init__(d)
        # Dict.__init__(d)
        # self._data = data
        super().__init__(data)

    def _get_data(self):
        return self._data
    
    def to_df(self, **kwargs)->pd.DataFrame:
        return pd.DataFrame([self._data])
    
    # Class Properties
    data = property(fget=_get_data)
