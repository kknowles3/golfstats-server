# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 12:03:41 2021

@author: kknow

Layout for tabbed version of team-by-team game summary statistics

*** Under construction ***
This is a remote data implementation of the Masters Pool.  This is designed to
refresh data from the cloud data server in MongoDB.

"""

import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc

from components.layouts import BasePageContent
from components.page import SettingsPanelBuilder
# from components.table import TeamGameStatsTableBuilder, ColConfig, ColType, fmtHyperlink
from components.table import ColType, ColConfig, PoolScoresTableBuilder, fmtMapper
import dash_defer_js_import as dji

from app import app
from dash.dependencies import Input, Output

########## Configuration Data, Parameters and Settings #############

# from components.page import metric_cat_configs, season_configs
from components.data import gel, pel

# team_id_abbrev_dict = game_stats.etsd.team_id_abbrev_dict

###################### Layout #############################

def create_page_header():
    
    page_header = html.H1('Masters Pool 2021 - Live Updates from Cloud Data Server')
    
    return page_header
    
def create_description():
    
    description = dbc.Alert([
        html.H4("Masters Pool 2021 - Live Updates", className='alert-heading'),
        dcc.Markdown(
            """This page shows current scores of the 2021 Masters Pool based on the latest scores, with the ability to
            enable live updates (off by default).\n"""),
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

    gel.refresh_scores()
    status_tag = gel.status_tag
    # TODO Switch this back to golf event update tag (for last time scores were updated)
    last_update = pel.get_last_update_tag()
    
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
        
        # html.Br(),
        # html.Div(
        #     "Projected cut: {}{:.0f}".format("+" if proj_cut > 0 else "", proj_cut),
        #     )

    ])
    
    return tbl_heading
    
def update_scoring_table_body():
    
    # ct = colTypes['string']
    ct = ColType("mapper", fmtMapper(map=pel.id_team_map), "left")
    grp_col_config = ColConfig(label='Team Name', name='team_id', colType=ct)

    # Refresh masters scores
    # scores_df = ege.scores_df
    
    # Get the pool scores
    pool_scores_df = pel.get_pool_scores_df()
    
    # Create the team game stats by tab
    df = pool_scores_df
    df = df.sort_values(by=['Rank', 'TB_Score'])

    df_cut = df[df['MadeCut'] == True]
    # df_out = df[df['MadeCut'] == False]
    
    # Refactored this to give more flexibility in building tables vs. tabs that hold that tables
    pb = PoolScoresTableBuilder()
    metric_cats = ['team_scores', 'player_scores', 'tiebreaker']
    pool_scores_tbl = pb.create_pool_scores_table(df_cut, metric_cats, grp_col_config)
    # out_scores_tbl = pb.create_pool_scores_table(df_out, metric_cats, grp_col_config)

    total_teams = len(df)
    made_cut = len(df_cut)
    # missed_cut = len(df_out)
    
    # https://stackoverflow.com/questions/63793969/making-table-sortable-in-dash-html-table-component
    # https://github.com/White-Tiger/sorttable.js
    # dji_js = dji.Import('tbl-sort-js', src="https://www.kryogenix.org/code/browser/sorttable/sorttable.js")
    dji_js = dji.Import(id='tbl-sort-js', src="https://kenalytics.com/reports/js/sorttable.js")

    body = [
        html.Br(),
        html.H4("At or Inside Cut Line - {:.0f} / {:.0f} Teams ({:.0%})".format(made_cut, total_teams, made_cut/total_teams)),
        html.Div(pool_scores_tbl),
        # html.Br(),
        # html.H4("Outside Cut Line - {:.0f} / {:.0f} Teams ({:.0%}) - ".format(missed_cut, total_teams, missed_cut/total_teams)),
        # html.Div(out_scores_tbl),  
        # html.Div([
        #     html.A(
        #         '999',
        #          style={'fontWeight':'bold',
        #                 'color': 'rgb(178,34,34)'}),
        #     html.A(
        #         ' - Missed Cut, Did Not Play, or Disqualified',
        #          style={'fontWeight':'bold'}
        #          ),
        #     ]),
        html.Article(dji_js),
        ]
    
    return body


# Static class
class MastersPoolRemoteUpdate(BasePageContent):
        
    # Static method
    def createPageContent(params):
    
        # Check whether params is null
        # if (params is None) | (type(params) is not dict) :
            # team_id = None
        # else:
            # Check for team_id parameter
            # team_id = params.get('team_id', None)
    
            # if team_id is None:
                # Check for team-abbrev (easier to remember)
                # team_abbrev = params.get('team_abbrev', None)
                # team_id = game_stats.etsd.team_abbrev_id_dict.get(team_abbrev, None)
        
        # gel.refresh_scores()

        page_header = create_page_header()
        page_description = create_description()
        
        # Instantiate panel builder for building the conference season selector panel
        # pb = PanelBuilder()

        # Testing ability to specify additonal component settings        
        # conf_kwargs = {'placeholder': 'Filter by Conference'}
        # cts_selector = pb.createConfSelector(team_list_df, conf_col='Conference', conf_kwargs=conf_kwargs)
        
        settings_panel = create_settings_panel()
        
        tbl_header = update_scoring_table_header()
        body = update_scoring_table_body()
        
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
            # html.Div([
            #     dcc.Interval(id="progress-interval", n_intervals=0, interval=500),
            #     dbc.Progress(id="progress"),
            #     ]
            #     ),
            dcc.Loading(
            # html.Div(
                id="spd-loading",
                type="default",
                style={'verticalAlign':'top'},
                fullscreen=False,
                children=[
                    html.Div(
                        tbl_header,
                        id='mpl-tbl-header'
                        ),
                    html.Div(
                        body,
                        id='mpl-tbl-body',
                        ),
                    ],
                    ),

            ]
    
        return content
              
#################### Callbacks #################################

# @app.callback(
#     [Output("progress", "value"), Output("progress", "children")],
#     [Input("progress-interval", "n_intervals")],
# )
# def update_progress(n):
#     # check progress of some background process, in this example we'll just
#     # use n_intervals constrained to be in 0-100
#     progress = min(n % 110, 100)
#     # only add text after 5% progress to ensure text isn't squashed too much
#     return progress, f"{progress} %" if progress >= 5 else ""

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
    
    # # report config parameters
    # min_gms = rpt_config.get('min-games', MIN_GAMES)
    # num_rfs = rpt_config.get('num-refs', NumRefsGroup.defaultVal)
    # conf_gm_type = rpt_config.get('conf-game-type', conf_game_type)
    # metric_cats = rpt_config.get('metric-cats', metric_cat_configs)
    # season_list = rpt_config.get('season-list', [d['value'] for d in season_configs])
    
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
@app.callback([Output('mpl-tbl-header', 'children'),
               Output('mpl-tbl-body', 'children')],
              Input('update-component', 'n_intervals'))
def update_scores(n):

    # ege.refresh_scores()
    tbl_header = update_scoring_table_header()
    tbl_body = update_scoring_table_body()
    
    return tbl_header, tbl_body

# # Callback for updating team heading
# @app.callback(
#     # Output('dd-output-container', 'children'),
#     Output('tgst-tabs-heading', 'children'),
#     Input('submit-button-state', 'n_clicks'),
#     [State(component_id='conf-dropdown', component_property='value'),
#     State("std-config-settings", "children")],
#     )
# def update_heading_panel(n_clicks, conf_name, rpt_config):
    
#     team_stats_panel = create_rpt_heading(conf_name, rpt_config)
    
#     return team_stats_panel

# @app.callback(
#     Output('tgst-tabs-body', 'children'),
#     Input('tgst-tabs-heading', 'children'),
#     [State(component_id='conf-dropdown', component_property='value'),
#     State("std-config-settings", "children")],)
# def update_game_stats_body(children, conf_name, rpt_config):
    
#     # # report config parameters
#     # min_gms = rpt_config.get('min-games', MIN_GAMES)
#     # num_rfs = rpt_config.get('num-refs', NumRefsGroup.defaultVal)
#     # conf_gm_type = rpt_config.get('conf-game-type', conf_game_type)
#     metric_cats = rpt_config.get('metric-cats', metric_cat_configs)
#     season_list = rpt_config.get('season-list', [d['value'] for d in season_configs])
    
#     # Configure the fixed grouping column
#     # TODO Add column config definitions for grouping/reference columns
#     # Move to standard configuration data
#     # Using a hyperlink column type here
#     url_base = '/team-ref-stat-tables/?team_abbrev={}'
#     ct = ColType("hyperlink", fmtHyperlink(url_base=url_base), "left")
#     grp_col_config = ColConfig(label='Team', name='TeamAbbrev', colType=ct)

#     # Check selected conference name
#     if conf_name is None:
#         team_results_df = None
#         game_stats_tabs = None
#         dji_js = None
#     else:
#         # Create filtered ref game results data
#         game_results_df = game_stats.gameResults_df
        
#         if conf_name == 'All':
#             team_results_df = game_results_df
#         else:
#             team_results_df = game_results_df[game_results_df['TeamConf'] == conf_name]
        
#         team_results_df = team_results_df[team_results_df['Season'].isin(season_list)]
    
#         # Calculate the summary statistics for the teams
#         game_stats_df = game_stats.calc_team_stats_summary(team_results_df).reset_index()

#         # Create the team game stats by tab
#         df = game_stats_df
#         tab_col = 'ConfGame'
#         tab_vals = ['Conf', 'NonConf', 'Overall']

#         # Refactored this to give more flexibility in building tables vs. tabs that hold that tables
#         tb = TeamGameStatsTableBuilder()
#         game_stats_tbls = [tb.create_game_stats_table(df[df[tab_col] == val], metric_cats, grp_col_config) for val in tab_vals]
#         game_stats_tabs = [tb.create_game_stats_tab(tbl, tab_label) for tbl, tab_label in zip(game_stats_tbls, tab_vals)]  
                                                                                                      
#         # https://stackoverflow.com/questions/63793969/making-table-sortable-in-dash-html-table-component
#         # https://github.com/White-Tiger/sorttable.js
#         # dji_js = dji.Import('tbl-sort-js', src="https://www.kryogenix.org/code/browser/sorttable/sorttable.js")
#         dji_js = dji.Import(id='tbl-sort-js', src="https://kenalytics.com/reports/js/sorttable.js")

#     body = [
#         html.Div(
#             dcc.Tabs(
#                 game_stats_tabs,
#                 mobile_breakpoint=0,
#                 className='gamestat-tabs'
#                 ),
#             className='gamestat-tabs-div pl-0',
#             ),
#         html.Article(dji_js),
#         ]
    
#     return body
