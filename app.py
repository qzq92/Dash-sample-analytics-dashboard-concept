# Import packages
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import sys
import logging
from dotenv import load_dotenv
# Load environment variables and logging
load_dotenv(override=True)

from components.banner_component import build_dashboard_banner
from components.map_component import map_component
from components.realtime_weather_page import realtime_weather_page
from components.weather_indices_page import weather_indices_page
from components.transport_page import transport_page
from components.nearby_transport_page import nearby_transport_page
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
from utils.data_download_helper import (
    download_hdb_carpark_csv,
    download_speed_camera_csv,
    clear_csv_files
)
from callbacks.carpark_callback import clear_carpark_locations_cache
from mcp import initialize_mcp_server

# Initialize MCP server for Singapore LTA data
print("Initializing MCP server for Singapore LTA...")
mcp_server_process = initialize_mcp_server()
if mcp_server_process:
    print("MCP server initialized successfully")
else:
    print("Warning: MCP server initialization failed or skipped")

# Clear all CSV files in data directory before downloading
print("Clearing existing CSV files from data directory...")
clear_csv_files()

# Download HDB carpark data from initiate-download API on startup
print("Downloading HDB carpark data from initiate-download API...")
if download_hdb_carpark_csv():
    print("HDB carpark data downloaded successfully")
    # Clear cache so new data will be loaded
    clear_carpark_locations_cache()
else:
    print("Warning: Failed to download HDB carpark data. Using existing CSV file if available.")

# Download speed camera data from initiate-download API on startup
print("Downloading speed camera data from initiate-download API...")
if download_speed_camera_csv():
    print("Speed camera data downloaded successfully")
else:
    print("Warning: Failed to download speed camera data. Using existing CSV file if available.")

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
                # Realtime weather page (hidden by default)
                realtime_weather_page(),
                # Weather indices page (hidden by default)
                weather_indices_page(),
                # Transport page (hidden by default)
                transport_page(),
                # Nearby transport page (hidden by default)
                nearby_transport_page(),
                # Main content area with map and right panel side by side
                html.Div(
                    id="main-content",
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "width": "100%",
                    },
                    children=[
                        html.Div(
                            id="main-content-area",
                            style={
                                "display": "flex",
                                "width": "100%",
                                "gap": "20px",
                                "padding": "20px",
                                "height": "calc(100vh - 100px)",  # Adjusted for header only (search bar moved to map)
                                "alignItems": "stretch",  # Ensure both containers have same height
                                "boxSizing": "border-box",  # Ensure padding is included in width calculation
                            },
                    children=[
                        # Left container - Land Checkpoints
                        html.Div(
                            id="left-container",
                            style={
                                "width": "25%",
                                "display": "flex",
                                "flexDirection": "column",
                                "height": "100%",
                            },
                            children=[
                                html.Div(
                                    id="camera-feeds-section",
                                    style={
                                        "width": "100%",
                                        "height": "100%",
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
                            ]
                        ),
                        # Center container - Map
                        html.Div(
                            id="center-container",
                            style={
                                "width": "50%",
                                "display": "flex",
                                "flexDirection": "column",
                                "height": "100%",
                            },
                            children=[
                                # Map container
                                html.Div(
                                    style={
                                        "width": "100%",
                                        "height": "100%",
                                        "minHeight": "0",
                                    },
                                    children=[
                                        map_component()
                                    ]
                                ),
                            ]
                        ),
                        # Right container - PSI and 24-hour forecast
                        html.Div(
                            id="right-container",
                            style={
                                "width": "25%",
                                "display": "flex",
                                "flexDirection": "column",
                                "gap": "10px",
                                "height": "100%",
                            },
                            children=[
                                # Incidents and Alerts container
                                html.Div(
                                    id="incidents-and-alerts",
                                    style={
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "marginBottom": "10px",
                                    },
                                    children=[
                                        # Lightning and Flood side by side
                                        html.Div(
                                            style={
                                                "display": "flex",
                                                "flexDirection": "row",
                                                "gap": "10px",
                                                "marginBottom": "10px",
                                            },
                                            children=[
                                                # Lightning indicator
                                                html.Div(
                                                    id="main-lightning-indicator-container",
                                                    style={
                                                        "backgroundColor": "#4a5a6a",
                                                        "borderRadius": "8px",
                                                        "padding": "10px",
                                                        "display": "flex",
                                                        "flexDirection": "column",
                                                        "overflow": "hidden",
                                                        "flex": "1",
                                                    },
                                                    children=[
                                                        html.H5(
                                                            "⚡ Lightning Alerts Location (last 5 minute)",
                                                            style={
                                                                "color": "#FFD700",
                                                                "margin": "0 0 5px 0",
                                                                "fontWeight": "600",
                                                                "fontSize": "13px"
                                                            }
                                                        ),
                                                        html.Div(
                                                            id="main-lightning-indicator",
                                                            style={
                                                                "flex": "1",
                                                                "overflowY": "auto",
                                                                "overflowX": "hidden",
                                                                "minHeight": "0",
                                                            },
                                                            children=[
                                                                html.P("Loading...", style={
                                                                    "color": "#999",
                                                                    "fontSize": "12px"
                                                                })
                                                            ]
                                                        )
                                                    ]
                                                ),
                                                # Flood indicator
                                                html.Div(
                                                    id="main-flood-indicator-container",
                                                    style={
                                                        "backgroundColor": "#4a5a6a",
                                                        "borderRadius": "8px",
                                                        "padding": "10px",
                                                        "display": "flex",
                                                        "flexDirection": "column",
                                                        "overflow": "hidden",
                                                        "flex": "1",
                                                    },
                                                    children=[
                                                        html.H5(
                                                            "🌊 Flood Alerts",
                                                            style={
                                                                "color": "#ff6b6b",
                                                                "margin": "0 0 5px 0",
                                                                "fontWeight": "600",
                                                                "fontSize": "13px"
                                                            }
                                                        ),
                                                        html.Div(
                                                            id="main-flood-indicator",
                                                            style={
                                                                "flex": "1",
                                                                "overflowY": "auto",
                                                                "overflowX": "hidden",
                                                                "minHeight": "0",
                                                            },
                                                            children=[
                                                                html.P("No flooding notice at the moment", style={
                                                                    "color": "#999",
                                                                    "fontSize": "12px"
                                                                })
                                                            ]
                                                        )
                                                    ]
                                                ),
                                            ]
                                        ),
                                        # Traffic incidents alert (below)
                                        html.Div(
                                            id="main-traffic-incidents-container",
                                            style={
                                                "backgroundColor": "#4a5a6a",
                                                "borderRadius": "8px",
                                                "padding": "10px",
                                                "display": "flex",
                                                "flexDirection": "column",
                                                "overflow": "hidden",
                                            },
                                            children=[
                                                html.H5(
                                                    "🚦 Traffic Incidents",
                                                    style={
                                                        "color": "#FF9800",
                                                        "margin": "0 0 5px 0",
                                                        "fontWeight": "600",
                                                        "fontSize": "13px"
                                                    }
                                                ),
                                                html.Div(
                                                    id="main-traffic-incidents-indicator",
                                                    style={
                                                        "flex": "1",
                                                        "overflowY": "auto",
                                                        "overflowX": "hidden",
                                                        "minHeight": "0",
                                                    },
                                                    children=[
                                                        html.P("Loading...", style={
                                                            "color": "#999",
                                                            "fontSize": "12px"
                                                        })
                                                    ]
                                                )
                                            ]
                                        ),
                                    ]
                                ),
                                # Taxi count section
                                html.Div(
                                    id="taxi-count-section",
                                    style={
                                        "backgroundColor": "#2c3e50",
                                        "borderRadius": "5px",
                                        "padding": "8px 10px",
                                        "flexShrink": "0",
                                    },
                                    children=[
                                        html.H5(
                                            "Registered Taxis on Ground",
                                            style={
                                                "textAlign": "center",
                                                "margin": "0 0 8px 0",
                                                "color": "#fff",
                                                "fontWeight": "700",
                                                "fontSize": "14px",
                                            }
                                        ),
                                        html.Div(
                                            id="taxi-count-content",
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
                                        "padding": "6px",
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
                # Footer with plotly|dash logo
                html.Div(
                    id="footer",
                    style={
                        "display": "flex",
                        "justifyContent": "flex-end",
                        "padding": "10px 20px",
                        "width": "100%",
                    },
                    children=[
                        html.A(
                            html.Img(
                                id="plotly-logo",
                                src=r"../assets/dash-logo.png",
                                style={"height": "30px"},
                            ),
                            href="https://plotly.com/dash/",
                        ),
                    ],
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