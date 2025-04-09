# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 08:50:23 2022

@author: kknow

Collection of generic file loading and saving utilities

"""

import os
import json
import pickle

def file_exists(fname, path=''):
    '''
    Check whether a file exists

    Parameters
    ----------
    fname : TYPE
        DESCRIPTION.
    path : TYPE, optional
        DESCRIPTION. The default is ''.

    Returns
    -------
    TYPE
        DESCRIPTION.

    '''    
    return os.path.exists(os.path.join(path, fname))

def load_json_data(fname, path=''):
    '''
    Convenience method for loading a json file

    Parameters
    ----------
    fname : TYPE
        DESCRIPTION.
    path : TYPE, optional
        DESCRIPTION. The default is ''.

    Returns
    -------
    jdata : TYPE
        DESCRIPTION.

    '''

    # TODO Check if file exists
    with open(os.path.join(path, fname), 'r') as f:
        jdata = json.load(f)        

    return jdata
        
def load_text_data(fname, path=''):
    '''
    Convenience method for loading a text file

    Parameters
    ----------
    fname : TYPE
        DESCRIPTION.
    path : TYPE, optional
        DESCRIPTION. The default is ''.

    Returns
    -------
    txtdata : TYPE
        DESCRIPTION.

    '''

    # TODO Check if file exists
    with open(os.path.join(path, fname), 'r') as f:
        txtdata = f.read()

    return txtdata

def save_json_data(jdata, fname, path='', indent=4):
    '''
    Convenience method for saving json data to a file

    Parameters
    ----------
    jdata : TYPE
        DESCRIPTION.
    fname : TYPE
        DESCRIPTION.
    path : TYPE, optional
        DESCRIPTION. The default is ''.
    indent : TYPE, optional
        DESCRIPTION. The default is 4.

    Returns
    -------
    bool
        DESCRIPTION.

    '''
    
    with open(os.path.join(path, fname), 'w') as f:
        json.dump(jdata, f, indent=indent)

    return True

def save_text_data(txtdata, fname, path=''):
    '''
    Convenience method for saving text data to a file

    Parameters
    ----------
    txtdata : TYPE
        DESCRIPTION.
    fname : TYPE
        DESCRIPTION.
    path : TYPE, optional
        DESCRIPTION. The default is ''.

    Returns
    -------
    bool
        DESCRIPTION.

    '''
    
    with open(os.path.join(path, fname), 'w') as f:
        f.write(txtdata)

    return True

# Utility method for loading object from pickle file
def load_file_to_object(fname, path=''):   
    with open(os.path.join(path, fname), 'rb') as input_file:
        obj = pickle.load(input_file)       
    return obj

# Utility method for saving objects to file        
def save_object_to_file(obj, fname, path=''):   
    with open(os.path.join(path, fname), 'wb') as output_file:
        pickle.dump(obj, output_file, pickle.HIGHEST_PROTOCOL)   
    return True

