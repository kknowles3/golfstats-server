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

# Base class for wrapped dictionaries
class DictDataWrapper():

    def __init__(self, data, kwargs={}):
        
        # super().__init__(d)
        # Dict.__init__(d)
        self._data = data
    
    def _get_data(self):
        return self._data

    def _get_item(self, key, item_type, varname):
        
        _item = getattr(self, varname)
        
        if _item is None:
            
            item_data = self.get(key)
            _item = item_type(item_data)
            
            setattr(self, varname, _item)
            
        return _item
    
    # TODO Consdier refactoring to remove this method
    # Accessor method for getting dictionary data
    def get(self, key_val):
        return self.data.get(key_val)
    
    # Class Properties
    data = property(fget=_get_data)

# TODO Consder whether this should be Dict or DictConvertible
# Base class for dataframe-convertible wrapper   
class BaseDataFrameConvertible(DictDataWrapper, DataFrameConvertible):

    def __init__(self, data):
        
        # super().__init__(d)
        # Dict.__init__(d)
        # self._data = data
        super().__init__(data)

    def _get_data(self):
        return self._data
    
    def to_df(self, **kwargs)->pd.DataFrame:
        return pd.DataFrame(self._data)
    
    # Class Properties
    data = property(fget=_get_data)
