# Import packages
from dash import Dash, html
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_design_kit as ddk
import plotly.graph_objects as go
import plotly.express as px
import sys
import logging

# Dash instantiation create the dash application using the above layout definition
app = Dash(__name__,
           meta_tags=[{"name": "viewport", "content": "width=device-width", "initial-scale=1.0"}],
           external_stylesheets=[dbc.themes.DARKLY],
           suppress_callback_exceptions = True #
        )

# Mapbox graph compnment
mapbox_graph = html.Div(id='div-body',children = [
                    dcc.Graph(id = 'mapbox')
               ])
 --------------------------------------------------------#

app.layout = html.Div(
    id="root",
    children=[
        # Header -------------------------------------------------#
        html.Div(
            id="header",
            children=[
                html.Div(
                    [
                        html.Div(
                            [html.H1(children="Analytics Dashboard Demo")],
                            style={
                                "display": "inline-block",
                                "width": "74%",
                                "padding": "10px 0px 0px 20px",  # top, right, bottom, left
                            },
                        ),
                        html.Div(
                            [html.H6(children="Created with")],
                            style={
                                "display": "inline-block",
                                "width": "10%",
                                "textAlign": "right",
                                "padding": "0px 20px 0px 0px",  # top, right, bottom, left
                            },
                        ),
                        html.Div(
                            [
                                html.A(
                                    [
                                        html.Img(
                                            src=app.get_asset_url("dash-logo.png"),
                                            style={"height": "100%", "width": "100%"},
                                        )
                                    ],
                                    href="https://plotly.com/",
                                    target="_blank",
                                )
                            ],
                            style={
                                "display": "inline-block",
                                "width": "14%",
                                "textAlign": "right",
                                "padding": "0px 10px 0px 0px",
                            },
                        ),
                    ]
                ),
            ],
        ),

        # App Container ------------------------------------------#
        html.Div(
            id="app-container",
            children=[
                # Left column for map
                html.Div(
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
                                dcc.Graph(id="choropleth"),
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
                # Information around the selected point ----------------------#
                html.Div(
                    id="graph-container",
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