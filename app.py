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
from callbacks.mrt_callback import register_mrt_callbacks
from callbacks.busstop_callbacks import register_busstop_callbacks
from auth.onemap_api import initialize_onemap_token

# Initialize OneMap API token on application startup
print("Initializing OneMap API authentication...")
if initialize_onemap_token():
    print("OneMap API token initialized successfully")
else:
    print("Warning: Failed to initialize OneMap API token. Some features may not work.")

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
register_mrt_callbacks(app)
register_busstop_callbacks(app)

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
                    style={
                        "display": "flex",
                        "justifyContent": "space-between",
                        "width": "100%",
                        "gap": "20px",
                        "margin": "10px 20px",
                    },
                    children=[
                        # CCTV feeds section (left side, expanded)
                        html.Div(
                            id="camera-feeds-section",
                            children=[
                                html.Div(
                                    id="camera-2701-container",
                                    children=[
                                        html.H5("Causeway", style={"textAlign": "center", "margin": "10px 0", "color": "#fff"}),
                                        html.Div(
                                            style={
                                                "width": "100%",
                                                "height": "calc(50vh - 100px)",
                                                "overflow": "hidden",
                                                "display": "flex",
                                                "alignItems": "center",
                                                "justifyContent": "center",
                                                "backgroundColor": "#000",
                                            },
                                            children=[
                                                html.Img(
                                                    id="camera-feed-2701",
                                                    src="",
                                                    style={
                                                        "width": "100%",
                                                        "height": "100%",
                                                        "objectFit": "cover",
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
                                        "height": "100%",
                                        "padding": "10px",
                                        "verticalAlign": "top",
                                    }
                                ),
                                html.Div(
                                    id="camera-4713-container",
                                    children=[
                                        html.H5("Second Link", style={"textAlign": "center", "margin": "10px 0", "color": "#fff"}),
                                        html.Div(
                                            style={
                                                "width": "100%",
                                                "height": "calc(50vh - 100px)",
                                                "overflow": "hidden",
                                                "display": "flex",
                                                "alignItems": "center",
                                                "justifyContent": "center",
                                                "backgroundColor": "#000",
                                            },
                                            children=[
                                                html.Img(
                                                    id="camera-feed-4713",
                                                    src="",
                                                    style={
                                                        "width": "100%",
                                                        "height": "100%",
                                                        "objectFit": "cover",
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
                                        "height": "100%",
                                        "padding": "10px",
                                        "verticalAlign": "top",
                                    }
                                ),
                            ],
                            style={
                                "backgroundColor": "#000000",
                                "borderRadius": "5px",
                                "padding": "0",
                                "height": "50vh",
                                "display": "flex",
                                "justifyContent": "space-around",
                                "flexWrap": "nowrap",
                                "flex": "1",
                                "minWidth": "0",
                            }
                        ),
                        # Weather forecast section (right side)
                        html.Div(
                            id="weather-forecast-section",
                            children=[
                                html.H4(
                                    "2-Hour Weather Forecast",
                                    style={
                                        "textAlign": "center",
                                        "margin": "10px 0",
                                        "color": "#fff",
                                        "fontWeight": "700"
                                    }
                                ),
                                html.Div(
                                    id="weather-2h-content",
                                    children=[
                                        html.P("Loading...", style={"textAlign": "center", "padding": "20px", "color": "#999"})
                                    ],
                                    style={
                                        "padding": "10px 20px",
                                        "maxHeight": "calc(50vh - 80px)",
                                        "overflowY": "auto",
                                    }
                                ),
                            ],
                            style={
                                "backgroundColor": "#4a5a6a",
                                "borderRadius": "5px",
                                "padding": "10px",
                                "height": "50vh",
                                "flex": "1",
                                "minWidth": "0",
                                "display": "flex",
                                "flexDirection": "column",
                            }
                        ),
                    ]
                ),
                # Interval component to update images and weather periodically
                dcc.Interval(
                    id='interval-component',
                    interval=30*1000,  # Update every 30 seconds
                    n_intervals=0
                ),
                html.Div(
                    id="Map and search bar container",
                    className="row",
                    children=[
                        # Left column for map placement
                        html.Div(
                            id="left-column",
                            className="seven columns",
                            children=[map_component()],  # Map will be updated via callback when search bar value changes
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
                # Three column section for nearest MRT, carpark, and bus stop
                html.Div(
                    id="nearest-facilities-section",
                    style={
                        "display": "flex",
                        "justifyContent": "space-between",
                        "width": "100%",
                        "padding": "20px 40px",
                        "gap": "20px"
                    },
                    children=[
                        # Nearest MRT column
                        html.Div(
                            id="nearest-mrt-column",
                            style={
                                "flex": "1",
                                "backgroundColor": "#2c3e50",
                                "borderRadius": "5px",
                                "padding": "15px",
                                "minHeight": "200px"
                            },
                            children=[
                                html.H4(
                                    "Nearest MRT",
                                    style={
                                        "textAlign": "center",
                                        "marginBottom": "15px",
                                        "color": "#fff",
                                        "fontWeight": "700"
                                    }
                                ),
                                html.Div(
                                    id="nearest-mrt-content",
                                    children=[
                                        html.P(
                                            "Select a location to view nearest MRT stations",
                                            style={
                                                "textAlign": "center",
                                                "color": "#999",
                                                "fontSize": "14px",
                                                "fontStyle": "italic",
                                                "padding": "20px"
                                            }
                                        )
                                    ]
                                )
                            ]
                        ),
                        # Nearest Carpark column
                        html.Div(
                            id="nearest-carpark-column",
                            style={
                                "flex": "1",
                                "backgroundColor": "#2c3e50",
                                "borderRadius": "5px",
                                "padding": "15px",
                                "minHeight": "200px"
                            },
                            children=[
                                html.H4(
                                    "Nearest Carpark",
                                    style={
                                        "textAlign": "center",
                                        "marginBottom": "15px",
                                        "color": "#fff",
                                        "fontWeight": "700"
                                    }
                                ),
                                html.Div(
                                    id="nearest-carpark-content",
                                    children=[
                                        html.P(
                                            "Select a location to view nearest carparks",
                                            style={
                                                "textAlign": "center",
                                                "color": "#999",
                                                "fontSize": "14px",
                                                "fontStyle": "italic",
                                                "padding": "20px"
                                            }
                                        )
                                    ]
                                )
                            ]
                        ),
                        # Nearest Bus Stop column
                        html.Div(
                            id="nearest-bus-stop-column",
                            style={
                                "flex": "1",
                                "backgroundColor": "#2c3e50",
                                "borderRadius": "5px",
                                "padding": "15px",
                                "minHeight": "200px"
                            },
                            children=[
                                html.H4(
                                    "Nearest Bus Stop",
                                    style={
                                        "textAlign": "center",
                                        "marginBottom": "15px",
                                        "color": "#fff",
                                        "fontWeight": "700"
                                    }
                                ),
                                html.Div(
                                    id="nearest-bus-stop-content",
                                    children=[
                                        html.P(
                                            "Select a location to view nearest bus stops",
                                            style={
                                                "textAlign": "center",
                                                "color": "#999",
                                                "fontSize": "14px",
                                                "fontStyle": "italic",
                                                "padding": "20px"
                                            }
                                        )
                                    ]
                                )
                            ]
                        ),
                    ]
                ),
            ],
        ),
    ]
)

if __name__ == '__main__':
    logging.info(sys.version)

    # Enable hot reloading to capture latest changes in code
    # If running locally in Anaconda env:
    if "conda-forge" in sys.version:
        app.run(debug=True, dev_tools_hot_reload=False)
    else:
        app.run(debug=True, dev_tools_hot_reload=False, host='0.0.0.0', port=8050)
    # Set app title
    app.title = "SG Dashboard"