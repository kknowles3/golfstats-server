# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 16:35:59 2021

@author: kknow
"""

# TODO Good tutorial, with authentication and migration to Heroku
# https://www.datacamp.com/community/tutorials/learn-build-dash-python

import dash
# import dash_auth
import pathlib

import dash_bootstrap_components as dbc

# <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-BmbxuPwQa2lc/FVzBcNJ7UAyJxM6wuqIj61tLrc4wSX0szH/Ev+nYRRuWlolflfl" crossorigin="anonymous">
# <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta2/dist/js/bootstrap.bundle.min.js" integrity="sha384-b5kHyXgcpbZJO/tY9Ul7kGkf1S0CWuKcCD38l8YkeH8z8QjE0GmW1gYU5S9FOnJ0" crossorigin="anonymous"></script>

# https://dash.plotly.com/external-resources
external_scripts = [
    # Font Awesome JS for showing icons
    {'src': "https://use.fontawesome.com/releases/v5.0.8/js/all.js",
     'integrity':"sha384-SlE991lGASHoBfWbelyBPLsUlwY1GwNDJo3jSJO04KZ33K2bwfV9YBauFfnzvynJ",
     'crossorigin': "anonymous"},
    ]

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    ]

# TODO Not sure if we need this
# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

# Get the user authorization data from the remote database
# Site with info on username-specific layouts:
# https://stackoverflow.com/questions/51639020/python-dash-basic-auth-get-username-in-app
# TODO Keep this out of source code repository - save in a file or a database
from dev.util.data_util import RemoteDataServer
# def get_valid_user_pairs():
    
#     db_name = 'static_data'
#     collection_name = 'valid_users'
#     rds = RemoteDataServer(db_name)

#     # Load valid user pairs
#     user_pairs = rds.load_remote_data_item(collection=collection_name).get('valid_user_pairs', None)

#     return user_pairs

# VALID_USERNAME_PASSWORD_PAIRS = get_valid_user_pairs()

app = dash.Dash(
    __name__, meta_tags=[{
        "name": "viewport", 
        "content": "width=device-width, initial-scale=1, shrink-to-fit=no",
        "theme-color": "#157878",
        # "site.title": "RefStats Dashboard",
        "initial-scale": 1,
        'shrink-to-fit': "no",
        }],
    external_scripts=external_scripts,
    external_stylesheets=external_stylesheets, 
    title="GolfStats - Server",
)

# auth = dash_auth.BasicAuth(
#     app,
#     VALID_USERNAME_PASSWORD_PAIRS
# )

app.config.suppress_callback_exceptions = True