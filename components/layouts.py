# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 17:40:20 2021

@author: kknow
"""

from dash import dcc, html
# import dash_html_components as html
import dash_bootstrap_components as dbc
# import dash_core_components as dcc

from components.page import Header, Footer


# class BaseLayout():
    
#     def __init__(self, pageContent=None):
        
#         self.header = Header()
#         self.footer = Footer()
#         self.pageContent = pageContent
#         self.containerClassName = 'p-2'
        
#         return None
        
#     # TODO Get or create?
#     # Should we separate the configuration data from the builder to have
#     # more flexibility?
#     def get_layout(self):

#         layout = dbc.Container(
#             children = [
#                 dcc.Location(id='url', refresh=True),
#                 self.header,
#                 html.Div(id='page-content',
#                          children=self.pageContent), 
#                 self.footer,
#                 ],
#             className = self.containerClassName
#             )
        
#         return layout

################ Abstract Base Page Content Class ####################

import abc

# Abstract base class for page content
# This allows us to use a standard approach for invoking page-content for layouts
class BasePageContent(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def createPageContent(self, params:dict):
        pass

    
# Utility class for building standard layouts
class LayoutBuilder():
    
    def __init__(self):
        
        self.header = Header()
        self.footer = Footer()
        self.containerClassName = 'page-content p-2'

        return None
        
    def createStandardLayout(self, pageContent=None):
        '''
        Creates a standard layout by wrapping content with the standard
        header footer.  Playing around with this approach to see which one is
        preferred.

        Parameters
        ----------
        content : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        layout : TYPE
            DESCRIPTION.

        '''
        
        # config = BaseLayout(pageContent)
        
        # layout = config.get_layout()
        
        layout = dbc.Container(
            children = [
                dcc.Location(id='url', refresh=True),
                # dcc.Location(id='search', refresh=True),
                self.header,
                html.Div(id='page-content',
                         children=pageContent), 
                self.footer,
                ],
            className = self.containerClassName
            )
        
        return layout
        
    def createNotebookLayout(self, pageContent=None):
        
        nb_content = html.Div(
            pageContent,
            className = "container page-content",
            id = "notebook-container"
            )

        layout = self.createStandardLayout(nb_content)

        return layout

######################## 404 Page ########################

class NoPage(BasePageContent):
   
    def createPageContent(params:dict):

        pageContent = html.Div([
            html.H1(
                404,
                style={
                    'margin': '30px 0',
                    'fontSize': '4em',
                    'lineHeight': 1,
                    'letterSpacing': '-1px',
                    }
                ),
            html.P(html.Strong("Page not found")),
            html.P("The requested page could not be found"),
            ],
            className='container',
            style={
                'margin': '10px auto',
                'maxWidth': '600px',
                'textAlign': 'center'
                }
            )
        
        return pageContent

    