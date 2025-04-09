# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 10:56:29 2021

@author: kknow
"""

# import dash_html_components as html
import dash_bootstrap_components as dbc
# import dash_core_components as dcc
from dash import html, dcc

from app import app
from dash.dependencies import Input, Output, State

from typing import List

SITE_TITLE = "GolfStats Data Server"

# import dash_core_components as dcc

# TODO Review this code structure.
# Consider implementing page builder class
# Consider ways to streamline nested components

################## Page Utilities #############################

# Gets a set of parameters from a url string
# https://stackoverflow.com/questions/5074803/retrieving-parameters-from-a-url
def getParams(url_search):
    
    if url_search.startswith("?"):
    
        params = url_search.split("?")[1]
        params = params.split('=')
        pairs = zip(params[0::2], params[1::2])
        answer = dict((k,v) for k,v in pairs)
    
    else:
        print('Unable to extract parameters from url search string {}'.format(url_search))
        return None
    
    return answer

################# Shared Components ###########################

def get_banner():

    banner = html.Section(
        id="banner", 
        className="py-5 d-none d-sm-block",
        children=html.Div(
            className="primary-overlay text-white my-auto",
            children = html.Div(
                className='container my-auto',
                children = html.Div(
                    className='row my-auto',
                    children = html.Div(
                        className = "col-md-6 text-center my-auto",
                        children = html.H1(
                            className=" display-3 py-4 bannertext text-nowrap my-auto",
                            style={'textAlign': 'center',
                                   'color': 'white',
                                   # 'fontWeight': 'bold',
                                   },
                            children = SITE_TITLE,
                            )
                        )
                    )
                )
            )
        )

    return banner
    
# This is based on dbc NavbarSimple component
# https://dash-bootstrap-components.opensource.faculty.ai/docs/components/navbar/#
def get_navbar_simple():

    # LOGO = "/assets/img/logo.png"

    def menu_label(icon_class, txt):
        return html.A([html.I(className=icon_class),txt])
    
    def menu_item(icon_class, txt, href):
        return dbc.DropdownMenuItem(menu_label(icon_class, txt), href=href)
    
    def new_menu_label(icon_class, txt):
        return html.A([html.I(className=icon_class),txt + " ", html.Span("New", className='badge badge-primary text-right')])

    def new_menu_item(icon_class, txt, href):
        return dbc.DropdownMenuItem(new_menu_label(icon_class, txt), href=href)
    
    navbar = dbc.NavbarSimple(
        children=[
            # dbc.Col(html.Img(src=LOGO, height="30px"), align='left', className='py-2', style={'float':'left'}),
            # dbc.NavItem(dbc.NavLink("Page 1", href="#")),

            # dbc.DropdownMenu(
            #     children=[
            #         dbc.DropdownMenuItem("Top/Bottom Ranking", header=True),
            #         # dbc.DropdownMenuItem(html.A([html.I(className="fa fa-table")," Team Ref Lists"]), href="/team-ref-lists/"),
            #         # dbc.DropdownMenuItem(menu_label("fa fa-table", " Team Ref Lists"), href="/team-ref-lists/"),
            #         # dbc.DropdownMenuItem("Team Ref Cards", href="/team-ref-cards/"),
            #         menu_item("fa fa-id-card", " Top/Bottom Ref Cards by Team", "/team-ref-cards/"),
            #         menu_item("fa fa-table", " Top/Bottom Ref Stat Lists by Team", "/team-ref-stat-lists/"),
            #         new_menu_item("fa fa-table", " Top/Bottom Team Stat Ranking Lists", "/team-stat-rank-lists/"),
            #         dbc.DropdownMenuItem("Summary Stats", header=True),
            #         new_menu_item("fa fa-table", " Team Ref Stats Grid", "/team-ref-stat-tables/"),
            #         new_menu_item("fa fa-table", " Multi-Team Summary Stats", "/team-game-stat-tables/"),
            #     ],
            #     nav=True,
            #     in_navbar=True,
            #     label="Teams",
            #     style={"zIndex":10},
            # ),
            
            # dbc.DropdownMenu(
            #     children=[
            #         dbc.DropdownMenuItem("Game Reports", header=True),
            #         # dbc.DropdownMenuItem("Game Referees", href="/team-game-list/"),
            #         menu_item("far fa-file-image", " Team Game Lists", "/team-game-list/"),
            #         menu_item("fa fa-table", " Conference Game Lists", "/conf-game-list/"),
            #     ],
            #     nav=True,
            #     in_navbar=True,
            #     label="Games",
            #     style={"zIndex":10},
            # ),
            
            # dbc.DropdownMenu(
            #     children=[
            #         dbc.DropdownMenuItem("Conference Reports", header=True),
            #         # dbc.DropdownMenuItem("Ref Stats by Team", href="/conf-ref-stats/"),
            #         menu_item("fa fa-table", " Ref Stats by Team", "/conf-ref-stats/"),
                    
            #         dbc.DropdownMenuItem("Odds Reports", header=True),
            #         # dbc.DropdownMenuItem("Spread Results", href="/spd-results/"),
            #         # dbc.DropdownMenuItem("Over-Under Results", href="/ou-results/"),
            #         menu_item("fa fa-chart-area", " Spread Results", "/conf-spd-results/"),
            #         menu_item("fa fa-chart-area", " Over-Under Results", "/conf-ou-results/"),
            #     ],
            #     nav=True,
            #     in_navbar=True,
            #     label="Conferences",
            #     style={"zIndex":100},
            # ),

            # dbc.DropdownMenu(
            #     children=[
            #         dbc.DropdownMenuItem("More", header=True),
            #         # dbc.DropdownMenuItem("About", href="/about/"),
            #         menu_item("fa fa-info-circle", " About", "/about/"),
            #     ],
            #     nav=True,
            #     in_navbar=True,
            #     label="About",
            #     style={"zIndex":10},
            # ),
            
        ],
        brand="GolfStats - Server",
        brand_href="/",
        brand_style={
            'color': '#0275d8',
            'fontWeight':'bold',
            # 'content': 'url("/assets/img/logo.png")',
            'width': 'auto',
            'height': '40px',
            # 'margin-top': '35px',
            # 'margin-bottom': '65px',
            'backgroundImage': 'url(/assets/img/logo.png)',
            'backgroundRepeat': 'no-repeat',
            'backgroundPosition': 'left center',
            'backgroundSize': '30px',
            'paddingLeft': '40px',
            },
        color="info",
        light=True,
        # className="navbar-expand-sm bg-light navbar-light sticky-top text-primary py-1",
        className="navbar-expand-md bg-light navbar-light text-primary py-1",
        style={'zIndex': 1000},
        fluid=True,
        sticky=True,
    )
    
    return navbar

# https://towardsdatascience.com/create-a-professional-dasbhoard-with-dash-and-css-bootstrap-e1829e238fc5
def Header(addMenu=True):
    lst = [
            get_banner(),
            html.Div(
                get_navbar_simple(),
                className='row sticky-top'
                ),
            # get_navbar(),
            html.Br([]),
            ]
    
    # if addMenu:
    #     lst.append(get_menu())
        
    return html.Div(lst)

def Footer():
    
    footer = html.Footer(
        className="page-footer font-small blue",
        children = [
            html.Div(
                className="footer-copyright text-center py-5",
                children= [
                    "Copyright © 2021:",
                    html.A(
                        href="https://kenalytics.com/",
                        children=" Kenalytics.com"),
                    html.Br(),
                    "All Rights Reserved.",
                    html.Br(),
                    html.A(
                        href="mailto:admin@kenalytics.com?subject=Feedback%20on%20{}%20Site".format(SITE_TITLE),
                        children=[
                            html.I(className="fas fa-envelope"),
                            " Contact Us"
                            ]
                        ),
                    ]),
            ],
        )
    
    return footer

###################### Panel Builder ###############################

# Utility class for creating reusable panel components
class PanelBuilder():
    
    def __init__(self):
        ...

    # Creates a heading with a logo image
    # TODO Consider where these utilities should go
    def create_logo_heading(self, logo_url, heading_txt):
        
        logo_heading = html.Div([
            
            # TODO Add team logo
            # html.Img(src=logo_url, width=100),
            # html.H3("{}".format(team_name)),
    
            html.Div([
                html.Img(
                    src=logo_url,
                    className='my-auto',
                    style={'width': '100px',
                           # 'height': '75px',
                           'marginRight': '5px',
                           'marginLeft': '2px',                           
                           },
                    ),
                html.Div([
                    html.P(
                        heading_txt,
                        className='conf-name my-auto',
                        ),
                    # html.P(
                    #     team_abbrev,
                    #     className='conf-abbrev',
                    #     ),
                    ],
                    className='my-auto',
                     style={'fontWeight': 'bold',
                           'fontSize': '40px',
                           # 'verticalAlign': 'center',
                           'padding': '2px 2px',
                           },
                         ),
                    ],
                className="row mx-2 mx-auto flex-nowrap my-auto",
                # style={'paddingLeft': '25px'}
                ),
    
            ])

        return logo_heading
        
    # def create_conf_dropdown(
    #         self, results_df, conf_name=None, id='conf-dropdown', 
    #         className='conf-dropdown', conf_col='Conference', dropdown_style=None, 
    #         placeholder_text='Select a conference', add_all_conf_selection=False, conf_kwargs=None):
        
    #     if  results_df[conf_col].dtype.name == 'category':
    #         # category
    #         conf_list = results_df[conf_col].cat.categories
    #     else: 
    #         # non-category
    #         conf_list = results_df[conf_col].unique()
    #         conf_list.sort()
        
    #     conf_choices = [ {'label':conf, 'value': conf} for conf in conf_list]

    #     if add_all_conf_selection:
    #         conf_choices = [{'label': 'All Conferences', 'value': 'All'}] + conf_choices
            
    #     props = dict(
    #         id=id,
    #         options=conf_choices,
    #         value=conf_name,
    #         searchable=False,
    #         clearable=True,
    #         placeholder=placeholder_text,
    #         # style=dropdown_style,
    #         className=className,
    #         persistence=True,
    #         persistence_type='session'
    #         )

    #     # Apply kwargs        
    #     if conf_kwargs is not None:
    #         props.update(conf_kwargs)
            
    #     # dd = dcc.Dropdown(
    #     #     id=id,
    #     #     options=conf_choices,
    #     #     value=conf_name,
    #     #     searchable=False,
    #     #     clearable=True,
    #     #     placeholder=placeholder_text,
    #     #     # style=dropdown_style,
    #     #     className=className,
    #     #     persistence=True,
    #     #     persistence_type='session'
    #     # )

    #     dd = dcc.Dropdown(**props)
        
    #     # # Apply kwargs
    #     # if conf_kwargs is not None:
    #     #     for k,v in conf_kwargs.items():
    #     #         dd[k] = v
            
    #     if dropdown_style is not None:
    #         dd.style = dropdown_style
    
    #     return dd
    
    # def create_season_dropdown(self, id='season-dropdown', className='season-dropdown', dropdown_style=None, multi=True):

    #     # using imported season_list
    #     # season_col = 'Season'
    #     # season_list = results_df[season_col].unique()
    #     # season_list.sort(reverse=True)
    #     season_choices = [ {'label':"{}-{}".format(season-1, str(season)[-2:]), 'value': season} for season in season_list]
        
    #     dd = dcc.Dropdown(
    #         id=id,
    #         options=season_choices,
    #         value=season_list,
    #         searchable=False,
    #         clearable=False,
    #         placeholder="Select seasons",
    #         multi=True,
    #         # style=dropdown_style,
    #         className=className,
    #         persistence=True,
    #         persistence_type='session'
    #     )

    #     if dropdown_style is not None:
    #         dd.style = dropdown_style
    
    #     return dd

    # from dev.espn.espn_team import EspnTeamStaticData
    
    # def create_team_dropdown(self, team_list_df, team_id=None, id='team-dropdown', className='team-dropdown', dropdown_style=None, placeholder_text='Select team'):
        
    #     # TODO Cache combo box for reuse
        
    #     team_list_df = team_list_df.sort_values(by='TeamName')
    #     team_name_id_dict = dict(zip(team_list_df['TeamName'], team_list_df['TeamId']))
    #     team_choices = [ {'label':key, 'value': value} for key,value in team_name_id_dict.items()]
        
    #     dd = dcc.Dropdown(
    #         id=id,
    #         options=team_choices,
    #         value=team_id,
    #         searchable=False,
    #         clearable=False,
    #         placeholder=placeholder_text,
    #         multi=False,
    #         # style=dropdown_style,
    #         className=className,
    #         persistence=True,
    #         persistence_type='session'
    #     )

    #     if dropdown_style is not None:
    #         dd.style = dropdown_style

    #     return dd

    # # Create a conference selector panel        
    # def createConfSelector(
    #         self, results_df, conf_name=None, conf_col='TeamConf', conf_kwargs=None):
        
    #     frmLabel = dbc.Label(
    #         "Conference:", 
    #         # size='sm', 
    #         className='mx-2 my-auto', 
    #         key='label', 
    #         html_for='conf-dropdown'
    #         )
        
    #     frmDropDown = self.create_conf_dropdown(results_df, conf_name, conf_col=conf_col, add_all_conf_selection=True, conf_kwargs=conf_kwargs)
        
    #     # frm_grp = dbc.FormGroup(
    #     #     [
    #     #         frmLabel,
    #     #         html.Div(
    #     #             frmDropDown,
    #     #             className='col-sm-3 px-2 my-1'),
    #     #     ],
    #     #     # check=True,
    #     #     inline=True,
    #     #     row=True,
    #     #     key='conf-dropdown-grp',
    #     #     className='px-2',
    #     #     # style={'display': display_style}
    #     #     )
        
    #     conf_season_selector = html.Div(
    #         html.Div([
    #             # html.Div(
    #             #     self.create_season_dropdown(),
    #             #     className='col-sm-auto px-2 my-1'),
    #             # html.Div(className="w-100"),
    #             frmLabel,
    #             html.Div(
    #                 frmDropDown,
    #                 className='col-sm-3 px-1 my-auto'),
    #             # dbc.Row(frm_grp),
    #             html.Div(
    #                 dbc.Button(
    #                     "Update",
    #                     id='submit-button-state', n_clicks=0, 
    #                     # outline=True,
    #                     color="primary", 
    #                     # className="round", 
    #                     size='sm', 
    #                     external_link=True,
    #                     ),
    #                 className='col-sm-2 px-2 my-1'),
                
    #             ],
    #             className='row p-2 align-items-center'),
    #         className='container px-2 border')
    
    #     return conf_season_selector
        
    # # Create a conference-season selector panel        
    # def createConfSeasonSelector(
    #         self, results_df, conf_name=None, conf_col='TeamConf', conf_kwargs=None):
        
    #     conf_season_selector = html.Div(
    #         html.Div([
    #             html.Div(
    #                 self.create_season_dropdown(),
    #                 className='col-sm-auto px-2 my-1'),
    #             html.Div(className="w-100"),
    #             html.Div(
    #                 self.create_conf_dropdown(results_df, conf_name, conf_col=conf_col, conf_kwargs=conf_kwargs),
    #                 className='col-sm-4 px-2 my-1'),
                
    #             # html.Div(
    #             #     dbc.Button(id='submit-button-state', n_clicks=0, children='Update', color="primary", className="mr-1", size='small'),
    #             #     className='col-6 col-sm-2 px-2 my-1'),
                
    #             html.Div(
    #                 # html.Button(id='submit-button-state', n_clicks=0, 
    #                 #            children='Update', 
    #                 #            # outline=True,
    #                 #            # color="primary", 
    #                 #            # className="mr-1", size='small', 
    #                 #            ),
    #                 dbc.Button(
    #                     "Update",
    #                     id='submit-button-state', n_clicks=0, 
    #                     # outline=True,
    #                     color="primary", 
    #                     # className="round", 
    #                     size='sm', 
    #                     ),
    #                 className='col-sm-2 px-2 my-1'),
                
    #             ],
    #             className='row p-2 align-items-center'),
    #         className='container px-2 border')
    
    #     return conf_season_selector

    # # TODO Consider refactoring this and other panels into a configurable class with exposed settings
    # # than can be modified before the final panel is created.
    # # Might be cleaner than a huge list of input parameters that need to be passed up and 
    # # down the calling hierarchy
    # # Create a conference-team selector panel    
    # def createConfTeamSelector(self, team_list_df, team_id=None, 
    #                            conf_dropdown_id='conf-dropdown', 
    #                            team_dropdown_id='team-dropdown',
    #                            conf_col='Conference'):

    #     selector = html.Div([
    #         html.Div([
    #             html.Div(
    #                 self.create_conf_dropdown(team_list_df, conf_col=conf_col, placeholder_text='Filter teams by conference', 
    #                                           id=conf_dropdown_id),
    #                 className='col-6 col-sm-4 px-2 my-1'),
    #             html.Div(className="w-100"),
    #             html.Div(
    #                 self.create_team_dropdown(team_list_df, team_id=team_id, id=team_dropdown_id),
    #                 className='col-sm-4 px-2 my-1'),
    #             ],
    #             className='row p-2 align-items-center'),
    #         ],
    #         className='container px-2 border')
    
    #     return selector

    # # Create a conference-team-update selector panel    
    # def createConfTeamUpdateSelector(self, team_list_df, team_id=None, conf_col='Conference'):

    #     selector = html.Div([
    #         html.Div([
    #             html.Div(
    #                 self.create_conf_dropdown(team_list_df, conf_col=conf_col, placeholder_text='Filter teams by conference'),
    #                 className='col-sm-4 px-2 my-1'),
    #             html.Div(className="w-100"),
    #             html.Div(
    #                 self.create_team_dropdown(team_list_df, team_id=team_id),
    #                 className='col-sm-4 px-2 my-1'),
    #             html.Div(
    #                 dbc.Button(
    #                     "Update",
    #                     id='submit-button-state', n_clicks=0, 
    #                     # outline=True,
    #                     color="primary", 
    #                     # className="round", 
    #                     size='sm', 
    #                     ),
    #                 className='col-sm-2 px-2 my-1'),
    #             ],
    #             className='row p-2 align-items-center'),
    #         ],
    #         className='container px-2 border')
    
    #     return selector
    
    # Too hard for now to get layout correct
    # # Create a conference-team-update form pane
    # def createConfTeamUpdateForm(self, team_list_df, team_id=None):

    #     form = html.Div([
    #         dbc.Form([
    #             dbc.FormGroup(
    #                 self.create_conf_dropdown(
    #                     team_list_df, conf_col='Conference', 
    #                     placeholder_text='Filter teams by conference', 
    #                     className='conf-dropdown col-sm-4 px-2 my-1',
    #                     # className=None
    #                     ),
    #                 # className='col-sm-4 px-2 my-1'
    #                 className='border'
    #                 ),
    #             # ]),
    #         # dbc.Form([
    #             # html.Div(className="w-100"), # Adds a row spacer 
    #             dbc.FormGroup([
    #                 dbc.Col(
    #                     self.create_team_dropdown(
    #                         team_list_df, team_id=team_id,
    #                         # className='team-dropdown col-sm-4 px-2 my-1',
    #                         # className=None,
    #                         dropdown_style={'width': '100%'},
    #                         className='mx-0'
    #                         ),
    #                     className='col-sm-4 mx-0 px-0, my-1 border',
    #                     ),
    #                 dbc.Button(
    #                     "Update",
    #                     id='submit-button-state', n_clicks=0, 
    #                     # outline=True,
    #                     color="primary", 
    #                     # className="round", 
    #                     size='sm', 
    #                     # className='col-sm-1 px-2 my-1',
    #                     className='px-2 my-1',
    #                     ),
    #                 ],
    #                 row=True,
    #                 inline=True,
    #                 # className='row p-2 align-items-center'                    ,
    #                 # className='row col-sm-6 p-2 clearfix',
    #                 className='border mx-0 px-0'
    #                 ),
    #             ],
    #             # inline=True,
    #             className='border mx-0 px-0'
    #             ),
    #         ],
    #         # className='container px-2 border'
    #         className='px-2 border'
    #         )
    
    #     return form
    
    # def createConfTeamSeasonSelector(self, team_list_df, team_id=None, season_id=None,conf_col='Conference'):
        
    #     selector = html.Div([
    #         html.Div([
    #             html.Div(
    #                 self.create_conf_dropdown(team_list_df, conf_col=conf_col, placeholder_text='Filter teams by conference'),
    #                 className='col-sm-4 px-2 my-1'),
    #             html.Div(className="w-100"),
    #             html.Div(
    #                 self.create_team_dropdown(team_list_df, team_id=team_id),
    #                 className='col-sm-4 px-2 my-1'),
    #             html.Div(
    #                 self.create_season_dropdown(),
    #                 className='col-sm-auto px-2 my-1'),

    #             html.Div(
    #                 dbc.Button(
    #                     "Update",
    #                     id='submit-button-state', n_clicks=0, 
    #                     # outline=True,
    #                     color="primary", 
    #                     # className="round", 
    #                     size='sm', 
    #                     external_link=True,
    #                     ),
    #                 className='col-6 col-sm-2 px-2 my-1'),
    #             ],
    #             className='row p-2 align-items-center'),
    #         ],
    #         className='container px-2 border')
        
    #     return selector

# TODO Move this somewhere else after it has been refined a bit
########## Settings Panel Builder ###############

# Trying to implement reusable panel settings
""" This is a clever attempt to introduce a framework for reusable panel settings.
We have a base class for a setting or group of settings, which have some descriptive
attributes that streamline downstream usage to create a flexible settings panel.

The isStorable parameter tells whether an item has a storable value.  If storable,
we use dcc.Store to create a dictionary based on the list of storable values from the 
settings items.  The mechanics are pretty generic and reusable, and only require the
callback to implement how the parameters are used from the data store.

"""

##################### Configuration Data ########################
# from components.data import season_list

# # TODO Consider moving this to the common data file
# # Default data settings
# NUM_REFS = 10
# MIN_GAMES = 5

# # conf_game_configs = [
# #     {"label": "All Games", "value": 'Overall', 'gameTag':'All Games', 'headingTag': 'All'},
# #     {"label": "Conference", "value": "Conf", 'gameTag': 'In Conference', 'headingTag': 'Conference'},
# #     {"label": "Non-Conference", "value": "NonConf", 'gameTag': 'Non-Conference', 'headingTag': 'Non-Conference'},
# #     ]
# conf_game_configs = {
#     "Overall": {"label": "All Games", "value": 'Overall', 'gameTag':'All Games', 'headingTag': 'All'},
#     "Conf": {"label": "Conference", "value": "Conf", 'gameTag': 'In Conference', 'headingTag': 'Conference'},
#     "NonConf": {"label": "Non-Conference", "value": "NonConf", 'gameTag': 'Non-Conference', 'headingTag': 'Non-Conference'},
#     }

# # metric_cat_configs = [
# #     {"label": ' Wins', "value": 'wins', 'title': 'Wins'},
# #     {"label": ' Points', "value": 'points', 'title': 'Average Points'},
# #     {"label": ' Fouls', "value": 'fouls', 'title': 'Average Fouls'},
# #     {"label": ' Turnovers', "value": 'turnovers', 'title': 'Average Turnovers'},
# #     {"label": ' Spreads', "value": 'spreads', 'title': 'Point Spreads'},
# #     {"label": ' Over/Under', "value": 'over-under', 'title': 'Over / Under'},
# #     ]
# metric_cat_configs = {
#     'wins': {"label": ' Wins', "value": 'wins', 'title': 'Wins'},
#     'points': {"label": ' Points', "value": 'points', 'title': 'Average Points'},
#     'fouls': {"label": ' Fouls', "value": 'fouls', 'title': 'Average Fouls'},
#     'turnovers': {"label": ' Turnovers', "value": 'turnovers', 'title': 'Average Turnovers'},
#     'spreads': {"label": ' Spreads', "value": 'spreads', 'title': 'Point Spreads'},
#     'over-under': {"label": ' Over/Under', "value": 'over-under', 'title': 'Over / Under'},
#     }

# season_configs = [{'label': '{}-{}'.format(season-1, str(season)[-2:]), 'value': season} for season in season_list]

# # Form Groups
from dataclasses import dataclass #, field
from typing import Any

# Base class for a group of settings items
@dataclass
class BaseSettingsItem:
    className: str = ""
    configName: str = ""
    isStorable: bool = False
    hasDefaultVal: bool = False
    defaultVal: Any = None
    visible: bool = True # TODO Change to isVisible
    
    def get_component():
        raise NotImplementedError

# # TODO Generalize to number of items?    
# @dataclass
# class NumRefsGroup(BaseSettingsItem):
    
#     def __init__(self, defaultVal=10): 
#         self.className="mr-3"
#         self.configName='num-refs'
#         self.isStorable=True
#         self.hasDefaultVal=True
#         self.defaultVal=defaultVal
    
#     frmLabel: dbc.Label = dbc.Label("Num. Ref Cards:", className="mr-2 form-control-sm", key='label')
    
#     frmInput: dbc.Input = dbc.Input(
#         id='num-refs-input', key='num-refs-input',
#         type="number", placeholder="Enter number of ref cards", 
#         className="form-control-sm my-1",
#         style={'width':'100px'},
#         bs_size="sm",
#         min=1,
#         persistence=True,
#         persistence_type='session',
#         )
    
#     def get_component(self):
        
#         inp = self.frmInput
#         inp.value = self.defaultVal
#         # display_style = 'initial' if self.visible else 'none'
        
#         frm_grp = dbc.FormGroup(
#             [
#                 self.frmLabel,
#                 inp,
#             ],
#             key='num-refs-grp',
#             # row=True,
#             className=self.className,
#             # style={'display': display_style}
#             )

#         if self.visible == False:
#             frm_grp.style = {'display': 'none'}

#         return  frm_grp

# @dataclass
# class MinGamesGroup(BaseSettingsItem):
    
#     def __init__(self, defaultVal=5): 
#         self.className="ml-1 mr-3" 
#         self.configName='min-games'
#         self.isStorable=True
#         self.hasDefaultVal=True
#         self.defaultVal=defaultVal
    
#     frmLabel: dbc.Label = dbc.Label(
#         "Min. Games:", 
#         className="form-control-sm", 
#         key='label', 
#         html_for='min-games-input',
#         # width=2,
#         )
    
#     frmInput: dbc.Input = dbc.Input(
#         id='min-games-input', key='min-games-input', 
#         type="number", placeholder="Enter minimum games per ref", 
#         # className="form-control form-control-sm my-1",
#         className="my-1",
#         style={'width':'100px'},
#         bs_size="sm",
#         min=0,
#         persistence=True,
#         persistence_type='session',
#         )
    
#     def get_component(self):
        
#         inp = self.frmInput
#         inp.value = self.defaultVal
#         # display_style = 'initial' if self.visible else 'none'
        
#         frm_grp = dbc.FormGroup(
#             [
#                 self.frmLabel,
#                 # dbc.Col(
#                     inp,
#                     # width = 4,
#                     # ),
#             ],
#             key='min-games-grp',
#             row=True,
#             className=self.className,
#             # style={'display': display_style}

#             )
    
#         # display_style = 'initial' if self.visible else 'none'
#         if self.visible == False:
#             frm_grp.style = {'display': 'none'}

#         return dbc.Row(frm_grp, form=True)

# @dataclass
# class ConfGameTypeGroup(BaseSettingsItem):
    
#     def __init__(self, defaultVal='Conf'): 
#         self.className="ml-1 mr-2 my-2"
#         self.configName='conf-game-type'
#         self.isStorable=True
#         self.hasDefaultVal=True
#         self.defaultVal=defaultVal
    
#     frmLabel: dbc.Label = dbc.Label(
#         "Game Type:", 
#         size='sm', 
#         className='px-2', 
#         key='label', 
#         html_for='conf-game-input'
#         )
    
#     frmRadioItems: dbc.RadioItems = dbc.RadioItems(
#         options=list(conf_game_configs.values()),
#         # value="Conf",
#         id="conf-game-input", 
#         key="conf-game-input",
#         className="form-control form-control-sm mx-2 px-2 py-1",
#         # className="form-control-sm",
#         labelClassName='small py-1',
#         persistence=True,
#         persistence_type='session',
#         inline=True,
#         ) 
#     def get_component(self):
        
#         radioItems = self.frmRadioItems
#         radioItems.value = self. defaultVal
#         # display_style = 'initial' if self.visible else 'none'
        
#         frm_grp = dbc.FormGroup(
#             [
#                 self.frmLabel,
#                 radioItems,
#             ],
#             inline=True,
#             row=True,
#             key='conf-game-grp',
#             className=self.className,
#             # style={'display': display_style}
#             )
    
#         # display_style = 'initial' if self.visible else 'none'
#         if self.visible == False:
#             frm_grp.style = {'display': 'none'}

#         return dbc.Row(frm_grp, form=True)


# # Metric categories (e.g., wins, points, turnovers)
# @dataclass
# class MetricCatsGroup(BaseSettingsItem):
    
#     def __init__(self):
#         self.className='ml-2 mr-2 my-2'
#         self.configName='metric-cats'
#         self.isStorable=True
#         self.hasDefaultVal=True
#         self.defaultVal=list(metric_cat_configs.keys())
    
#     frmLabel: dbc.Label = dbc.Label(
#         "Categories:", 
#         size='sm', 
#         className='px-2', 
#         key='label', 
#         html_for='metric-cat-input'
#         )
    
#     frmChecklist: dbc.Checklist = dbc.Checklist(
#         id='metric-cat-input', 
#         key='metric-cat-input',
#         options=list(metric_cat_configs.values()),
#         # value=['wins'],
#         className='form-control form-control-sm py-1',
#         # className='form-control-sm',
#         labelClassName='small py-1',
#         # labelStyle={'display': 'inline-block',
#         #             # 'marginRight': '5px'
#         #             },
#         persistence=True,
#         persistence_type='session',
#         inline=True
#     )
#     def get_component(self):
        
#         checklist = self.frmChecklist
#         checklist.value = self.defaultVal
        
#         frm_grp = dbc.FormGroup(
#             [
#                 self.frmLabel,
#                 checklist,
#             ],
#             # check=True,
#             inline=True,
#             row=True,
#             key='metric-cats-grp',
#             className=self.className,
#             # style={'display': display_style}
#             )

#         # display_style = 'initial' if self.visible else 'none'
#         if self.visible == False:
#             frm_grp.style = {'display': 'none'}

#         return dbc.Row(frm_grp, form=True)

# # Season filter
# @dataclass
# class SeasonPicklist(BaseSettingsItem):
    
#     def __init__(self):
#         self.className='ml-1 mr-2 my-2'
#         self.configName='metric-seasons'
#         self.isStorable=True
#         self.hasDefaultVal=True
#         self.defaultVal=season_list
       
#     frmLabel: dbc.Label = dbc.Label(
#         "Seasons:", 
#         size='sm', 
#         className='mr-2', 
#         key='label', 
#         html_for='season-input'
#         )
    
#     frmChecklist: dbc.Checklist = dbc.Checklist(        
#         id='season-input',
#         key='season-input',
#         options=[{'label': '{}-{}'.format(season-1, str(season)[-2:]), 'value': season} for season in season_list],
#         # value=['wins'],
#         className='form-control form-control-sm py-1',
#         labelClassName='small py-1',
#         # labelStyle={'display': 'inline-block',
#         #             # 'marginRight': '5px'
#         #             },
#         persistence=True,
#         persistence_type='session',
#         inline=True
#     )
#     # frmDropDown: dcc.Dropdown = dcc.Dropdown(
#     #         id='season-input',
#     #         # key='season-input',
#     #         options=season_configs,
#     #         # value=[config['value'] for config in season_configs],
#     #         searchable=False,
#     #         clearable=False,
#     #         placeholder="Select seasons",
#     #         multi=True,
#     #         # style=dropdown_style,
#     #         # className='form-control form-control-sm',
#     #         className='form-control-sm',
#     #         persistence=True,
#     #         persistence_type='session'
#     #     )
    
#     def get_component(self):
        
#         checklist = self.frmChecklist
#         checklist.value = self.defaultVal
#         # display_style = 'initial' if self.visible else 'none'
#         # dropdown = self.frmDropDown
#         # dropdown.value = self.defaultVal
        
#         frm_grp = dbc.FormGroup(
#             [
#                 self.frmLabel,
#                 checklist,
#                 # dropdown
#             ],
#             inline=True,
#             row=True,
#             key='season-grp',
#             className=self.className,
#             # style={'display': display_style},
#             # check=True,
#             )
        
#         # display_style = 'initial' if self.visible else 'none'
#         if self.visible == False:
#             frm_grp.style = {'display': 'none'}

#         return dbc.Row(frm_grp, form=True)

@dataclass
class ApplyButton(BaseSettingsItem):
    className='m-2'
    # configName=None
    # isStorable=False
    btn: dbc.Button = dbc.Button(
        "Apply", 
        id='apply-btn', 
        key='apply-btn', 
        color="primary", 
        size='sm')
    
    def get_component(self):
        return dbc.Row([
            dbc.Col(width=7),
            dbc.Col(
                self.btn,
                width=1,
                ),
            ],
            # form=True,
            # className='ml-2',
            style={'width':'100%'}
            )

@dataclass
class LiveUpdateSwitch(BaseSettingsItem):
    
    def __init__(self):
        self.className='ml-2 mr-2 my-2'
        self.configName='update-switch'
        self.isStorable=True
        self.hasDefaultVal=True
        self.defaultVal=[True] # enable updates by default

    frmLabel: dbc.Label = dbc.Label(
        "Live Updates:", 
        size='sm',
        className='px-2',
        key='label',
        html_for='update-switch-input'
        )
    
    frmChecklist: dbc.Checklist = dbc.Checklist(
        id='update-switch-input', 
        key='update-switch-input',
        options=[
            {'label': 'On', 'value': True},
            # {'label': 'Off', 'value': False}
            ],
        className='form-control form-control-sm py-1 px-2',
        # className='form-control-sm',
        labelClassName='small py-1 px-1',
        # labelStyle={'display': 'inline-block',
        #             # 'marginRight': '5px'
        #             },
        persistence=True,
        persistence_type='session',
        inline=True,
        switch=True
    )
    
    def get_component(self):
        
        switch = self.frmChecklist
        switch.value = self.defaultVal
        
        # frm_grp = dbc.FormGroup(
        frm_grp = dbc.Row(
            
            [
                self.frmLabel,
                switch,
            ],
            # check=True,
            # inline=True,
            # row=True,
            key='update-switch-grp',
            className=self.className,
            # style={'display': display_style}
            )

        # display_style = 'initial' if self.visible else 'none'
        if self.visible == False:
            frm_grp.style = {'display': 'none'}

        # return dbc.Row(frm_grp, form=True)
        return dbc.Row(frm_grp)


@dataclass
class UpdateFreqGroup(BaseSettingsItem):
    
    def __init__(self, defaultVal=10): 
        self.className="ml-1 mr-3" 
        self.configName='update-freq'
        self.isStorable=True
        self.hasDefaultVal=True
        self.defaultVal=defaultVal
    
    frmLabel: dbc.Label = dbc.Label(
        "Update Frequency (seconds):", 
        className="form-control-sm", 
        key='label', 
        html_for='update-freq-input',
        # width=2,
        )
    
    frmInput: dbc.Input = dbc.Input(
        id='update-freq-input', key='update-freq-input', 
        type="number", placeholder="Enter minimum games per ref", 
        # className="form-control form-control-sm my-1",
        className="my-1",
        style={'width':'100px'},
        size="sm",
        min=5,
        persistence=True,
        persistence_type='session',
        disabled=True,
        )
    
    def get_component(self):
        
        inp = self.frmInput
        inp.value = self.defaultVal
        # display_style = 'initial' if self.visible else 'none'
        
        # frm_grp = dbc.FormGroup(
        frm_grp = dbc.Col(
            [
                self.frmLabel,
                # dbc.Col(
                    inp,
                    # width = 4,
                    # ),
            ],
            key='update-freq-grp',
            # row=True,
            className=self.className,
            # style={'display': display_style}

            )
    
        # display_style = 'initial' if self.visible else 'none'
        if self.visible == False:
            frm_grp.style = {'display': 'none'}

        # return dbc.Row(frm_grp, form=True)
        return dbc.Row(frm_grp)

@dataclass
class ConfigStore(BaseSettingsItem):
    frmItems: List[BaseSettingsItem] = None  # List of configuration items whose parameters will be stored
    showConfig: bool = False

    def get_component(self, frm_items: List[BaseSettingsItem] = None, showConfig: bool = False):
        
        frm_items = self.frmItems if frm_items is None else frm_items
        showConfig = self.showConfig if showConfig is False else showConfig
        display_style = {'display': 'inline'} if showConfig else {'display':'none'}
        
        # if type(frmItems) is List[BaseSettingsItem]:
        #     config_store_data = {item.configName:item.defaultVal for item in self.frm_items if item.isStorable & item.hasDefaultVal}
        # else:
        #     config_store_data = None
        config_store_data = {item.configName:item.defaultVal for item in frm_items if item.isStorable & item.hasDefaultVal}
            
        if config_store_data is None:
            # Nothing to store
            return None
        
        config_store = None
        
        if len(config_store_data) > 0:
 
            config_store = html.Div([                
                # For debugging, comment style line
                html.Pre(str(config_store_data), id='std-config-data', key='std-config-data',
                          style=display_style,  
                          ),
                dcc.Store(
                    id='std-config-settings',
                    data=config_store_data,
                    storage_type='session',
                    ),
                ],
                key='std-config-store',
                )
 
            return config_store

# # Utility class for building settings panels
# # TODO Consider whether to create new instances of settings form items
# # TODO Consider whether to embed settings data classes under the settings panel builder
class SettingsPanelBuilder():
    
    def __init__(self):
        
#         # TODO convert this to a named list and only instantiate settings that are in use
#         self.numRefsGroup = NumRefsGroup()
#         self.minGamesGroup = MinGamesGroup()
#         self.confGameTypeGroup = ConfGameTypeGroup()
#         self.metricCatsGroup = MetricCatsGroup()
#         self.seasonPicklist = SeasonPicklist()
        self.applyButton = ApplyButton()
        self.configStore = ConfigStore()
        self.liveUpdateSwitch = LiveUpdateSwitch()
        self.updateFreqGroup = UpdateFreqGroup()
    
    # Creates a storable settings panel with a list of settings form items
    def create_settings_panel(self, frm_items):
        
        # Hide items that aren't used
        # It's simpler for now to build and reuse a generic settings panel
        # self.numRefsGroup.visible = False
        
        # Get the components from the form item configs
        frm_components = [item.get_component() for item in frm_items]

        # Get the item to store the configuration item values
        config_store = self.configStore
        frm_components.append(config_store.get_component(frm_items=frm_items, showConfig=False))
        settings_form = dbc.Form(
            frm_components,
            # inline=True,
        )
        
        settings = html.Div(
            [
                dbc.Button(
                    html.A(["Settings ", html.I(className="fa fa-cog")]),
                    id="std-settings-btn",
                    className="mb-1",
                    color="primary",
                    size="sm",
                ),
                dbc.Collapse(
                    # dbc.Card(dbc.CardBody("This content is hidden in the collapse")),
                    settings_form,
                    id="std-settings-panel",
                    className='border p-2 mt-0 bg-light',
                    # style={'backgroundColor': '#E6E6E3'},
                ),
            ],
            className="container m-2 mx-auto",
        )
        
        return settings
   

# #################### Settings Panel Callbacks #######################

# Callback for toggling standard settings panel
@app.callback(
    Output("std-settings-panel", "is_open"),
    [Input("std-settings-btn", "n_clicks")],
    [State("std-settings-panel", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# Standard callback for applying report settings
# Shared callback based on all available settings parameters
# Not sure about this one
# TODO Consider whether we can pass a generic list of inputs vs. hard-coded list
# Can probably pass settings children as input and loop through generically
@app.callback(
    [
     # Output('submit-button-state', 'n_clicks'),
      Output("std-settings-btn", "n_clicks"),
      Output("std-config-settings", "children"),
      Output("std-config-data", 'children'),],
    [Input("apply-btn", "n_clicks")],
    [
     # State('submit-button-state', 'n_clicks'),
      State("std-settings-btn", "n_clicks"),
      State('update-switch-input', 'value'),
      State("update-freq-input", 'value'),
      
      # State("num-refs-input", "value"),
      # State("min-games-input", "value"),
      # State("conf-game-input", "value"),
      # State("metric-cat-input", "value"),
      # State("season-input", "value"),     
      ],
)
def apply_settings(n1, n3, update_switch, update_freq):
    config = {        
        'update-switch-input': update_switch,
        "update-freq-input": update_freq,
        # "conf-game-type": conf_game_type,
        # "metric-cats": metric_cats,
        # "season-list": season_list,
        }
    return n3, config, str(config)

        