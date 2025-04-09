# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 16:36:21 2021

@author: kknow
"""

from dash import html
# import dash_html_components as html
# import dash_core_components as dcc
import dash_bootstrap_components as dbc

from components.layouts import BasePageContent

class PageCardBuilder():
    """
    Utility for building page link cards for the home page
    TODO Move this to the page class
    """
    
    def __init__(self):
        
        self.cardClass = "card shadow mx-auto py-2 my-2"
        self.cardBodyClass = 'card-body mb-1 pb-1'
        self.cardTitleClass = 'card-title'
        self.cardTextClass = 'card-text'
        self.pageButtonClass = "stretched-link"
        self.imgClass = "mx-auto"
        
    def create_page_card(self, card_title, card_text, page_href, img_src):
        
        title = html.H4(card_title, className=self.cardTitleClass)
        txt = html.P(card_text, className=self.cardTextClass)
        btn = dbc.Button("View Page", href=page_href, color="primary", size='sm', className=self.pageButtonClass)
        img = dbc.CardImg(
            src=img_src, className=self.imgClass, bottom=True,
            style={'height':'auto', 'width':'300px'}
            )
        
        card = dbc.Col(            
            dbc.Card([
                img,
                dbc.CardBody([
                    title,
                    txt,
                    btn
                    ],
                    # className=self.cardBodyClass,
                    style={"width": '20rem'},
                    ),
                ],
                className=self.cardClass
                ),
            width='auto'
            )
        
        return card

def create_page_cards():
    
    pb = PageCardBuilder()
    page_cards = []

    # page_cards.append(
    #     pb.create_page_card(
    #         card_title='Masters Pool 2021 - Live Update Server',
    #         card_text="""Admin page for live updates from the pool data server.""",
    #         page_href='/pool-data-server/',
    #         img_src='/assets/img/pages/pool-data-server.jpg' 
    #         )
    #     )

    page_cards.append(
        pb.create_page_card(
            card_title='PGA Pool 2021 - Live Update Server',
            card_text="""Admin page for live updates from the pool data server.""",
            page_href='/pool-data-server/',
            img_src='/assets/img/pages/pga-pool-data-server.jpg' 
            )
        )
    
    return dbc.Row(page_cards)

class HomePage(BasePageContent):
   
    def createPageContent(params:dict):
        
        page_cards = create_page_cards()
        
        # <div class="container-fluid mx-auto d-block">
        # <div class="row mx-auto">
        card_content = html.Div(
            page_cards,
            className="container-fluid mx-auto d-block"
            )

        content = [
            html.Div([
                html.H1('GolfStats - Pool Scoring Reports'),
                html.P(
                    """This site is a placeholder for various golf statistics and reports.  Please note that this site is currently under 
construction and includes only one report.\n""",
                    className='mb-2'),
                # html.Br(),
#                 dcc.Markdown(
#                     """The site currently includes a few reports based on historical game results:
# \n"""),
                # html.Br(),
#                 dcc.Markdown("""
# - [Referee Profiles By Game](/team-game-list/)
# - [Top/Bottom Ref Cards by Team](/team-ref-cards/)
# - [Top/Bottom Ref Lists by Team](/team-ref-stat-lists/)
# - [Ref Summary Stats by Team](/team-ref-stat-tables/)
# - [Team by Team Summary Statistics](/team-game-stat-tables/)
# - [Team Ref Stats by Conference](/conf-ref-stats/)
# - [Game spread results by conference](/conf-spd-results/)
# - [Over-under game results by conference](/conf-ou-results/)
# """,
#                 dangerously_allow_html=False),
                card_content,
                # html.Hr(),
#                 html.P("""If you have constructive feedback on what basketball statistics you'd like to see on the site, feel free to click
# on the "Contact Us" link below and send feedback.""",
                    # className='mb-2'),
                html.Hr(),
                dbc.Alert([
                    html.H4("Performance Considerations", className="alert-heading"),
                    html.P(
"""Please note that this site is currently hosted on a low-budget server, so performance may be spotty from time
to time, and it may take a few seconds to initially load the site (and before you'll see this helpful message).\n"""),
                        ],
                        color="warning", 
                        dismissable=False,
                        style={'width':'80%'},
                        className='mx-auto my-2',
                        ),
                                                                                           
                   html.Hr(),
                        
                ],
                className="px-3 mx-3",)
            ]

        return content