# Import packages
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import sys
import logging
from dotenv import load_dotenv
# Load environment variables and logging
load_dotenv(override=True)

from components.banner_component import build_dashboard_banner
from components.map_component import map_component, show_descriptive_stats, search_bar, nearest_mrt_panel
from components.tab_component import display_tabs
from callbacks.map_callback import register_search_callbacks
from callbacks.traffic_callback import register_camera_feed_callbacks
from callbacks.weather_callback import register_weather_callbacks

# Dash instantiation ---------------------------------------------------------#
app = Dash(__name__,
           meta_tags=[{
               "name": "viewport",
               "content": "width=device-width",
               "initial-scale": "1.0"}],
           external_stylesheets=[dbc.themes.DARKLY],
           suppress_callback_exceptions = True, #
           title="SimpleDashboard Demo"
        )
register_search_callbacks(app)
register_camera_feed_callbacks(app)
register_weather_callbacks(app)

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
                # Combined section for CCTV feeds and Weather forecasts
                html.Div(
                    id="camera-weather-section",
                    children=[
                        # First div: CCTV feeds
                        html.Div(
                            id="camera-feeds-section",
                            children=[
                                html.H3("Traffic Camera Feeds", style={"padding": "10px 20px", "margin": "0"}),
                                html.Div(
                                    id="camera-feeds-container",
                                    children=[
                                        html.Div(
                                            id="camera-2701-container",
                                            children=[
                                                html.H5("Causeway", style={"textAlign": "center", "margin": "10px 0"}),
                                                html.Div(
                                                    style={
                                                        "width": "100%",
                                                        "height": "calc(33.33vh - 140px)",
                                                        "overflow": "hidden",
                                                        "display": "flex",
                                                        "alignItems": "center",
                                                        "justifyContent": "center",
                                                    },
                                                    children=[
                                                        html.Img(
                                                            id="camera-feed-2701",
                                                            src="",
                                                            style={
                                                                "maxWidth": "100%",
                                                                "maxHeight": "100%",
                                                                "objectFit": "contain",
                                                            }
                                                        ),
                                                    ]
                                                ),
                                                html.Div(
                                                    id="camera-2701-metadata",
                                                    style={
                                                        "textAlign": "center",
                                                        "padding": "5px",
                                                        "fontSize": "12px",
                                                        "color": "#ccc",
                                                    }
                                                ),
                                            ],
                                            style={
                                                "display": "inline-block",
                                                "width": "48%",
                                                "height": "calc(33.33vh - 80px)",
                                                "padding": "10px",
                                                "verticalAlign": "top",
                                            }
                                        ),
                                        html.Div(
                                            id="camera-4713-container",
                                            children=[
                                                html.H5("Second Link", style={"textAlign": "center", "margin": "10px 0"}),
                                                html.Div(
                                                    style={
                                                        "width": "100%",
                                                        "height": "calc(33.33vh - 140px)",
                                                        "overflow": "hidden",
                                                        "display": "flex",
                                                        "alignItems": "center",
                                                        "justifyContent": "center",
                                                    },
                                                    children=[
                                                        html.Img(
                                                            id="camera-feed-4713",
                                                            src="",
                                                            style={
                                                                "maxWidth": "100%",
                                                                "maxHeight": "100%",
                                                                "objectFit": "contain",
                                                            }
                                                        ),
                                                    ]
                                                ),
                                                html.Div(
                                                    id="camera-4713-metadata",
                                                    style={
                                                        "textAlign": "center",
                                                        "padding": "5px",
                                                        "fontSize": "12px",
                                                        "color": "#ccc",
                                                    }
                                                ),
                                            ],
                                            style={
                                                "display": "inline-block",
                                                "width": "48%",
                                                "height": "calc(33.33vh - 80px)",
                                                "padding": "10px",
                                                "verticalAlign": "top",
                                            }
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "justifyContent": "space-around",
                                        "padding": "10px 20px",
                                        "height": "calc(33.33vh - 60px)",
                                        "flexWrap": "nowrap",
                                    }
                                ),
                            ],
                            style={
                                "backgroundColor": "#000000",
                                "margin": "10px 20px",
                                "borderRadius": "5px",
                                "padding": "10px 0",
                                "height": "33.33vh",
                                "display": "flex",
                                "flexDirection": "column",
                                "width": "48%",
                                "verticalAlign": "top",
                            }
                        ),
                        # Second div: Weather forecasts
                        html.Div(
                            id="weather-forecast-section",
                            children=[
                                html.H3("Weather Forecast", style={"padding": "10px 20px", "margin": "0"}),
                                html.Div(
                                    id="weather-forecast-container",
                                    children=[
                                        html.Div(
                                            id="weather-2h-container",
                                            children=[
                                                html.H4("2-Hour Forecast", style={"textAlign": "center", "margin": "10px 0"}),
                                                html.Div(
                                                    id="weather-2h-content",
                                                    children=[
                                                        html.P("Loading...", style={"textAlign": "center", "padding": "20px"})
                                                    ],
                                                    style={
                                                        "height": "calc(33.33vh - 120px)",
                                                        "overflowY": "auto",
                                                        "padding": "10px",
                                                    }
                                                ),
                                            ],
                                            style={
                                                "display": "inline-block",
                                                "width": "48%",
                                                "height": "calc(33.33vh - 80px)",
                                                "padding": "10px",
                                                "verticalAlign": "top",
                                            }
                                        ),
                                        html.Div(
                                            id="weather-24h-container",
                                            children=[
                                                html.H4("24-Hour Forecast", style={"textAlign": "center", "margin": "10px 0"}),
                                                html.Div(
                                                    id="weather-24h-content",
                                                    children=[
                                                        html.P("Loading...", style={"textAlign": "center", "padding": "20px"})
                                                    ],
                                                    style={
                                                        "height": "calc(33.33vh - 120px)",
                                                        "overflowY": "auto",
                                                        "padding": "10px",
                                                    }
                                                ),
                                            ],
                                            style={
                                                "display": "inline-block",
                                                "width": "48%",
                                                "height": "calc(33.33vh - 80px)",
                                                "padding": "10px",
                                                "verticalAlign": "top",
                                            }
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "justifyContent": "space-around",
                                        "padding": "10px 20px",
                                        "height": "calc(33.33vh - 60px)",
                                        "flexWrap": "nowrap",
                                    }
                                ),
                            ],
                            style={
                                "backgroundColor": "#2C3E50",
                                "margin": "10px 20px",
                                "borderRadius": "5px",
                                "padding": "10px 0",
                                "height": "33.33vh",
                                "display": "flex",
                                "flexDirection": "column",
                                "width": "48%",
                                "verticalAlign": "top",
                            }
                        ),
                        # Interval component to update images and weather periodically
                        dcc.Interval(
                            id='interval-component',
                            interval=30*1000,  # Update every 30 seconds
                            n_intervals=0
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justifyContent": "space-between",
                        "width": "100%",
                    }
                ),
                html.Div(
                    className="row",
                    children=[
                        # Left column for map placement
                        html.Div(
                            id="left-column",
                            className="seven columns",
                            children=[map_component()],
                            style={
                                "display": "inline-block",
                                "padding": "20px 10px 10px 40px",
                                "width": "59%",
                            },
                        ),
                        # Right column for Information around the selected point ----------------------#
                        html.Div(
                            id="Search-bar-container",
                            # Right column for map
                            children= [search_bar(),
                                nearest_mrt_panel(),
                                # Next row
                                #show_descriptive_stats(),
                            ],
                            style={
                                "display": "inline-block",
                                "padding": "20px 20px 10px 10px",
                                "width": "39%",
                            },
                        ),
                    ],
                ),
            ],
        ),
    ]
)

if __name__ == '__main__':
    logging.info(sys.version)

    # If running locally in Anaconda env:
    if "conda-forge" in sys.version:
        app.run(debug=True)
    else:
        app.run(debug=False, host='0.0.0.0', port=8050)
    # Set app title
    app.title = "SG Dashboard"