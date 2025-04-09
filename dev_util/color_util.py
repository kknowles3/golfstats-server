# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 08:57:12 2022

@author: kknow

Collection of color-related utilities and classes

"""

import math

def get_rgb_from_hex(hex_code):
    
    h = hex_code.lstrip('#')
    rgb_code = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    
    return rgb_code

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

# TODO Refactor and clean these up into generic interpolators
class LowColorRanker(ThreeColorRanker):
    
    # Gets a ranked color for a single input value based on looking backward (i.e., low color( interpolation)
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
            color = self.low_color
        else:
            color = self.mid_color

        r = color[0]
        g = color[1]
        b = color[2]
            
        color = 'rgb({},{},{})'.format(r, g, b)

        return color

class HighColorRanker(ThreeColorRanker):
    
    # Gets a ranked color for a single input value based on looking forward (i.e., high color( interpolation)
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
            color = self.mid_color
        else:
            color = self.high_color
                
        # Normalize the width of the interpolation interval
        r = color[0]
        g = color[1]
        b = color[2]
            
        color = 'rgb({},{},{})'.format(r, g, b)

        return color
    