# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 11:46:26 2025

@author: kknow
"""

from dev_util.data_util import DictDataWrapper, DataFrameConvertibleList
from dev_util.pandas_util import expand_dict_columns

class AthleteDataWrapper(DictDataWrapper):
    
    def __init__(self, jdata):
        
        super().__init__(data=jdata)

        
class AthleteListDataWrapper(DataFrameConvertibleList):
    
    def __init__(self, data:list):
        
        super().__init__(data)
        
        self._df_drop_cols = [
            'uid',
            'guid',
            'birthPlace',
            'links'
            ]
        
        self._df_expand_col_configs = [
            {'col_name': 'headshot', 'col_name_map': {'href': 'headshotUrl'}},
            {'col_name': 'flag', 'col_name_map': {'href': 'flagUrl', 'alt': 'countryName'}},
            ]
        
    def _drop_df_cols(self, df, drop_cols=None):

        df_cols = df.columns.values

        drop_cols = self._df_drop_cols if drop_cols is None else drop_cols
        
        if drop_cols is not None:
            drop_cols = [col for col in drop_cols if col in df_cols]
            
            if len(drop_cols) > 0:
                df = df.drop(drop_cols, axis=1)

        return df

    def _expand_df_cols(self, df, expand_col_configs=None):
        
        expand_col_configs = self._df_expand_col_configs if expand_col_configs is None else expand_col_configs
        
        if expand_col_configs is not None:
            df = expand_dict_columns(df, expand_col_configs)
        
        return df
        
    def to_df(self):
        
        df = super().to_df()
        
        # Drop columns
        df = self._drop_df_cols(df)
        
        # Expand columns
        df = self._expand_df_cols(df)
        
        return df
        