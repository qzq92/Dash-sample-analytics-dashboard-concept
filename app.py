from helpers.process_static_data import process_traffic_cam_locations
# Import packages
from dash import Dash, html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_design_kit as ddk
import plotly.graph_objects as go
import plotly.express as px
import sys
import logging
import logging.config
# create the dash application using the above layout definition

external_stylesheets = [dbc.themes.CERULEAN]
app = Dash(__name__, external_stylesheets=[external_stylesheets])

default_placeholder_content = html.Div([
    html.H3(id = 'under_construction', children = "Under construction")]
    )
""" Create the layout of the web-based dashboard using dash bootstrap components and dash core components
"""
# Traffic_cam_location
traffic_cam_loc_data = process_traffic_cam_locations()

# Dropdown selection for traffic camera location description
traffic_cam_location_dropdown = dcc.Dropdown(
    id='location_dropdown', 
    options=traffic_cam_loc_data["Description of Location"].unique(), 
    value=None
)

# Mapbox graph compnment
mapbox_graph = html.Div(id='div-body',children = [
                    dcc.Graph(id = 'mapbox')
                ])


weather = dbc.Row([
    dbc.Col(html.Div([]))
])

vehicle_count = 
analytics_summary = html.Div([])

rows = html.Div(
    [   
        # First row of layout representing title
        dbc.Row(dbc.Col(html.Div([
            html.H3(id = 'title', children = "Weather and traffic conditions dashboard"),
            html.H5(id = 'subtitle', children = 'Based on dataset from data.gov.sg'),            
        ], style = {'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}))),

        # Second row of layout with 2 columns representing content
        dbc.Row(
            [   
                # Sidebar
                dbc.Col(html.Div(children=[
                    html.H1(children='List of traffic camera location'),
                    traffic_cam_location_dropdown,
                ]), width=3),
                # Mapbox
                dbc.Col(mapbox_graph, width=6),
                # Analytics sidebar
                dbc.Col(analytics_summary , width=3),
            ], style = {'textAlign': 'center'}
        ),
    ]
)

# Put the entire layout as an container.
app.layout = dbc.Container(rows, fluid=True) 

""" start the web application
    the host IP 0.0.0.0 is needed for dockerized version of this dash application
"""
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)
    server = app.server # required for some deployment environment like Heroku