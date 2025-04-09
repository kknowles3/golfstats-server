# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 12:03:41 2021

@author: kknow

Live data server page for updating golf event and pool event scores

*** Under construction ***

"""

import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc

from components.layouts import BasePageContent
from components.page import SettingsPanelBuilder
# from components.table import TeamGameStatsTableBuilder, ColConfig, ColType, fmtHyperlink
# from components.table import colTypes, ColConfig, PoolScoresTableBuilder
# import dash_defer_js_import as dji

from app import app
from dash.dependencies import Input, Output, State

########## Configuration Data, Parameters and Settings #############

from components.data import ege, updater

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

def update_scoring_table_header():

    status_tag = ege.status_tag
    last_update = ege.get_last_update_tag()
    
    updater.update_pool_scores(refresh=True, save_remote=True)
    status_tag = ege.status_tag
    last_update = ege.get_last_update_tag()
    
    # logo_url = 'http://www.leaderboard.net.au/_Media/masters_logo_med_hr.jpeg'
    # logo_url = 'https://www.kindpng.com/picc/m/303-3031177_transparent-the-masters-logo-png-2019-masters-golf.png'
    # logo_url = 'https://banner2.cleanpng.com/20180510/syq/kisspng-augusta-national-golf-club-2018-masters-tournament-5af3cde64fc488.8371720915259273983267.jpg'
    logo_url = 'https://a.espncdn.com/i/espn/misc_logos/500/masters_17.png'
    
    # proj_cut = ege.cut_score

    tbl_heading = html.Div([
    
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
                    status_tag,
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

        html.Div(
            "Last update: {}".format(last_update.split(" ", 1)[1]),
            ),
        
    ])
    
    return tbl_heading

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
        update_interval = rpt_config.get("update-freq-input", 30) * 1000
        
        if update_switch_disabled:
            update_txt = 'Live updates are off.'
        else:
            update_txt = 'Live updates are enabled every {:.0f} seconds'.format(update_interval/1000)
            
        return update_txt, update_switch_disabled, update_interval 

# Callback to refresh scores based on update interval
@app.callback([Output('pds-status-tag', 'children'),
               Output('pds-last-update', 'children')],
              Input('update-component', 'n_intervals'),
              State('pds-last-update', 'children'))
def update_scores(n, recent_update_list):

    max_updates = 5 # Number of most recent updates to show
    ege.refresh_scores()
    updater.update_pool_scores(refresh=True, save_remote=True)
    status_tag = ege.status_tag
    last_update = ege.get_last_update_tag()
    
    if recent_update_list is None:
        recent_update_list = [last_update, html.Br()]
    else:
        recent_update_list = [last_update, html.Br()] + recent_update_list[:2*(max_updates - 1)]

    return status_tag, recent_update_list
