# -*- coding: utf-8 -*-
"""
Created on Mon Jul 19 11:56:53 2021

@author: kknow

Collection of utilities for Pandas DataFrames

"""

import os
import pandas as pd

# TODO This is embedded a reuqirement that APP_PATH must be defined
# TODO Consider how to handling app_path without hard-coding dependency
# Consider removing app path from here.  Let calling context handling this.
# from config.app_data import APP_PATH

# TODO Generalize this hack
def is_zip_fname(fname):
    if fname[-3:] == 'zip':
        return True
    return False

# TODO Move to pandas_util
# TODO Organize the file loading and saving utilities
# Utility method for loading a csv file into a dataframe
# KK 1/18/22: Removed app_path prepending
def load_csv_as_df(path, fname, index_col=False):
    """
    Loads a csv file into a dataframe

    Parameters
    ----------
    path : TYPE
        DESCRIPTION.
    fname : TYPE
        DESCRIPTION.
    index_col : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    df : TYPE
        DESCRIPTION.

    """
    # if prepend_app_path:
    #     full_path = os.path.join(APP_PATH, path)
    # else:
    #     full_path = path

    fname = os.path.join(path, fname)
    
    if is_zip_fname(fname):
        df = pd.read_csv(fname, compression='zip', index_col=index_col)
        # df = pd.read_csv(fname, index_col=index_col)
    else: # load csv
        df = pd.read_csv(fname, index_col=index_col)
        
    return df

# TODO Move to pandas_util
# TODO Organize the file loading and saving utilities
# Utility method for saving a dataframe to a local csv file
# KK 1/18/22: Removed app_path prepending
def save_df_to_csv(df, path, fname, index_col=False):
    """
    Saves a dataframe to a local csv file

    Parameters
    ----------
    path : TYPE
        DESCRIPTION.
    fname : TYPE
        DESCRIPTION.
    index_col : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    None

    """
    # if prepend_app_path:
    #     full_path = os.path.join(APP_PATH, local_path)
    # else:
    #     full_path = local_path
    
    if is_zip_fname(fname):
        # save dataframe to zipped csv
        fname_csv = fname[:-3] + 'csv'
        compression_opts = dict(method='zip',
                                archive_name=fname_csv)
        df.to_csv(os.path.join(path, fname), index=index_col, compression=compression_opts)
    else:
        df.to_csv(os.path.join(path, fname), encoding='utf-8', index=index_col)
    
    return df

# Saves a dataframe to a zipped csv file
def save_df_as_csv_zip(df, path, fname_tag, index_col=False):

    # fname_tag = 'covid_death_history_state'
    # path = 'data'
    
    # save dataframe to zipped csv
    fname_zip = '{}.zip'.format(fname_tag)
    fname_csv = '{}.csv'.format(fname_tag)
    compression_opts = dict(method='zip',
                            archive_name=fname_csv)
    df.to_csv(os.path.join(path, fname_zip), index=False, compression=compression_opts)

    return None

# Utility method for merging a list of dfs
def merge_dfs(df_list):
    return pd.concat(df_list, ignore_index=True, sort=False)

# Utlility method for loading and merging a list of dfs stored in csv files
def merge_df_files(fname_list):
    
    # TODO Add error handling and validation of filenames
    dfs = [pd.read_csv(fname) for fname in fname_list]
    merge_df = merge_dfs(dfs)
    
    return merge_df

# TODO Move to pandas_util
# Creates a memory profile for each column of a dataframe
def create_df_mem_profile(df, add_totals=True):
    
    s = df.dtypes
    s.name = 'col_type'
    profile_df = s.to_frame()
    
    profile_df['mem_usage'] = df.memory_usage()
    profile_df.index.name = 'column'
    
    if add_totals:
        profile_df.loc['Total'] = ['dataframe', profile_df['mem_usage'].sum()]        
    
    return profile_df

# https://stackoverflow.com/questions/12680754/split-explode-pandas-dataframe-string-entry-to-separate-rows
def tidy_split(df, column, sep='|', keep=False):
    """
    Split the values of a column and expand so the new DataFrame has one split
    value per row. Filters rows where the column is missing.

    Params
    ------
    df : pandas.DataFrame
        dataframe with the column to split and expand
    column : str
        the column to split and expand
    sep : str
        the string used to split the column's values
    keep : bool
        whether to retain the presplit value as its own row

    Returns
    -------
    pandas.DataFrame
        Returns a dataframe with the same columns as `df`.
    """
    indexes = list()
    new_values = list()
    df = df.dropna(subset=[column])
    for i, presplit in enumerate(df[column].astype(str)):
        values = presplit.split(sep)
        if keep and len(values) > 1:
            indexes.append(i)
            new_values.append(presplit)
        for value in values:
            indexes.append(i)
            new_values.append(value)
    new_df = df.iloc[indexes, :].copy()
    new_df[column] = new_values
    
    return new_df

# TODO Consider consolidating some of these methods into a utilities class

def calc_summary_by_group(data_df, grp_col_configs, agg_col_configs, sort_by=None, gbargs={}):
    '''
    Summarizes and aggregates a dataframe based on grouping and aggregation
    configurations.  The configuration settings can have additional information (e.g,. formatting)
    that are not used by this method.
    
    Example configuration data:
        
        group_col_configs = [
            {'col':'season', 'label':'Season'},
            {'col':'team_owner', 'label':'Owner'},
        ]

        agg_col_configs = [
            {'col':'team_score', 'agg':'sum', 'label':'Projected<br>Points', 'format':'{:,.1f}'},
            {'col':'opp_score', 'agg':'sum', 'label':'Actual<br>Points', 'format':'{:,.1f}'}, 
            {'col':'diff_score', 'agg':'sum', 'label':'Points<br>Above/Below<br>Projection', 'format':'{:,.1f}'},
            {'col':'win', 'agg':'sum', 'label':'Points<br>Above/Below<br>Projection', 'format':'{:,.1f}'},
            {'col':'loss', 'agg':'sum', 'label':'Points<br>Above/Below<br>Projection', 'format':'{:,.1f}'},
            {'col':'game', 'agg':'count', 'label':'Points<br>Above/Below<br>Projection', 'format':'{:,.1f}'},
        ]

    Parameters
    ----------
    data_df : TYPE
        dataframe to group and aggregate.
    grp_col_configs : TYPE
        list of dictionaries of source grouping columns and output labels.
    agg_col_configs : TYPE
        list of dictionaries of source aggregation columns and aggregation methods.  
    sort_by : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    None.

    '''

    # https://pandas.pydata.org/pandas-docs/stable/user_guide/groupby.html#groupby-aggregate-named
    # animals.groupby("kind").agg(
    #      **{
    #          "total weight": pd.NamedAgg(column="weight", aggfunc=sum)
    #      }
    # )

    grp_cols = [d['col'] for d in grp_col_configs]
    gb = data_df.groupby(grp_cols, **gbargs)

    agg_dict = {}
    for d in agg_col_configs:
        
        col = d['col']
        agg = d['agg']
        name = d.get('label', (col,str(agg)))

        agg_dict[name] = pd.NamedAgg(column=col, aggfunc=agg)

    df = gb.agg(**agg_dict)
    
    # # modified to handle multiple aggregations per column
    # # agg_dict = {d['col']:d['agg'] for d in agg_col_configs}
    # agg_dict = {}
    # rename_dict = {}
    # for d in agg_col_configs:
    #     col = d['col']
    #     agg = d['agg']
    #     # print(col)
    #     # print(d['agg'])
    #     # print(agg_dict.get(col, []))
    #     di = agg_dict.get(col, [])
    #     di.append(agg)
    #     agg_dict[col] = di
        
    #     label = d.get('label', None)
    #     if label is not None:
    #         rename_dict[(col,str(agg))] = label

    # grp_cols = [d['col'] for d in grp_col_configs]
    # df = data_df.groupby(grp_cols).agg(agg_dict)
    
    if sort_by is not None:
        df = df.sort_values(by=sort_by, ascending=False)
        
    # # Rename columns
    # print(df.columns.values)
    # print(rename_dict)
    # df = df.rename(columns=rename_dict)
                                  
    return df

def filter_columns(data_df, col_configs, copy_df=True, rename_cols=True):
    '''
    Filter, sort, and rename columns in a dataframe based on a set of col_configs

    Parameters
    ----------
    data_df : TYPE
        DESCRIPTION.
    col_configs : TYPE
        list of column configurations, which each must include 'col' and optionally
        'label' is rename_cols is True.
    copy_df : TYPE, optional
            Optional parameter to copy data_df. The default is True.
    rename_cols : TYPE, optional
        DESCRIPTION. The default is True.

    Returns
    -------
    df : TYPE
        DESCRIPTION.

    '''
    
    df_cols = data_df.columns.values
    cols = [col['col'] for col in col_configs if col['col'] in df_cols]
    df = data_df[cols].copy() if copy_df else data_df[cols]
    if rename_cols:
        col_names = {col['col']: col['label'] for col in col_configs if col.get('label') is not None}
        df = df.rename(columns=col_names)
    
    return df

# Utility function for flattening multiindex columns
# joins with the join tag, exclude zero-length columns
def flatten_multi_index_columns(df):

    col_names = [ [ col_item for col_item in list(col) if len(col_item) > 0 ] for col in df.columns.values  ]
    # new_cols = ['_'.join(col) if type(col) is tuple else col for col in df.columns.values]
    new_cols = ['_'.join(col) for col in col_names]
    df.columns = new_cols

    return df 

# Adds column formats to a dataframe styler
# TODO consider generalizing renamed columns vs. raw columns
def add_column_formats(df_styler, col_configs):
    
    # Formats
    col_formats = {col['label']:col['format'] for col in col_configs if col.get('format', None) is not None}
    df_styler.format(col_formats, na_rep="-")
    
    return df_styler

# Utilities

# Consoliddate multiple files into a single dataframe
# Assumes that files have consistent structures
# TODO Add some error handling
def get_multi_files_as_df(filenames):

    df_all = None
    for fname in filenames:
        df = pd.read_csv(fname, header=[0])
        if df_all is None:
            df_all = df
        else:
            df_all = df_all.append(df, ignore_index=True, sort=False)

    return df_all

# Utility method for displaying a dataframe
def print_df_info(df):
    
    print(df.head())
    print(df.tail())
    print(df.shape)
    
    return None

# Generic utility method to reorder columns
# Usage example
# my_list = df.columns.tolist()
# reordered_cols = reorder_columns(my_list, first_cols=['fourth', 'third'], last_cols=['second'], drop_cols=['fifth'])
# df = df[reordered_cols]
def reorder_columns(columns, first_cols=[], last_cols=[], drop_cols=[]):
    columns = list(set(columns) - set(first_cols))
    columns = list(set(columns) - set(drop_cols))
    columns = list(set(columns) - set(last_cols))
    new_order = first_cols + columns + last_cols
    return new_order

# Convert dataframe into denormalized list
def denormalize_df(df, ref_cols, denorm_cols, denorm_cat_name='category', denorm_val_name='value'):

    '''
    Denormalizes a sparse stats dataframe.  The denormalized list gives more flexibility for
    pivot tables in Excel.

    Parameters
    ----------
    df : DataFrame
        flattened (likely sparse) matrix of data
    ref_cols : list
        list of columns to keep from denormalized stats_df
    denorm_cols : list
        list of columns to denormalize
    denorm_cat_name : string
        name of the output column with the denormalized categories
    denorm_val_name : string
        name of the output column with the denormalized values
    '''
    
    # Create an empty dataframe
    denorm_df = pd.DataFrame()

    # Iterate through columns to denormalize
    for denorm_col in denorm_cols:

        # print(denorm_col)
        # TODO find a better way to do this that doesn't require copy
        newcols = ref_cols.copy()
        newcols.append(denorm_col)
        # print(newcols)

        col_df = df[newcols].dropna(subset=[denorm_col])
        col_df = col_df.rename(columns={denorm_col:denorm_val_name})
        if col_df.shape[0] > 0:
            col_df.insert(len(newcols) - 1, denorm_cat_name, denorm_col) 
            denorm_df = denorm_df.append(col_df, ignore_index=True, sort=False)

    denorm_df.index.name = 'id'

    return denorm_df

# TODO Add validation that columns values are dictionaries
def expand_dict_column(df, col_name, suffix='', prefix='', capitalize_child_labels=False):
    '''
    Expands a column whose values are dictionaries into a set of columns, based
    on the first level keys of the dictionary.
    

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.
    col_name : TYPE
        DESCRIPTION.
    suffix : string
        Optional suffix to apply when expanded columns already exist in dataframe
    capitalize_child_labels : bool
        Optional flag to capitalize column names of embedded children (e.g., "parentChild").
    Returns
    -------
    df : TYPE
        DESCRIPTION.

    '''
    
    if col_name in df.columns.values:
        
        df2 = pd.DataFrame(df[col_name].values.tolist())
        col_names = df2.columns.values
        # TODO Consider moving capitalization flag into expand column configs
        # if capitalize_child_labels:
        #     col_names = [col.capitalize() for col in col_names]
        new_col_names = {col:"{}{}{}".format(prefix, col.capitalize() if capitalize_child_labels else col, suffix) for col in col_names}
        df2.rename(columns=new_col_names, inplace=True)
        
        # df = df.drop(col_name, axis=1).join(df2, rsuffix=suffix)
        df = df.drop(col_name, axis=1).join(df2)
        
    return df

def expand_dict_columns(df, expand_col_configs, capitalize_child_labels=False):
    '''
    Expands dictionary-based columns into multiple columns based on a list
    of column configs. Each column config is a dictionary with the
    following keys: 'col_name', "prefix" "suffix".

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.
    expand_col_configs : TYPE
        DESCRIPTION.

    Returns
    -------
    df : TYPE
        DESCRIPTION.

    '''
    
    dfcols = df.columns.values
    
    # Expand columns
    for d in expand_col_configs:
        col_name = d.get('col_name')

        if col_name in dfcols:
            prefix = d.get('prefix', '')
            suffix = d.get('suffix', '')
            df = expand_dict_column(df, col_name=col_name, suffix=suffix, prefix=prefix, capitalize_child_labels=capitalize_child_labels)

    return df

# Utility class for formatting and styling a dataframe and styling as an HTML table
# TODO Under construction
class TableFormatter():
    """
    Formatting actions include:
        - filtering for a subset of columns
        - renaming columns
        - formatting values
        - setting column alignment
        - adding colors
    """
    
    def __init__(self, df:pd.DataFrame=None, copy_df=True):
        
        if df is None:
            self.df = None
        else:
            self.df = df.copy() if copy_df == True else df
        self.styler = None
        
        return None