# Import packages
from dash import Dash, html
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
import logging

from .conf.api_key import MAPBOX_DEFAULT_KEY

from components import build_dashboard_banner,radius_selection_button, build_street_map_component, show_descriptive_stats, display_tabs

# Dash instantiation ---------------------------------------------------------#
app = Dash(__name__,
           meta_tags=[{
               "name": "viewport",
               "content": "width=device-width",
               "initial-scale": 1.0}],
           external_stylesheets=[dbc.themes.DARKLY],
           suppress_callback_exceptions = True, #
           title="SimpleDashboard Demo"
        )

# Dashboard app layout ------------------------------------------------------#
app.layout = html.Div(
    id="root",
    children=[
        # Header/Banner -------------------------------------------------#
        html.Div(
            id="header",
            children=[
                build_dashboard_banner()
            ],
        ),

        # App Container ------------------------------------------#
        html.Div(
            id="app-container",
            children=[
                # Left column for map placement
                build_street_map_component(mapbox_default_key=MAPBOX_DEFAULT_KEY),
                # Right column for Information around the selected point ----------------------#
                html.Div(
                    id="Descriptive-stats-content-container",
                    # Right column for map
                    children=[
                        # First row
                        radius_selection_button(),
                        # Next row
                        show_descriptive_stats(),
                        # Next div showing details in tab format(bus,bicycle,taxi,carpark and nearby available cctv footage)
                        display_tabs(),
                        #Content of tab
                        html.Div(id='tab-content')
                    ],
                    style={
                        "display": "inline-block",
                        "padding": "20px 20px 10px 10px",
                        "width": "39%",
                    },
                ),
            ],
            className="row",
        ),
)

# Callback imports -----------------------------------------------------------
# Putting callback before app layout results in error.
from callbacks import map_callback, tabs_callback

""" start the web application
    the host IP 0.0.0.0 is needed for dockerized version of this dash application
"""
if __name__ == '__main__':
    logging.info(sys.version)

    # If running locally in Anaconda env:
    if "conda-forge" in sys.version:
        app.run_server(debug=True)
    else:
        app.run_server(debug=False, host='0.0.0.0', port=8050)
    # Set app title
    app.title = "Near Real Time Analytics Dashboard"