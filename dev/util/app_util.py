# -*- coding: utf-8 -*-
"""
Created on Sat Feb  6 10:57:03 2021

@author: kknow

Collection of application-level utilities

"""

import os
import math
import json
import pytz
import datetime as dt

# Setting for Heroku environment
# TODO Generalize - consider adding Heroku environment variable
APP_PATH = os.environ.get('APP_PATH', os.getcwd())
# print(type(APP_PATH))
# TODO Move this to config vars
# BASE_TIME_ZONE = 'UTC'
RPT_TIME_ZONE = 'America/New_York'
BASE_TZ = pytz.utc
RPT_TZ = pytz.timezone(RPT_TIME_ZONE)

# Standalone utility method to get the value of a configuration item
# TODO Convert this into a generic configuration utility for broader reuse
def get_config_val(config_data_key, config_data_grp=None):
    fname = "config.json"  # default configuration data file
    env_var_name = config_data_key
    
    # Check if file exists
    file_exists = os.path.isfile(fname)
    if file_exists:
        with open(fname, "r") as jsonfile:
            data = json.load(jsonfile) # Reading the file
            # print("Read successful")
            jsonfile.close()
            if config_data_grp is None:
                config_val = data.get(config_data_key, None)
            else:
                d = data.get(config_data_grp, None)                
                if d is not None:
                    config_val = d.get(config_data_key, None)
    else:
        # If not, check environment config
        # print("File: {} not found".format(fname))
        # print("Checking for configuration variables")
        config_val = os.getenv(env_var_name, None)

    return config_val

def get_now():
    """
    Gets the current datetime relative to UTC.

    Parameters
    ----------

    Returns
    -------
    TYPE
        the current datetime relative to UTC.

    """
    
    # https://api.mongodb.com/python/3.4.0/examples/datetimes.html
    # https://gavinwiener.medium.com/quick-tip-converting-python-datetime-timezones-e94d14676ee9
    now = dt.datetime.utcnow().replace(tzinfo=pytz.utc)

    return now

def convert_utc_to_timezone(utc_dt, to_tz=RPT_TZ):
    """
    Converts a UTC datetime to a different timezone (e.g., 'America/New_York')

    Parameters
    ----------
    dt : datetime
        a valid datetime expressed relative to UTC timezone.
    to_tz : TYPE, optional
        timezone for converting from UTC datetime. The default is RPT_TIME_ZONE, which
        is set as a global configuration parameter (e.g., 'America/New_York').

    Returns
    -------
    TYPE
        datetime converted to specified timezone.

    """
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(to_tz)

# Utility function for flattening multiindex columns
# joins with the join tag, exclude zero-length columns
def flatten_multi_index_columns(df):

    col_names = [ [ col_item for col_item in list(col) if len(col_item) > 0 ] for col in df.columns.values  ]
    # new_cols = ['_'.join(col) if type(col) is tuple else col for col in df.columns.values]
    new_cols = ['_'.join(col) for col in col_names]
    df.columns = new_cols

    return df 

# https://medium.com/@gobbagpete/hi-callum-32289a40fe79
def getColorGradient(fromRGB, toRGB, steps=50):
    """
    colorGradient(fromRGB, toRGB, steps=50)
    Returns a list of <steps> html-style color codes forming a gradient between the two supplied colors
    steps is an optional parameter with a default of 50
    If fromRGB or toRGB is not a valid color code (omitting the initial hash sign is permitted),
    an exception is raised.
    
    Peter Cahill 2020
    """

    # hexRgbRe = re.compile('#?[0–9a-fA-F]{6}') # So we can check format of input html-style colour codes
    # The code will handle upper and lower case hex characters, with or without a # at the front
    # print(not hexRgbRe.match(fromRGB))
    # print(not hexRgbRe.match(toRGB))
    
    # if (not hexRgbRe.match(fromRGB)) | (not hexRgbRe.match(toRGB)):
    #     raise Exception('Invalid parameter format') # One of the inputs isn’t a valid rgb hex code
    
    # Tidy up the parameters
    rgbFrom = fromRGB.split('#')[-1]
    rgbTo = toRGB.split('#')[-1]
    
    # Extract the three RGB fields as integers from each (from and to) parameter
    rFrom, gFrom, bFrom = [(int(rgbFrom[n:n+2], 16)) for n in range(0, len(rgbFrom), 2)]
    rTo, gTo, bTo = [(int(rgbTo[n:n+2], 16)) for n in range(0, len(rgbTo), 2)]
    
    # For each color component, generate the intermediate steps
    rSteps = ['#{0:02x}'.format(round(rFrom + n * (rTo - rFrom) / (steps - 1))) for n in range(steps)]
    gSteps = ['{0:02x}'.format(round(gFrom + n * (gTo - gFrom) / (steps - 1))) for n in range(steps)]
    bSteps = ['{0:02x}'.format(round(bFrom + n * (bTo - bFrom) / (steps - 1))) for n in range(steps)]
    
    # Reassemble the components into a list of html-style #rrggbb codes
    return [r+g+b for r, g, b in zip(rSteps, gSteps, bSteps)]

# Creates a uniformly interpolated color scale from a list of discrete colors
def createUniformColorScale(colors, num_values, reverseScale=True):

    color_scale = []
    for i in range(1, len(colors)):
        n_vals = round(num_values * i/(len(colors)-1) - len(color_scale))
        scale_i = getColorGradient(colors[i-1], colors[i], steps=n_vals)
        color_scale += scale_i

    if reverseScale:
        color_scale.reverse()
        
    fill_colors = { i+1:clr for i,clr in enumerate(color_scale) }

    return fill_colors


# Converts the color list rgb strings into tuples of ints
def get_rgb_tuples(color_list):
        
    rgb_list = [tuple([int(s) for s in color[4:-1].split(",")]) for color in color_list]
                            
    return rgb_list

# # Gets the weights for the interpolation
# def get_color_weights(num_colors_in, num_colors_out):
    
#     c_step = (num_colors_in - 1) / (num_colors_out - 1)
#     weight_list = [ {'x': x, 'low': math.floor(x), 'high': math.ceil(x)} for i in range(0, num_colors_out) for x in [i * c_step] ]

#     # weight_list = [ {'x': x, 'low': math.floor(x), 'high': math.ceil(x)} for x in [i * c_step for i in range(num_colors_out + 1)] ]

#     return weight_list

def get_interpolated_colors(rgb_list, num_colors):
    """
    Get a discrete list of interpolated colors from a list of rgb tuples

    Parameters
    ----------
    rgb_list : int
        list of rgb tuples (e.g., (26, 152, 80).
    num_colors : TYPE
        total number of colors for the sequence.

    Returns
    -------
    colors : TYPE
        DESCRIPTION.

    """
    
    c_step = (len(rgb_list) - 1) / (num_colors - 1)
    colors = []

    for i in range(0, num_colors):
        
        x = i * c_step
        x_lo = math.floor(x)
        x_hi = math.ceil(x)
        dx = x - x_lo
        
        lo_color = rgb_list[x_lo]
        hi_color = rgb_list[x_hi]
        
        r = int(lo_color[0] * (1 - dx) + hi_color[0] * dx)
        g = int(lo_color[1] * (1 - dx) + hi_color[1] * dx)
        b = int(lo_color[2] * (1 - dx) + hi_color[2] * dx)
        
        colors.append('rgb({},{},{})'.format(r, g, b))
        
    return colors

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

# Simple three-color ranker
# TODO Refactor this into a base class for color ranker
class ThreeColorRanker():
    
    def __init__(self, low_color, mid_color, high_color, mid_factor=0.5):
        
        self.low_color = self.get_rgb_tuple(low_color)
        self.mid_color = self.get_rgb_tuple(mid_color)
        self.high_color = self.get_rgb_tuple(high_color)
        self.mid_factor = mid_factor
    
    # Get the RGB tuple from a color string, e.g., 'rgb(165,0,38)'
    def get_rgb_tuple(self, color_str):
        # TODO Add validation of color string input
        return tuple([int(s) for s in color_str[4:-1].split(",")])
        
    # Gets a ranked color for a single input value based on linear interpolation
    def get_ranked_color(self, val, min_val, max_val, reverse=False):
        
        # Check for zero range issue
        # If so, return mid color
        epsilon = 1e-6
        if abs(max_val - min_val) < epsilon:
            r = self.mid_color[0]
            g = self.mid_color[1]
            b = self.mid_color[2]
            return 'rgb({},{},{})'.format(r, g, b)
        
        # Calculate the normalized z value for the input value
        if reverse:
            z_val = 1 - (val - min_val) / (max_val - min_val)
        else:
            z_val = (val - min_val) / (max_val - min_val)
        
        if z_val < self.mid_factor:
            low_color = self.low_color
            high_color = self.mid_color   
            z_low = 0.0
            z_high = self.mid_factor
        else:
            low_color = self.mid_color
            high_color = self.high_color
            z_low = self.mid_factor
            z_high = 1.0

        # Normalize the width of the interpolation interval
        dz = (z_val - z_low) / (z_high - z_low)                       
        r = int(low_color[0] * (1.0 - dz) + high_color[0] * dz)
        g = int(low_color[1] * (1.0 - dz) + high_color[1] * dz)
        b = int(low_color[2] * (1.0 - dz) + high_color[2] * dz)
            
        color = 'rgb({},{},{})'.format(r, g, b)

        return color
        
    # Gets a set of ranked colors for a given list of values
    # input colors should be specified as RGB strings (e.g., 'rgb(165,0,38)')
    # TODO Add validation of input values and range
    # TODO Add default behavior if all input values are the same
    def get_ranked_colors(self, vals, reverse=False):
        
        max_val = max(vals)
        min_val = min(vals)
        
        ranked_colors = [self.get_ranked_color(val, min_val, max_val, reverse) for val in vals]        
        
        return ranked_colors
    
# Simple three-color cut line ranker
# TODO Refactor this into a base class for color ranker
class CutLineColorRanker():
    
    def __init__(self, low_color, mid_color, high_color, cut_line=0):
        
        self.low_color = low_color
        self.mid_color = mid_color
        self.high_color = high_color
        self.cut_line = cut_line
    
    # # Get the RGB tuple from a color string, e.g., 'rgb(165,0,38)'
    # def get_rgb_tuple(self, color_str):
    #     # TODO Add validation of color string input
    #     return tuple([int(s) for s in color_str[4:-1].split(",")])
        
    # Gets a ranked color for a single input value based on linear interpolation
    def get_ranked_color(self, val):
               
        if val > self.cut_line:
            color = self.high_color
        elif val < self.cut_line:
            color = self.low_color
        else:
            color = self.mid_color

        return color
        
    # Gets a set of ranked colors for a given list of values
    # input colors should be specified as RGB strings (e.g., 'rgb(165,0,38)')
    # TODO Add validation of input values and range
    # TODO Add default behavior if all input values are the same
    def get_ranked_colors(self, vals, reverse=False):
        
        ranked_colors = [self.get_ranked_color(val) for val in vals]        
        
        return ranked_colors