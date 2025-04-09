# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 11:18:03 2021

@author: kknow

Wrapper script to launch app in debug mode

"""

# TODO Good tutorial, with authentication and migration to Heroku
# https://www.datacamp.com/community/tutorials/learn-build-dash-python

# Good note on Heroku deployment and setup
# https://towardsdatascience.com/deploying-your-dash-app-to-heroku-the-magical-guide-39bd6a0c586c

from app import app
import os

# from dash.dependencies import Input, Output

# from components.layouts import LayoutBuilder

import prod

#################### Page Layout Handler #################

if __name__ == "__main__":
    
    app.run_server(debug=True, port=os.getenv("PORT", "8051"))