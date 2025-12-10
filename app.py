# Import packages
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import sys
import logging
from dotenv import load_dotenv
# Load environment variables and logging
load_dotenv(override=True)

from components.banner_component import build_dashboard_banner
from components.map_component import map_component, search_bar
from components.weather_page import weather_forecast_page
from components.realtime_weather_page import realtime_weather_page
from components.weather_indices_page import weather_indices_page
from components.transport_page import transport_page
from callbacks.map_callback import register_search_callbacks
from callbacks.traffic_callback import register_camera_feed_callbacks
from callbacks.weather_callback import register_weather_callbacks
from callbacks.realtime_weather_callback import register_realtime_weather_callbacks
from callbacks.weather_indices_callback import register_weather_indices_callbacks
from callbacks.mrt_callback import register_mrt_callbacks
from callbacks.busstop_callbacks import register_busstop_callbacks
from callbacks.carpark_callback import register_carpark_callbacks
from callbacks.tab_navigation_callback import register_tab_navigation_callback
from callbacks.transport_callback import register_transport_callbacks
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
register_realtime_weather_callbacks(app)
register_weather_indices_callbacks(app)
register_mrt_callbacks(app)
register_busstop_callbacks(app)
register_carpark_callbacks(app)
register_transport_callbacks(app)
register_tab_navigation_callback(app)

# Dashboard app layout ------------------------------------------------------#
app.layout = html.Div(
    id="root",
    children=[
        # Header/Banner -------------------------------------------------#
        html.Div(
            id="header",
            children=[
                build_dashboard_banner(),
            ],
        ),
        # Hidden search bar section div (for tab navigation callback compatibility)
        html.Div(
            id="search-bar-section",
            style={"display": "none"},
        ),

        # App Container ------------------------------------------#
        html.Div(
            id="app-container",
            children=[
                # Weather forecast page (hidden by default, shown when weather tab is selected)
                weather_forecast_page(),
                # Realtime weather page (hidden by default)
                realtime_weather_page(),
                # Weather indices page (hidden by default)
                weather_indices_page(),
                # Transport page (hidden by default)
                transport_page(),
                # Main content area with map and right panel side by side
                html.Div(
                    id="main-content-area",
                    style={
                        "display": "flex",
                        "width": "100%",
                        "gap": "20px",
                        "padding": "10px 20px",
                        "height": "calc(100vh - 100px)",  # Adjusted for header only (search bar moved to map)
                        "alignItems": "stretch",  # Ensure both containers have same height
                    },
                    children=[
                        # Left container - Search bar and Map
                        html.Div(
                            id="left-container",
                            style={
                                "width": "50%",
                                "display": "flex",
                                "flexDirection": "column",
                                "height": "100%",
                                "gap": "10px",
                            },
                            children=[
                                # Search bar above map
                                html.Div(
                                    id="map-search-bar",
                                    style={
                                        "flexShrink": "0",
                                    },
                                    children=[
                                        search_bar()
                                    ]
                                ),
                                # Map container
                                html.Div(
                                    style={
                                        "flex": "1",
                                        "minHeight": "0",
                                    },
                                    children=[
                                        map_component()
                                    ]
                                ),
                            ]
                        ),
                        # Right container - CCTV and Weather side by side at top, Nearest facilities at bottom
                        html.Div(
                            id="right-container",
                            style={
                                "width": "50%",
                                "display": "flex",
                                "flexDirection": "column",
                                "gap": "20px",
                                "height": "100%",
                            },
                            children=[
                                # Top row: CCTV feeds and 24-hour Weather forecast side by side
                                html.Div(
                                    id="top-right-section",
                                    style={
                                        "display": "flex",
                                        "gap": "20px",
                                        "flex": "1",
                                        "minHeight": "0",
                                    },
                                    children=[
                                        # CCTV feeds section (left side)
                                        html.Div(
                                            id="camera-feeds-section",
                                            style={
                                                "flex": "1",
                                                "backgroundColor": "#000000",
                                                "borderRadius": "5px",
                                                "padding": "0",
                                                "display": "flex",
                                                "flexDirection": "column",
                                                "justifyContent": "space-around",
                                                "flexWrap": "nowrap",
                                            },
                                            children=[
                                                html.H4(
                                                    "Land Checkpoints",
                                                    style={
                                                        "textAlign": "center",
                                                        "margin": "5px 0 5px 0",
                                                        "color": "#fff",
                                                        "fontWeight": "700",
                                                        "fontSize": "18px"
                                                    }
                                                ),
                                                html.Div(
                                                    id="camera-2701-container",
                                                    children=[
                                                        html.Div(
                                                            style={
                                                                "width": "100%",
                                                                "flex": "1",
                                                                "minHeight": "0",
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
                                                                "padding": "5px 0",
                                                                "fontSize": "12px",
                                                                "color": "#ccc",
                                                            }
                                                        ),
                                                    ],
                                                    style={
                                                        "flex": "1",
                                                        "padding": "10px",
                                                        "display": "flex",
                                                        "flexDirection": "column",
                                                        "minHeight": "0",
                                                    }
                                                ),
                                                html.Div(
                                                    id="camera-4713-container",
                                                    children=[
                                                        html.Div(
                                                            style={
                                                                "width": "100%",
                                                                "flex": "1",
                                                                "minHeight": "0",
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
                                                                "padding": "5px 0",
                                                                "fontSize": "12px",
                                                                "color": "#ccc",
                                                            }
                                                        ),
                                                    ],
                                                    style={
                                                        "flex": "1",
                                                        "padding": "10px",
                                                        "display": "flex",
                                                        "flexDirection": "column",
                                                        "minHeight": "0",
                                                    }
                                                ),
                                            ]
                                        ),
                                        # Right column: PSI and 24-hour forecast stacked
                                        html.Div(
                                            id="right-info-column",
                                            style={
                                                "flex": "1",
                                                "display": "flex",
                                                "flexDirection": "column",
                                                "gap": "10px",
                                                "minHeight": "0",
                                            },
                                            children=[
                                                # Average PSI section (top)
                                                html.Div(
                                                    id="psi-24h-section",
                                                    style={
                                                        "backgroundColor": "#2c3e50",
                                                        "borderRadius": "5px",
                                                        "padding": "8px 10px",
                                                        "flexShrink": "0",
                                                    },
                                                    children=[
                                                        html.H5(
                                                            "Average PSI Reading",
                                                            style={
                                                                "textAlign": "center",
                                                                "margin": "0 0 8px 0",
                                                                "color": "#fff",
                                                                "fontWeight": "700",
                                                                "fontSize": "14px",
                                                            }
                                                        ),
                                                        html.Div(
                                                            id="psi-24h-content",
                                                            children=[
                                                                html.P("Loading...", style={"textAlign": "center", "color": "#999", "fontSize": "12px"})
                                                            ],
                                                        ),
                                                    ]
                                                ),
                                                # 24-hour Weather forecast section (bottom)
                                                html.Div(
                                                    id="weather-forecast-24h-section",
                                                    style={
                                                        "flex": "1",
                                                        "backgroundColor": "#4a5a6a",
                                                        "borderRadius": "5px",
                                                        "padding": "10px",
                                                        "display": "flex",
                                                        "flexDirection": "column",
                                                        "overflow": "hidden",
                                                        "minHeight": "0",
                                                    },
                                                    children=[
                                                        html.H5(
                                                            "Next 24-Hour Forecast",
                                                            style={
                                                                "textAlign": "center",
                                                                "margin": "0 0 8px 0",
                                                                "color": "#fff",
                                                                "fontWeight": "700",
                                                                "flexShrink": "0",
                                                                "fontSize": "14px",
                                                            }
                                                        ),
                                                        html.Div(
                                                            id="weather-24h-content",
                                                            children=[
                                                                html.P("Loading...", style={"textAlign": "center",  "color": "#999"})
                                                            ],
                                                            style={
                                                                "flex": "1",
                                                                "display": "flex",
                                                                "alignItems": "center",
                                                                "justifyContent": "center",
                                                                "overflow": "hidden",
                                                                "minHeight": "0",
                                                                "minWidth": "0",
                                                            }
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),
                                    ]
                                ),
                                # Bottom section: Nearest MRT, Carpark, and Bus Stop
                                html.Div(
                                    id="nearest-facilities-section",
                                    style={
                                        "display": "flex",
                                        "justifyContent": "space-between",
                                        "width": "100%",
                                        "gap": "20px",
                                        "flex": "1",
                                        "minHeight": "0",
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
                                                    "Nearest MRT (1KM radius)",
                                                    style={
                                                        "textAlign": "center",
                                                        "marginBottom": "10px",
                                                        "color": "#fff",
                                                        "fontWeight": "700",
                                                        "fontSize": "14px"
                                                    }
                                                ),
                                                html.Div(
                                                    id="nearest-mrt-content",
                                                    style={
                                                        "overflowY": "auto",
                                                        "overflowX": "hidden",
                                                        "maxHeight": "calc(100% - 40px)"
                                                    },
                                                    children=[
                                                        html.P(
                                                            "Select a location to view nearest MRT stations",
                                                            style={
                                                                "textAlign": "center",
                                                                "color": "#999",
                                                                "fontSize": "12px",
                                                                "fontStyle": "italic",
                                                                "padding": "15px"
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
                                                    "Top 5 Nearest HDB Carparks",
                                                    style={
                                                        "textAlign": "center",
                                                        "marginBottom": "10px",
                                                        "color": "#fff",
                                                        "fontWeight": "700",
                                                        "fontSize": "14px"
                                                    }
                                                ),
                                                html.Div(
                                                    id="nearest-carpark-content",
                                                    style={
                                                        "overflowY": "auto",
                                                        "overflowX": "hidden",
                                                        "maxHeight": "calc(100% - 40px)"
                                                    },
                                                    children=[
                                                        html.P(
                                                            "Select a location to view nearest carparks",
                                                            style={
                                                                "textAlign": "center",
                                                                "color": "#999",
                                                                "fontSize": "12px",
                                                                "fontStyle": "italic",
                                                                "padding": "15px"
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
                                                    "Top 5 Nearest Bus Stops",
                                                    style={
                                                        "textAlign": "center",
                                                        "marginBottom": "10px",
                                                        "color": "#fff",
                                                        "fontWeight": "700",
                                                        "fontSize": "14px"
                                                    }
                                                ),
                                                html.Div(
                                                    id="nearest-bus-stop-content",
                                                    style={
                                                        "overflowY": "auto",
                                                        "overflowX": "hidden",
                                                        "maxHeight": "calc(100% - 40px)"
                                                    },
                                                    children=[
                                                        html.P(
                                                            "Select a location to view nearest bus stops",
                                                            style={
                                                                "textAlign": "center",
                                                                "color": "#999",
                                                                "fontSize": "12px",
                                                                "fontStyle": "italic",
                                                                "padding": "15px"
                                                            }
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),
                # Interval component to update images and weather periodically
                dcc.Interval(
                    id='interval-component',
                    interval=30*1000,  # Update every 30 seconds
                    n_intervals=0
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