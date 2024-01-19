# Import packages
from dash import Dash, html
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq
import plotly.graph_objects as go
import plotly.express as px
import sys
import logging

""" ----------------------------------------------------------------------------
 Dash App
---------------------------------------------------------------------------- """
app = Dash(__name__,
           meta_tags=[{
               "name": "viewport",
               "content": "width=device-width",
               "initial-scale": 1.0}],
           external_stylesheets=[dbc.themes.DARKLY],
           suppress_callback_exceptions = True, #
           title="SimpleDashboard Demo"
        )

# --------------------------------------------------------

def build_dashboard_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("Simple Dashboard Demo"),
                    html.H6("Showcasing nearby transportation option and activities"),
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.A(
                        html.Button(children="ENTERPRISE DEMO"),
                        href="https://plotly.com/get-demo/",
                    ),
                    html.Button(
                        id="learn-more-button", children="LEARN MORE", n_clicks=0
                    ),
                    html.A(
                        html.Img(id="logo", src=app.get_asset_url("dash-logo-new.png")),
                        href="https://plotly.com/dash/",
                    ),
                ],
            ),
        ],
    )

def radius_selection_button():
    return html.Div(
        id="Select-options",
        children=[   
            dcc.RadioItems(['500m Radius', '1Km Radius'], '500m Radius', inline=True)
        ],
        style={"textAlign": "right"},
    ),


def build_onestreet_map():
    return html.Div(
        id="left-column",
        children=[
            html.Div(
                id="osm-map-container",
                children=[
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H5(Children="Click on anywhere on the map"),
                                ],
                                style={
                                    "display": "inline-block",
                                    "width": "64%",
                                },
                                className="eight columns",
                            ),
                        ]
                    ),
                    dcc.Graph(id="onestreetmap"),
                ],
            ),
        ],
        style={
            "display": "inline-block",
            "padding": "20px 10px 10px 40px",
            "width": "59%",
        },
        className="seven columns",
    ),

def show_descriptive_stats():
    return html.Div(
        id="Descriptive-stats",
        children = [
            html.Div([
                html.P("Total Bus stops nearby"),
                daq.LEDDisplay(
                    id="nearby-bus-stop-led",
                    color="#92e0d3",
                    backgroundColor="#1e2130",
                    size=50,
                )],
                style={
                    "text-align": "center",
                }
            ),
            html.Div([
                html.P("Total Taxi Stands nearby"),
                daq.LEDDisplay(
                    id="nearby-taxi-stand-led",
                    color="#92e0d3",
                    backgroundColor="#1e2130",
                    size=50,
                )],
                style={
                    "text-align": "center",
                }
            ),
            html.Div([
                html.P("Total Bicycle Parking areas nearby"),
                daq.LEDDisplay(
                    id="nearby-bicycle-parking-led",
                    color="#92e0d3",
                    backgroundColor="#1e2130",
                    size=50,
                ),
                ],
                style={
                    "text-align": "center",
                }
            ),
            html.Div([
                html.P("Total Parking areas nearby"),
                daq.LEDDisplay(
                    id="nearby-bicycle-parking-led",
                    color="#92e0d3",
                    backgroundColor="#1e2130",
                    size=50,
                ),
            ],
                style={
                    "text-align": "center",
                }
            ),
        ]
    ),


def display_tabs():
    return html.Div(
        id = "tabs",
        classname="tabs",
        children = dcc.Tabs(
            id="multi-tabs",
            value="tab2",
            className="custom-tabs",
            children=[
                dcc.Tab(
                    id="bus-stop-tab",
                    label="Nearest bus stop",
                    value="bus-stop-tab",
                ),
                dcc.Tab(
                    id="bicycle-tab",
                    label="Nearest bicycle parking",
                    value="bicycle-tab",
                ),
                dcc.Tab(
                    id="taxi-stand-tab",
                    label="Nearest taxi stand",
                    value="taxi-stand-tab",
                ),
                dcc.Tab(
                    id="carpark-tab",
                    label="Nearest carpark",
                    value="carpark-tab",
                ),
                dcc.Tab(
                    id="traffic-cctv-tab",
                    label="Nearest available CCTV footage",
                    value="cctv-tab",
                ),
            ]
        )
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
                # Left column for map
                build_onestreet_map(),
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
        # Other analytics data --------------------------#
        html.Div(
            [
                html.Div(
                    [dcc.Markdown("Other surrounding information")],
                    style={
                        "textAlign": "left",
                        "padding": "0px 0px 5px 40px",
                        "width": "69%",
                    },
                    className="nine columns",
                ),
                html.Div(
                    id="-container",
                    children=[
                        html.Div(
                            [
                                dcc.Checklist(
                                    id="property-type-checklist",
                                    options=[
                                        {"label": "F: Flats/Maisonettes", "value": "F"},
                                        {"label": "T: Terraced", "value": "T"},
                                        {"label": "S: Semi-Detached", "value": "S"},
                                        {"label": "D: Detached", "value": "D"},
                                    ],
                                    value=["F", "T", "S", "D"],
                                    labelStyle={"display": "inline-block"},
                                    inputStyle={"margin-left": "10px"},
                                ),
                            ],
                            style={"textAlign": "right"},
                        ),
                        html.Div([dcc.Graph(id="price-time-series")]),
                    ],
                    style={
                        "display": "inline-block",
                        "padding": "20px 20px 10px 10px",
                        "width": "39%",
                    },
                    className="five columns",
                ),
                ),
            ],
            className="row",
        ),
    ],
)



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