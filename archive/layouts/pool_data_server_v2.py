# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 12:03:41 2021

@author: kknow

Live data server page for updating golf event and pool event scores

*** Under construction ***

"""

import dash_bootstrap_components as dbc
from dash import html, dcc

from components.layouts import BasePageContent
from components.page import SettingsPanelBuilder
# from components.table import TeamGameStatsTableBuilder, ColConfig, ColType, fmtHyperlink
# from components.table import colTypes, ColConfig, PoolScoresTableBuilder
# import dash_defer_js_import as dji

from app import app
from dash.dependencies import Input, Output, State
from pymongo import DESCENDING
import datetime as dt
# import pytz

########## Configuration Data, Parameters and Settings #############

from components.data import updater
from dev.util.app_util import convert_utc_to_timezone

###################### Layout #############################

def create_page_header():
    
    page_header = html.H1('Masters Pool 2021 - Live Update Server')
    
    return page_header
    
def create_description():
    
    description = dbc.Alert([
        html.H4("Masters Pool 2021 - Live Update Server", className='alert-heading'),
        dcc.Markdown(
            """This page is the live update server for the 2021 Masters Pool, with the ability to
            enable and disable the live update mechanism (off by default).\n"""),
        html.A("""Click on the """),
        html.A(["Settings ", html.I(className="fa fa-cog")], className="btn-sm btn-primary stretched-link"),
        html.A(" button to configure the live update settings for the page."),

            ],
            color="info", 
            dismissable=True,
            style={'width':'90%'},
            className='mx-auto my-2',
            )
                         
    return description

def create_settings_panel():

    spb = SettingsPanelBuilder()
    
    frm_items = [
        spb.liveUpdateSwitch,
        spb.updateFreqGroup,
        spb.applyButton,
    ]

    frm_items[0].visible = True
    frm_items[1].visible = True
    
    settings_panel = spb.create_settings_panel(frm_items)
    
    return settings_panel

# def update_scoring_table_header():

#     updater.update_pool_scores(refresh=True, save_remote=True)
#     status_tag = updater.ege.status_tag
#     last_update = updater.ege.get_last_update_tag()
    
#     # logo_url = 'http://www.leaderboard.net.au/_Media/masters_logo_med_hr.jpeg'
#     # logo_url = 'https://www.kindpng.com/picc/m/303-3031177_transparent-the-masters-logo-png-2019-masters-golf.png'
#     # logo_url = 'https://banner2.cleanpng.com/20180510/syq/kisspng-augusta-national-golf-club-2018-masters-tournament-5af3cde64fc488.8371720915259273983267.jpg'
#     logo_url = 'https://a.espncdn.com/i/espn/misc_logos/500/masters_17.png'
    
#     # proj_cut = ege.cut_score

#     tbl_heading = html.Div([
    
#         html.Div([
#             html.Img(
#                 src=logo_url,
#                 className='my-auto',
#                 style={'width': '75px',
#                        'height': '75px',
#                        'marginRight': '5px',
#                        'marginLeft': '2px',                           
#                        },
#                 ),
#             html.Div([
#                 html.P(
#                     status_tag,
#                     className='conf-name my-auto',
#                     ),
#                 ],
#                 className='my-auto',
#                  style={'fontWeight': 'bold',
#                        'fontSize': '32px',
#                        # 'verticalAlign': 'center',
#                        'padding': '2px 2px',
#                        },
#                      ),
#                 ],
#             className="row mx-2 mx-auto flex-nowrap my-3",
#             ),

#         html.Div(
#             "Last update: {}".format(last_update.split(" ", 1)[1]),
#             ),
        
#     ])
    
#     return tbl_heading

# # Testing status tag updates from live update server
# # Testing whether we can bypass the standard dash callbacks to do the updates
# def update_status_info():

#     max_updates = 5 # Number of most recent updates to show
#     ege.refresh_scores()
#     updater.update_pool_scores(refresh=True, save_remote=True)
#     status_tag = ege.status_tag
#     last_update = ege.get_last_update_tag()
    
#     if recent_update_list is None:
#         recent_update_list = [last_update, html.Br()]
#     else:
#         recent_update_list = [last_update, html.Br()] + recent_update_list[:2*(max_updates - 1)]

#     return status_tag, recent_update_list

# Static class
class PoolDataServer(BasePageContent):
        
    # Static method
    def createPageContent(params):

        page_header = create_page_header()
        page_description = create_description()
        
        settings_panel = create_settings_panel()
        
        # tbl_header = update_scoring_table_header()
        
        logo_url = 'https://a.espncdn.com/i/espn/misc_logos/500/masters_17.png'

        tbl_header = html.Div([
    
            html.Div([
                html.Img(
                    src=logo_url,
                    className='my-auto',
                    style={'width': '75px',
                           'height': '75px',
                           'marginRight': '5px',
                           'marginLeft': '2px',                           
                           },
                    ),
                html.Div([
                    html.P(
                        # status_tag,
                        id='pds-status-tag',
                        className='conf-name my-auto',
                        ),
                    ],
                    className='my-auto',
                     style={'fontWeight': 'bold',
                           'fontSize': '32px',
                           # 'verticalAlign': 'center',
                           'padding': '2px 2px',
                           },
                         ),
                    ],
                className="row mx-2 mx-auto flex-nowrap my-3",
                ),
    
            # dcc.Loading(
            # # html.Div(
            #     id="spd-loading",
            #     type="default",
            #     style={'verticalAlign':'top'},
            #     fullscreen=False,
            #     children=[
                html.H5(
                    "Recent updates:"
                    ),
                html.Div(
                    # "Last update: {}".format(last_update.split(" ", 1)[1]),
                    id='pds-last-update',
                    ),
                # ]),
            
        ])

        
        content = [

            # Intro
            html.Div([
                page_header,
                page_description,
                ]),

            # Settings
            html.Div([        
                html.Hr(),
                # cts_selector,
                settings_panel,
                ]),
            
            # Updater
            html.Div(
                dcc.Interval(
                    id='update-component',
                    interval=20*1000, # in milliseconds
                    n_intervals=0,
                    disabled=True,
                    )
                ),

            # Report
            html.Div(
                id='mpl-tbl-div',
                className='font-italic'),
            html.Div(
                tbl_header,
                id='mpl-tbl-header'
                ),
            # dcc.Loading(
            # # html.Div(
            #     id="spd-loading",
            #     type="default",
            #     style={'verticalAlign':'top'},
            #     fullscreen=False,
            #     children=[
            #         html.Div(
            #             tbl_header,
            #             id='mpl-tbl-header'
            #             ),
            #         ],
            #         ),

            ]
    
        return content
              
#################### Callbacks #################################

# Callback to toggle status of update frequency
@app.callback(
    Output('update-freq-input', 'disabled'),
    # Input('apply-btn', 'n_clicks'),
    Input("update-switch-input", "value"),
    )
def update_refresh_freq(update_switch_val):
    
    if update_switch_val is None:
        return True
    else:
        update_freq_inp = False if len(update_switch_val) > 0 else True
        
    return update_freq_inp

# Callback to configure live update settings
@app.callback(
    Output('mpl-tbl-div', 'children'),
    Output('update-component', 'disabled'),
    Output('update-component', 'interval'),
    # Input('apply-btn', 'n_clicks'),
    Input("std-config-settings", "children"),
    )
def update_game_stats_body(rpt_config):
    
    if rpt_config is None:
        return None, None, None
    else:
        
        # TODO Pull these defaults out into page default configuration parameters
        update_switch_disabled = False if len(rpt_config.get('update-switch-input', [])) > 0 else True
        update_freq = rpt_config.get("update-freq-input", 30)
        update_interval =  update_freq * 1000
        
        if update_switch_disabled:
            # Stop updates if updater is currently updating
            if updater.is_updating():
                updater.stop()
            update_txt = 'Live updates are off.'
        else:
            # Start updates if updater is not currently updating
            if not updater.is_updating():
                updater.update_freq_secs = update_freq
                updater.start_updates()
            update_txt = 'Live updates are enabled every {:.0f} seconds'.format(update_interval/1000)
            
        return update_txt, update_switch_disabled, update_interval 

# Callback to show the list of recent scoring updates
@app.callback([Output('pds-status-tag', 'children'),
                Output('pds-last-update', 'children')],
              Input('update-component', 'n_intervals'),
              State('pds-last-update', 'children'))
def update_scores(n, recent_update_list):

    # max_updates = 10 # Number of most recent updates to show
    
    find_kwargs = {'projection':{'_id':False, 'last_update':True, 'status_tag':True}, 'sort': [('last_update', DESCENDING)]}
    collection_name = 'pool_score'
    fmt_string = "%m/%d/%y %I:%M:%S %p %Z"
    
    # TODO This page needs a separate rds to avoid interfering with the updates
    recent_updates = updater.rds.load_remote_data_items(collection_name, find_kwargs=find_kwargs)

    if len(recent_updates) > 0:
        status_tag = recent_updates[0].get('status_tag', 'Missing Status Tag')
    else:
        status_tag = 'No updates'
        
    rows = []
    for item in recent_updates:
        update_val = item.get('last_update', 'missing update')
        if type(update_val) is dt.datetime:
            # TODO This should work on herokuapp in UTC local time
            # TODO Fix this for when server is running in non-UTC time
            update_val2 = convert_utc_to_timezone(update_val)
            update_str = update_val2.strftime(fmt_string) # + " " + str(update_val.replace(tzinfo=pytz.utc).tzinfo)
        else:
            update_str = update_val
        
        row = html.Div([
            html.Div(update_str, className='col-3 text-align-left'),
            html.Div(item.get('status_tag', 'missing status tag'), className='col'),
            ],
            className='row'
            )
        rows.append(row)
    
    recent_update_div = html.Div(
        rows,
        className='container-flex'
        )

    return status_tag, recent_update_div
