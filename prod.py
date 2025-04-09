# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 11:18:03 2021

@author: kknow

This is production server file.  The code is virtually the same as the
debug file, except for the extra server instantiation and debug parameters

"""

# TODO Good tutorial, with authentication and migration to Heroku
# https://www.datacamp.com/community/tutorials/learn-build-dash-python

# Good note on Heroku deployment and setup
# https://towardsdatascience.com/deploying-your-dash-app-to-heroku-the-magical-guide-39bd6a0c586c

from app import app

from dash.dependencies import Input, Output

from components.layouts import LayoutBuilder, NoPage
from components.page import getParams

from layouts.home_page import HomePage
# from layouts.pool_data_server import PoolDataServer
from layouts.generic_pool_data_server import PoolDataServer

########### Initiate the app #############################
# Note that this is only for the production server
server = app.server

lb = LayoutBuilder()
app.layout = lb.createNotebookLayout()

#################### Page Layout Handler #################

# site_root = ''

def get_page_content(pathname, url_search=None):
    
    params = getParams(url_search)

    if pathname[-1] != "/":
        pathname = pathname + "/"
    
    content_dict = {
        '/': HomePage,
        '/pool-data-server/': PoolDataServer,

        }    

    content_bldr = content_dict.get(pathname, NoPage)
      
    content = content_bldr.createPageContent(params)
    
    return content

##########################################################

# TODO Convert layout display logic into a registration dictionary
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname'),
                Input('url', 'search')])
def display_page(pathname, search):    
    return get_page_content(pathname, search)

if __name__ == "__main__":
    
#     # Testing Google Analytics for prod
#     # https://community.plotly.com/t/tracking-application-analytics-with-google-analytics/38946/2
#     app.index_string = """<!DOCTYPE html>
# <html>
#     <head>
#         <!-- Global site tag (gtag.js) - Google Analytics -->
#         <script async src="https://www.googletagmanager.com/gtag/js?id=UA-179900031-1"></script>
#         <script>
#             window.dataLayer = window.dataLayer || [];
#             function gtag(){dataLayer.push(arguments);}
#             gtag('js', new Date());

#             gtag('config', 'UA-179900031-1', { 'anonymize_ip': true });
#         </script>
#         {%metas%}
#         <title>{%title%}</title>
#         {%favicon%}
#         {%css%}
#     </head>
#     <body>
#         {%app_entry%}
#         <footer>
#             {%config%}
#             {%scripts%}
#             {%renderer%}
#         </footer>
#     </body>
# </html>"""

    # https://aticoengineering.com/shootin-trouble-in-data-science/google-analytics-in-dash-web-apps/
    app.index_string = '''<!DOCTYPE html>
<html>
<head>
  <!-- Global site tag (gtag.js) - Google Analytics -->
    <script>(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
    
    ga('create', 'UA-179900031-1', 'auto');
    ga('send', 'pageview');
    </script>
  <!-- End Global Google Analytics -->
{%metas%}
<title>{%title%}</title>
{%favicon%}
{%css%}
</head>
<body>
{%app_entry%}
<footer>
{%config%}
{%scripts%}
{%renderer%}
</footer>
</body>
</html>
'''
    
    app.run_server(debug=False)