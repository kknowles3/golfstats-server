# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 17:55:02 2022

@author: kknow
"""

from layouts.pool_data_server import PoolDataServer
from components.page import getParams

url_search = ""
params = getParams(url_search)

layout =  PoolDataServer.createPageContent(params)