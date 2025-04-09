# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 10:04:35 2022

@author: kknow

Collection of markdown, html, and web page utilities for building jupyter notebooks
and reports

"""

import os
import shutil
from IPython.display import display, HTML
import markdown as md
import pandas as pd
import re
import json

import plotly.io as pio
# from pprintpp import pprint
import pprint as ppp


# Utility code for printing inline HTML text

def header(text, size=1):
    raw_html = '<h{}>'.format(size) + str(text) + '</h{}>'.format(size)
    return raw_html

def box(text):
    raw_html = '<div style="border:1px dotted black;padding:2em;">'+str(text)+'</div>'
    return raw_html

# TODO Consider better name for this
def mdtag(label, item, sep=': '):
    '''
    Generates labeled markdown text.  Useful for printing single-line
    variables, with a descriptive label.

    Parameters
    ----------
    label : TYPE
        DESCRIPTION.
    item : TYPE
        DESCRIPTION.
    sep : TYPE
        DESCRIPTION.

    Returns
    -------
    md_txt : TYPE
        DESCRIPTION.

    '''
    md_txt = "**{}**{}{}".format(label, sep, item)
    
    return md_txt

def mdalert(md_txt="", width='90%', alert_type='info'):
    
    # TODO add handling of invalid alert type

    # https://www.w3schools.com/charsets/ref_emoji.asp
    # icon = '&#9432;' # circled information
    # icon = '&#8505;&#65039;' # blue information
    # icon = '&#9989;' # green check box
    alert_icons = {
        'info': '&#128161;', # light bulb
        'success': '&#9989;', # green check box
        'warning': '&#9888;',
        'danger': '&#9940;'  
        }
    
    icon = alert_icons.get(alert_type.lower())
    
    alert_txt = """<div class="alert alert-{} alert-center mx-auto" role="alert" style="width:{}; margin=auto;">
{} 
{}
</div>""".format(alert_type, width, icon, md_txt)

    return alert_txt
    
def mdprint(md_txt):
    display(HTML(md.markdown(md_txt)))
    return None

def mdprint_tag(label, item, sep=': '):
    
    mdprint(mdtag(label, item, sep))
    return None

def mdprint_alert(md_txt, width='90%', alert_type='info'):
    # TODO add handling of invalid alert type

    # # https://www.w3schools.com/charsets/ref_emoji.asp
    # # icon = '&#9432;' # circled information
    # # icon = '&#8505;&#65039;' # blue information
    # # icon = '&#9989;' # green check box
    # alert_icons = {
    #     'info': '&#128161;', # light bulb
    #     'success': '&#9989;', # green check box
    #     'warning': '&#9888;',
    #     'danger': '&#9940;'  
    #     }
    
    # icon = alert_icons.get(alert_type.lower())
    
    # alert_txt = """<div class="alert alert-{} alert-center mx-auto" role="alert" style="width:{}; margin=auto;">
    # {} {}</div>""".format(alert_type, width, icon, md_txt)

    alert_txt = mdalert(md_txt=md_txt, width=width, alert_type=alert_type)
    
    mdprint(alert_txt)
    
    return None

def mdprint_info(md_txt, width='90%'):
    return mdprint_alert(md_txt=md_txt, width=width, alert_type='info')

def mdprint_warning(md_txt, width='90%'):
    return mdprint_alert(md_txt=md_txt, width=width, alert_type='warning')

def mdprint_error(md_txt, width='90%'):
    return mdprint_alert(md_txt=md_txt, width=width, alert_type='danger')

    # icon = '&#9432;' # circled information
    # icon = '&#8505;&#65039;' # blue information
    # icon = '&#9989;' # green check box
    icon = '&#128161;' # light bulb
    
    alert_txt = """<div class="alert alert-info alert-center" role="alert" style="width:{}; margin=auto;">
    {} {}</div>""".format(width, icon, md_txt)
    
    mdprint(alert_txt)
    
    return None

def mdprint_list(lst):

    mdlist = ['<li>{}</li>'.format(i) for i in lst]
    mdtxt = '<ul> ' + "".join(mdlist) + '</ul>'

    mdprint(mdtxt)

    return None

def dfprint(d):
    '''
    Converts a dictionary or list of dictionaries to a 
    dataframe and then displays (i.e., prints) it in a 
    notebook panel.
    
    Parameters
    ----------
    d : dictionary or list of dictionaries
        DESCRIPTION.

    Returns
    -------
    None.

    '''

    df = pd.DataFrame(d)    
    display(df)
    
    return None

def jprint(d, indent=2):
    '''
    Converts a python dictionary to a formatted json string and
    then prints to console.  This is useful when cutting and
    pasting dictionary data across contexts (e.g., paste to swagger input)

    Parameters
    ----------
    d : dict
        python dictionary.
    indent : int, optional
        number of additional spaces to indent child rows. The default is 2.

    Returns
    -------
    None.

    '''
    
    print(json.dumps(d, indent=indent))
    return None

def jstr(d, indent=2):
    '''
    Converts a python dictionary to a formatted json string. This is useful 
    when cutting and pasting dictionary data across contexts
    (e.g., paste to swagger input)

    Parameters
    ----------
    d : dict
        python dictionary.
    indent : int, optional
        number of additional spaces to indent child rows. The default is 2.

    Returns
    -------
    None.

    '''
    
    return json.dumps(d, indent=indent)

def pprint(d, sort_dicts=False):
    
    ppp.PrettyPrinter(sort_dicts=sort_dicts, indent=1, width=80, depth=None, stream=None, compact=False).pprint(d)
    return None
    
# This doesn't belong in a shared utility
# # TODO Refactor to remove the global variable
# def addContent(raw_html):
#     # Example
#     # htmlContent = ''
#     # addContent( header("This is a header") )
#     # addContent( header("This is a header<2>", 2) )
#     # addContent( box("This is some text in a box") )
#     # HTML(htmlContent)

#     global htmlContent
#     htmlContent += raw_html

def displayHeader(text, size=1):    
    display(HTML(header(text, size)))
    
# Utility class for converting jupyter notebooks to html pages
class NbkConverter():
    
    def __init__(self):
        
        self.env_tag = 'NBK_DEV_MODE'
        
        # Default header props
        self.hdr_props = {
            'theme': 'jekyll-theme-cayman',
            'title': 'Fantasy Football Stats',
            'layout': 'notebook',
            'permalink': '/draft-perf-espn-2021/'
        }    

        return None
    
    def convert_notebook(self, path_tag, fname_nbk, fname_rpt):
    
        # Example
        # path_tag = "leagues/ff4m/notebooks/"
        # fname_nbk = "FF4M-In-Season Performance - GM - 2021-Copy2.ipynb"
        # fname_rpt = "FF4M-DraftPerf-TSP-2021.md"

        # Get the current dev mode setting (just in case this coversion process is 
        # persistent or run from notebook)
        dev_mode = os.environ.get(self.env_tag, None)
        
        try:
            # Initialize notebook to Prod Mode
            os.environ[self.env_tag] = 'PROD'
            
            # TODO Add exception handling
            cmd = 'jupyter nbconvert "{}{}" --no-input --to html --output {} --template basic'.format(path_tag, fname_nbk, fname_rpt)
            os.system(cmd)
 
        finally:
            # Reset dev_mode
            if dev_mode is None:
                os.environ.pop(self.env_tag)
            else:
                os.environ[self.env_tag] = dev_mode

        return None
    
    def convert_notebook_to_html(self, path_tag, fname_nbk, fname_out, template='basic', execute_nbk=False):

        # Get the current dev mode setting (just in case this coversion process is 
        # persistent or run from notebook)
        dev_mode = os.environ.get(self.env_tag, None)
        
        try:
            # Initialize notebook to Prod Mode
            os.environ[self.env_tag] = 'PROD'
        
            if execute_nbk:
                cmd = 'jupyter nbconvert "{}{}" --no-input --to html --execute --output {} --template {}'.format(path_tag, fname_nbk, fname_out, template)
            else:
                cmd = 'jupyter nbconvert "{}{}" --no-input --to html --output {} --template {}'.format(path_tag, fname_nbk, fname_out, template)
                
            print(cmd)
            cmd_code = os.system(cmd)
            cmd_tag = 'Success' if cmd_code == 0 else 'Failure'
            print("System command code: {} - {}".format(cmd_code, cmd_tag))

        finally:
            # Reset dev_mode
            if dev_mode is None:
                os.environ.pop(self.env_tag)
            else:
                os.environ[self.env_tag] = dev_mode
    
        return cmd_code

    # Runs the standard conversion to html and then converts to md filename
    def convert_notebook_to_markdown(self, path_tag, fname_nbk, fname_md, template='basic', execute_nbk=False):

        # Convert to html
        cmd_code = self.convert_notebook_to_html(path_tag, fname_nbk, fname_md, template, execute_nbk)
        
        if cmd_code == 0: # Success

            # Convert from html to md
            fname_md = "{}{}".format(path_tag, fname_md)
            self.convert_to_md_extension(fname_md)
            
        else:
            print('Notebook conversion failed.  Unable to continue')
            return None
    
        return cmd_code

    # Streamlined method convert a notebook using configuration data dictionary and copy to remote dest if desired
    def convert_notebook_by_config(self, config_data, template='basic', execute_nbk=False, copy_to_dest=True):
        
        local_path_tag = config_data.get("local_path_tag")
        fname_nbk = config_data.get("fname_nbk")
        fname_out = config_data.get("fname_out")
        output_fmt = config_data.get("output_fmt")
        
        if output_fmt == 'markdown':
            cmd_code = self.convert_notebook_to_markdown(path_tag=local_path_tag, fname_nbk=fname_nbk, fname_md=fname_out, execute_nbk=execute_nbk)
        elif output_fmt == 'html':
            cmd_code = self.convert_notebook_to_html(path_tag=local_path_tag, fname_nbk=fname_nbk, fname_md=fname_out, execute_nbk=execute_nbk)
        else:
            print('Invalid or missing output_fmt: {}. Unable to convert notebook'.format(output_fmt))
            return None
        
        if cmd_code == 0: # Success
        
            if copy_to_dest:            
                dest_path_tag = config_data.get('dest_path_tag')
                if output_fmt == 'markdown':
                    # Prepend the header tags and copy to remote directory
                    hdr_props = config_data.get('hdr_props')
                    self.prepend_header_text(local_path_tag, fname_out, hdr_props)
                self.copy_file(local_path_tag, fname_out, dest_path_tag)
        
        return cmd_code

    def convert_notebook_by_multiconfig(
            self, 
            config_data, 
            template='basic', 
            execute_nbk=False, 
            copy_to_dest=True
            ):
        '''
        Streamlined method convert a notebook and copy to multiple output
        configurations.
        

        Parameters
        ----------
        config_data : TYPE
            DESCRIPTION.
        template : TYPE, optional
            DESCRIPTION. The default is 'basic'.
        execute_nbk : TYPE, optional
            DESCRIPTION. The default is False.
        copy_to_dest : TYPE, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        cmd_code : TYPE
            DESCRIPTION.

        '''
        
        local_path_tag = config_data.get("local_path_tag")
        fname_nbk = config_data.get("fname_nbk")
        fname_base = config_data.get("fname_base")

        cmd_code = self.convert_notebook_to_html(path_tag=local_path_tag, fname_nbk=fname_nbk, fname_out=fname_base, execute_nbk=execute_nbk)
        
        # if output_fmt == 'markdown':
        #     cmd_code = self.convert_notebook_to_markdown(path_tag=local_path_tag, fname_nbk=fname_nbk, fname_md=fname_out, execute_nbk=execute_nbk)
        # elif output_fmt == 'html':
        #     cmd_code = self.convert_notebook_to_html(path_tag=local_path_tag, fname_nbk=fname_nbk, fname_md=fname_out, execute_nbk=execute_nbk)
        
        if cmd_code == 0: # Success
        
            if copy_to_dest:
                
                for config in config_data.get('output_configs'):

                    dest_path_tag = config.get('dest_path_tag')
                    dest_fname_out = config.get('dest_fname_out')
                    fname_in = "{}.html".format(fname_base)
                    self.copy_file(local_path_tag, fname_in, os.path.join(dest_path_tag, dest_fname_out))

                    output_fmt = config_data.get("output_fmt")
                    if output_fmt == 'markdown':
                                        
                        # Prepend the header tags and copy to remote directory
                        hdr_props = config.get('hdr_props')
                        self.prepend_header_text(path_tag=dest_path_tag, fname_md=dest_fname_out, hdr_props=hdr_props)
        
        return cmd_code
    
    # Converts (i.e., renames) an existing file to a markdown (i.e., md) extension
    # Replaces input file and overwrites existing file, if it exists
    def convert_to_md_extension(self, fname_md):
        shutil.move(fname_md + '.html', fname_md)
    
    # Prepends the jekyll header text into a markdown file
    # TODO Convert to input property dictionary
    # TODO Generalize this to handle arbirtray tags
    def prepend_header_text(self, path_tag, fname_md, hdr_props):

        header_txt = """---
theme: {}
title: {}
layout: {}
permalink: {}
---

""".format(hdr_props['theme'], 
           hdr_props['title'],
           hdr_props['layout'],
           hdr_props['permalink'],
          )

        path_fname_md = os.path.join(path_tag, fname_md)

        with open(path_fname_md, 'r') as original: data = original.read()
        with open(path_fname_md, 'w') as modified: modified.write(header_txt + data)

    def copy_file(self, local_path_tag, fname_md, dst_path_tag):
        # Copy new file to another directory
        src = os.path.join(local_path_tag, fname_md)
    #     dst = "C:/Users/kknow/OneDrive/Documents/Analytics/dev/reports/_pages"
        newPath = shutil.copy(src, dst_path_tag)
        
        return newPath

class NbkDevViewer():
    '''
    Class for viewing and printing notebook information while developing the notebook.
    In general, the methods of this class as intended to display information while
    the notebook is used in interactive (i.e., "DEV" mode), but are not displayed
    as output when the notebook is converted to a report.
    '''
    
    def __init__(self, nbk_dev_mode=None):
        
        if nbk_dev_mode is None:
            # TODO Consider how to generalizet these setting assumptions
            self.NBK_DEV_MODE = os.environ.get('NBK_DEV_MODE', None)
            if (self.NBK_DEV_MODE is None):
            #     print("NBK_DEV_MODE not set...initializing as DEV")
                self.NBK_DEV_MODE = "DEV"
        else:
            self.NBK_DEV_MODE = nbk_dev_mode

        # print("NBK_DEV_MODE: {}".format(self.NBK_DEV_MODE))

        return None        

    # TODO Use an annotation tag here to minimize the duplicate coding for each method.
    def display(self, df, nbk_dev_mode=None):

        nbk_dev_mode = self.NBK_DEV_MODE if nbk_dev_mode is None else nbk_dev_mode
        
        if nbk_dev_mode == 'DEV':
            
            display(df)
            
        return None
    
    def print(self, df, nbk_dev_mode=None):

        nbk_dev_mode = self.NBK_DEV_MODE if nbk_dev_mode is None else nbk_dev_mode
        
        if nbk_dev_mode == 'DEV':
            
            print(df)
            
        return None

    def mdprint(self, mdtxt, nbk_dev_mode=None):

        nbk_dev_mode = self.NBK_DEV_MODE if nbk_dev_mode is None else nbk_dev_mode
        
        if nbk_dev_mode == 'DEV':
            
            mdprint(mdtxt)
            
        return None
    
    def pprint(self, mdtxt, nbk_dev_mode=None, sort_dicts=False):

        nbk_dev_mode = self.NBK_DEV_MODE if nbk_dev_mode is None else nbk_dev_mode
        
        if nbk_dev_mode == 'DEV':
            
            pprint(mdtxt, sort_dicts=sort_dicts)
            
        return None
                
# TODO Consider a more generalized NbkViewer
# Utility class for displaying plotly figures in notebooks
class NbkFigViewer(NbkDevViewer):
    
    # Wrapper function for showing figure in notebook
    # This addresses a plotly issue when converting notebook to HTML
    def showFig(self, fig, nbk_dev_mode=None):

        nbk_dev_mode = self.NBK_DEV_MODE if nbk_dev_mode is None else nbk_dev_mode

        # Disable axis zooming
        #     fig.update_xaxes(fixedrange=True)
        #     fig.update_yaxes(fixedrange=True)
    
        config = {
            'scrollZoom': False,
            'displayModeBar': False,
            }
    
        if nbk_dev_mode == 'DEV': # Show figure in notebook if in DEV mode
    #         pio.show(fig, config=config)
    #         print("{% raw %}")
            fig.show()
    #         print("% endraw %")
        else: # Generate output for nbconvert  
            # Note: this is wrapped in raw tags to prevent liquid parsing errors
    #         display(HTML("{% raw %}" + pio.to_html(fig, include_plotlyjs=False, full_html=False, config=config) + "{% endraw %}")) 
            display(HTML("{% raw %}" + pio.to_html(fig, include_plotlyjs=False, full_html=False, config=config) + "{% endraw %}")) 

    def get_fig_html(self, fig):
           
    #     fig.update_xaxes(fixedrange=True)
    #     fig.update_yaxes(fixedrange=True)
        
        config = {'scrollZoom': False,
                  'displayModeBar': False,
                 }
    
        # The "{% raw %}" tags are required to prevent a plotly js parsing issue in jekyll and liquid
        fig_html_str = "{% raw %}" + pio.to_html(fig, include_plotlyjs=False, full_html=False, config=config) + "{% endraw %}"
        
        return fig_html_str
    
    def get_fig_div(self, fig, fig_id=0, min_width='550px', max_width='1000px'):
        
        plot_div_str = '<div id="plotDiv{}" class="container-fluid px-0 plotDiv col-6" style="min-width: {}; max-width: {};">'.format(fig_id, min_width, max_width)
        plot_div_str += self.get_fig_html(fig)
        plot_div_str += "</div>"

        return plot_div_str
    
    def show_fig_div(self, fig, fig_id=0, min_width='550px', max_width='1000px'):
        """
        Wrapper to create and show a figure within a plot div
        Adjusted for in-notebook vs. web page
        Sizing parameters are ignored within notebook      

        Parameters
        ----------
        fig : TYPE
            DESCRIPTION.
        min_width : TYPE, optional
            DESCRIPTION. The default is '550px'.
        max_width : TYPE, optional
            DESCRIPTION. The default is '1000px'.

        Returns
        -------
        None.

        """
        
        if self.NBK_DEV_MODE == 'DEV': # Show figure in notebook if in DEV mode
            
            fig.show()
            
        else: # Generate output for nbconvert  
    
            plot_div_str = '<div id="pltGrp0" class="container-fluid px-0">'
            plot_div_str += self.get_fig_div(fig, fig_id=fig_id, min_width=min_width, max_width=max_width)
            plot_div_str += "</div>"
            
            display(HTML(plot_div_str))
        
        return None
    
    def show_fig_divs(self, figs, grp_id=0, min_width='550px', max_width='1000px'):
        """
        Wrapper to create and show a list of figures within a plot group div
        Adjusted for in-notebook vs. web page
        Sizing parameters are ignored within notebook

        Parameters
        ----------
        figs : TYPE
            DESCRIPTION.
        min_width : TYPE, optional
            DESCRIPTION. The default is '550px'.
        max_width : TYPE, optional
            DESCRIPTION. The default is '1000px'.

        Returns
        -------
        None.

        """
        
        if self.NBK_DEV_MODE == 'DEV': # Show each figure in notebook if in DEV mode

            for fig in figs:
                fig.show()

        else: # Generate output for nbconvert  

            # TODO Pull out configuration parameters for id, class and style    
            plot_divs_str = '<div id="pltGrp{}" class="container-fluid px-0">'.format(grp_id)
            
            for i, fig in enumerate(figs):
                plot_divs_str += self.get_fig_div(fig, fig_id=i, min_width=min_width, max_width=max_width)

            plot_divs_str += "</div>"
            
            display(HTML(plot_divs_str))
        
        return None

# Adapted from FFStats-dev project    
class NbkReporter():

    def __init__(self):
        self.tbl_class = 'dataframe topn-tbl'

    def add_rank_cols(self, df, val_cols, rnk_tag='_rnk', ascending=True, method='min'):
        
        for col in val_cols:
            df[col + rnk_tag] = df[col].rank(ascending=ascending, method=method)
            
        return df
    
    def add_pct_of_total(self, df, val_cols, tot_col='Total'):
    
        pct_tag = '_pct'
        
        for col in val_cols:
            df[col + pct_tag] = df[col]/df[tot_col]
            
        return df
        
    def calc_pivot_view(self, df, idx_cols, col_cols, val_col, add_total_col=True, total_col_name='Total'):
        
        # Pivot the team totals
        pivot_df = df.pivot(index=idx_cols, columns=col_cols, values=val_col)

        # Combine Totals and Roster Source details
        
        # pvt_val_cols = pivot_df.columns.values
        
        # Add total for each row
        if add_total_col:
            pivot_df[total_col_name] = pivot_df.sum(axis=1)
            # pivot_df = self.add_pct_of_total(pivot_df, pvt_val_cols, tot_col=total_col_name, add_total_row=False)
        # if add_ranks:
        #     pivot_df = self.add_rank_cols(pivot_df, pvt_val_cols)

        return pivot_df
        
    def calc_summary_by_group(self, df, grp_col_configs, agg_col_configs, sort_col=None):

        # Example
        # agg_col_configs = [
        #     {'col':'projected_points', 'aggfunc':'mean', 'label':'Projected<br>Points', 'format':'{:,.1f}'},
        #     {'col':'actual_points', 'aggfunc':'mean', 'label':'Actual<br>Points', 'format':'{:,.1f}'},
        #     {'col':'diff_points', 'aggfunc':'mean', 'label':'Points<br>Above/Below<br>Projection', 'format':'{:,.1f}'},
        #     {'col':'diff_points2', 'aggfunc':'std', 'label':'Standard<br>Deviation', 'format':'{:,.1f}'}
        #     ]
        
        grp_col_configs = grp_col_configs if isinstance(grp_col_configs, list) else [grp_col_configs]

        grp_cols = [d['col'] for d in grp_col_configs if d.get('col') is not None]
        # print(grp_cols)
        
        # TODO Add error handling if entries are missing
        # 'team_act_tot': pd.NamedAgg(column='actual', aggfunc='sum')
        agg_dict = {d['label']:pd.NamedAgg(column=d['col'], aggfunc=d['aggfunc']) for d in agg_col_configs if (None not in [d.get('col'), d.get('aggfunc'), d.get('label')])}
        # print(agg_dict)
        
        df = df.groupby(grp_cols).agg(**agg_dict)
        # print(df)
        
        if sort_col is not None:
            df = df.sort_values(by=sort_col, ascending=False)
                                      
        return df
    
    # TODO Move this non-generic method elsewhere
    def calc_team_totals(self, player_totals_df, grp_col_configs=None, agg_col_configs=None, sort_cols=['team_id']):
        '''
        Calculates the season totals by team.

        Parameters
        ----------
        player_totals_df : TYPE
            DESCRIPTION.

        Returns
        -------
        team_tot_df : TYPE
            DESCRIPTION.

        '''

        if grp_col_configs is None:
            grp_col_configs = [
                {'col': 'team_id'}, 
                {'col': 'owner_name'},
                ]

        if agg_col_configs is None:
            agg_col_configs = [
                {'col':'act_pts_tot', 'aggfunc':'sum', 'label':'act_pts_tot', 'format':'{:,.1f}', 'bg_color':{'cmap':self.cm}},
                {'col':'act_pts_avg', 'aggfunc':'sum', 'label':'act_pts_tot', 'format':'{:,.1f}', 'bg_color':{'cmap':self.cm}},
                {'col':'st_act_pts_tot', 'aggfunc':'sum', 'label':'st_act_pts_tot', 'format':'{:,.1f}', 'bg_color':{'cmap':self.cm}},
                {'col':'st_act_pts_avg', 'aggfunc':'sum', 'label':'st_act_pts_tot', 'format':'{:,.1f}', 'bg_color':{'cmap':self.cm}},
                ]
        
        sort_cols = ['team_id']
        
        # Calc starter season totals
        team_tot_df = self.calc_summary_by_group(
            player_totals_df, 
            grp_col_configs=grp_col_configs, 
            agg_col_configs=agg_col_configs, 
            sort_col=[d['col'] for d in grp_col_configs]
        ).reset_index()
        
        team_tot_df = team_tot_df.sort_values(by=sort_cols)
    
        return team_tot_df
    
    def add_background_gradient(self, tbl, color_cols, cmap, vmax_val=None, vmin_val=None):
        
        tbl.background_gradient(cmap=cmap, subset=color_cols, vmax=vmax_val, vmin=vmin_val)
        
        return tbl
    
    # TODO Consider adding a color min/max class that we can use for getting mins and maxes
    def add_bg_color_minmax(self, df:pd.DataFrame, col_name, bg_color_config:dict):
        
        col_bg = bg_color_config.copy()
    
        # Set the min/max vals if not already set
        if col_bg.get('vmax') is None:
            col_bg['vmax'] = df[col_name].max() 
        if col_bg.get('vmin') is None:
            col_bg['vmin'] = df[col_name].min() 

        return col_bg

    def rename_columns(self, df, col_configs):

        col_names = {col['col']:col['label'] for col in col_configs if col.get('label') is not None}
        # print(col_names)
        df = df.rename(columns=col_names)
        
        return df
        
    # Filters, orders, and renames columns in a dataframe based on col_configs
    # Optional parameter to copy df, default = True.
    def filterColumns(self, df, col_configs, copy_df=True):
        
        df_cols = list(df.columns.values)
        # cols = []
        # for d in col_configs:
        #     col = d.get('col')
        #     if col in df_cols:
        #         cols.append(col)
        cols = [d['col'] for d in col_configs if d['col'] in df_cols]
        # print(cols)
        df2 = df[cols].copy() if copy_df else df[cols]
        
        return df2

    # Adds column formats to a dataframe styler
    # TODO consider generalizing renamed columns vs. raw columns
    # TODO Add support for additional formatters
    def addColumnFormats(self, tbl, col_configs):
        
        # Formats
        col_formats = {col['label']:col['format'] for col in col_configs if col.get('format', None) is not None}
        tbl.format(col_formats)
        
        return tbl
    
    # Adds the sticky-col class using regex approach
    # TODO find a cleaner approach
    def add_fixed_col(self, tbl, col_num):
        '''
        Converts a dataframe styler into a table string and inserts a
        fixed column style tag for the input column number.

        Parameters
        ----------
        tbl : TYPE
            DESCRIPTION.
        col_num : TYPE
            DESCRIPTION.

        Returns
        -------
        tbl_str : TYPE
            DESCRIPTION.

        '''
        pattern = re.compile(r'( col[{}])\b'.format(col_num))
        tbl_str = pattern.sub(" col{} sticky-col".format(col_num), tbl.to_html())
        return tbl_str

    # TODO Consider cleaner way to use bg_color_df
    def get_table_styled(self, df, col_configs, bg_color_df=None, filter_columns=True):

        bg_color_df = df if bg_color_df is None else bg_color_df

        tbl_df = df
        
        # Filter columns
        if filter_columns:
            tbl_df = self.filterColumns(df, col_configs)
                
        # TODO This needs to be refactored to work with multiindex dfs
        # Rename columns
        tbl_df = self.rename_columns(tbl_df, col_configs)
        
        # Filter the col_configs for columns in df
        # rpt_col_configs = [d for d in col_configs if d.get('col') in tbl_df.columns.values]
        
        rpt_col_configs = []
        col_vals = list(tbl_df.columns.values)
        for d in col_configs:
            if d.get('label') in col_vals:
                rpt_col_configs.append(d)

        tbl = (tbl_df.style
                .hide(axis='index')
                .set_table_attributes('class="{}"'.format(self.tbl_class))
                .set_table_styles([{'selector':'th', 'props':[('text-align', 'center')]}])
              )        
        
        # Add the column alignments
        for config in rpt_col_configs:
            col_name = config.get('col')
            col_label = config.get('label')

            # Add the column alignments
            col_align = config.get('align')
            if col_align is not None:
                tbl.set_properties(**{'text-align': col_align}, subset=[col_label])

            # Add the background gradients
            col_bg = config.get('bg_color')                                
            if col_bg is not None:
                col_bg = self.add_bg_color_minmax(bg_color_df, col_name, col_bg)
                tbl.background_gradient(**col_bg, subset=[col_label])
        
        tbl = self.addColumnFormats(tbl, rpt_col_configs)
        
        # KK 1/24/22: Pulled this out to preserve the styler object for downstream mods
        # tbl_str = self.add_fixed_col(tbl, 0)
    
        return tbl
