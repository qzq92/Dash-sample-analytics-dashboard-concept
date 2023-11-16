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


# Dash instantiation create the dash application using the above layout definition
app = Dash(__name__,  meta_tags=[{"name": "viewport", "content": "width=device-width"}])

# Plotly mapbox public token
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"


# Traffic_cam_location dataframe initialization
traffic_cam_locations_df = process_traffic_cam_locations()
traffic_cam_locations = traffic_cam_locations_df.to_dict("Description")


# Mapbox graph compnment
mapbox_graph = html.Div(id='div-body',children = [
                    dcc.Graph(id = 'mapbox')
               ])


# Layout of Dash App
app.layout = html.Div(
    children=[
        # Define a single html div
        html.Div(
            className="row",
            children=[
                # Column via Div for user controls
                html.Div(
                    className="div-user-controls",
                    children=[
                        html.P(
                            """Select location"""
                        ),
                        # Change 
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for locations on map
                                        dcc.Dropdown(
                                            id="location-dropdown",
                                            options=[
                                                # Set label and value
                                                {"label": i, "value": i}
                                                for i in traffic_cam_locations
                                            ],
                                            placeholder="Select a location",
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="div-for-map bg-grey",
                    children=[
                        # First children Mapbox graph
                        dcc.Graph(id="map-graph"),
                        # Column for analytics 
                        html.Image(
                            id="traffic-footage",
                            className="div-for-traffic-footage bg-grey",
                        ),
                    ],
                ),
                # Column for analytics 
                html.Div(
                    className="div-for-analytics bg-grey",
                    children=[


                        
                    ]
                ),
            ],
        )
    ]
)

""" start the web application
    the host IP 0.0.0.0 is needed for dockerized version of this dash application
"""
if __name__ == '__main__':
    # Set app title
    app.title = "Near Real Time Analytics Dashboard"
    app.run_server(debug=False, host='0.0.0.0', port=8050)
    server = app.server # required for some deployment environment like Heroku