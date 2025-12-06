"""
Component for the realtime weather metrics page.
Displays live weather station data across Singapore.
"""
from dash import html, dcc
import dash_leaflet as dl


def realtime_weather_page():
    """
    Create the realtime weather metrics page layout.
    Features: temperature, rainfall, humidity, wind readings with map.

    Returns:
        HTML Div containing the realtime weather metrics section
    """
    # Singapore center coordinates (Adjusted to frame Singapore nicely)
    sg_center = [1.36, 103.82]
    onemap_tiles_url = "https://www.onemap.gov.sg/maps/tiles/Night/{z}/{x}/{y}.png"
    fixed_zoom = 12

    # Map bounds to restrict view to Singapore area
    sg_bounds = [[1.1304753, 103.6020882], [1.492007, 104.145897]]

    return html.Div(
        id="realtime-weather-page",
        style={
            "display": "none",  # Hidden by default
            "padding": "20px",
            "height": "calc(100vh - 180px)",
            "width": "100%",
        },
        children=[
            # Header
            html.H4(
                "Realtime Weather Metrics",
                style={
                    "textAlign": "center",
                    "margin": "0 0 10px 0",
                    "color": "#fff",
                    "fontWeight": "700"
                }
            ),
            # Status indicators (Lightning and Flood)
            html.Div(
                id="status-indicators",
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "gap": "15px",
                    "margin": "0 0 15px 0",
                    "flexWrap": "wrap",
                },
                children=[
                    html.Div(
                        id="lightning-indicator",
                        style={
                            "display": "inline-flex",
                            "alignItems": "center",
                            "gap": "8px",
                            "padding": "6px 12px",
                            "borderRadius": "6px",
                            "fontSize": "12px",
                            "fontWeight": "600",
                            "backgroundColor": "#3a4a5a",
                        },
                        children=[
                            html.Span("⚡", style={"fontSize": "16px"}),
                            html.Span("Loading...", style={"color": "#888"})
                        ]
                    ),
                    html.Div(
                        id="flood-indicator",
                        style={
                            "display": "inline-flex",
                            "alignItems": "center",
                            "gap": "8px",
                            "padding": "6px 12px",
                            "borderRadius": "6px",
                            "fontSize": "12px",
                            "fontWeight": "600",
                            "backgroundColor": "#3a4a5a",
                        },
                        children=[
                            html.Span("🌊", style={"fontSize": "16px"}),
                            html.Span("No flooding notice at the moment", style={"color": "#888"})
                        ]
                    ),
                ]
            ),
            # Main content: readings grid on left, map on right
            html.Div(
                id="realtime-weather-section",
                style={
                    "display": "flex",
                    "gap": "20px",
                    "height": "calc(100% - 50px)",
                    "maxWidth": "1800px",
                    "margin": "0 auto",
                },
                children=[
                    # Store for active marker type (none by default)
                    dcc.Store(id="active-marker-type", data={'type': None, 'ts': 0}),
                    # Left side: Weather readings panels in 2x2 grid
                    html.Div(
                        id="realtime-readings-panel",
                        style={
                            "flex": "1",
                            "display": "grid",
                            "gridTemplateColumns": "repeat(2, 1fr)",
                            "gridTemplateRows": "repeat(2, 1fr)",
                            "gap": "12px",
                            "minWidth": "400px",
                        },
                        children=[
                            # Temperature readings card
                            html.Div(
                                id="temperature-readings-card",
                                style={
                                    "backgroundColor": "#4a5a6a",
                                    "borderRadius": "8px",
                                    "padding": "10px",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "overflow": "hidden",
                                },
                                children=[
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "alignItems": "center",
                                            "marginBottom": "5px",
                                        },
                                        children=[
                                            html.H5(
                                                "🌡️ Temperature",
                                                style={
                                                    "color": "#FF9800",
                                                    "margin": "0",
                                                    "fontWeight": "600",
                                                    "fontSize": "13px"
                                                }
                                            ),
                                            html.Button(
                                                "📍",
                                                id="toggle-temp-markers",
                                                n_clicks=0,
                                                style={
                                                    "padding": "4px 8px",
                                                    "borderRadius": "4px",
                                                    "border": "2px solid #FF9800",
                                                    "backgroundColor": "transparent",
                                                    "color": "#FF9800",
                                                    "cursor": "pointer",
                                                    "fontSize": "12px",
                                                    "fontWeight": "600",
                                                }
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        id="temperature-readings-content",
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
                                        ],
                                    ),
                                ]
                            ),
                            # Rainfall readings card
                            html.Div(
                                id="rainfall-readings-card",
                                style={
                                    "backgroundColor": "#4a5a6a",
                                    "borderRadius": "8px",
                                    "padding": "10px",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "overflow": "hidden",
                                },
                                children=[
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "alignItems": "center",
                                            "marginBottom": "5px",
                                        },
                                        children=[
                                            html.H5(
                                                "🌧️ Rainfall",
                                                style={
                                                    "color": "#2196F3",
                                                    "margin": "0",
                                                    "fontWeight": "600",
                                                    "fontSize": "13px"
                                                }
                                            ),
                                            html.Button(
                                                "📍",
                                                id="toggle-rainfall-markers",
                                                n_clicks=0,
                                                style={
                                                    "padding": "4px 8px",
                                                    "borderRadius": "4px",
                                                    "border": "2px solid #2196F3",
                                                    "backgroundColor": "transparent",
                                                    "color": "#2196F3",
                                                    "cursor": "pointer",
                                                    "fontSize": "12px",
                                                    "fontWeight": "600",
                                                }
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        id="rainfall-readings-content",
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
                                        ],
                                    ),
                                ]
                            ),
                            # Humidity readings card
                            html.Div(
                                id="humidity-readings-card",
                                style={
                                    "backgroundColor": "#4a5a6a",
                                    "borderRadius": "8px",
                                    "padding": "10px",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "overflow": "hidden",
                                },
                                children=[
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "alignItems": "center",
                                            "marginBottom": "5px",
                                        },
                                        children=[
                                            html.H5(
                                                "💧 Humidity",
                                                style={
                                                    "color": "#00BCD4",
                                                    "margin": "0",
                                                    "fontWeight": "600",
                                                    "fontSize": "13px"
                                                }
                                            ),
                                            html.Button(
                                                "📍",
                                                id="toggle-humidity-markers",
                                                n_clicks=0,
                                                style={
                                                    "padding": "4px 8px",
                                                    "borderRadius": "4px",
                                                    "border": "2px solid #00BCD4",
                                                    "backgroundColor": "transparent",
                                                    "color": "#00BCD4",
                                                    "cursor": "pointer",
                                                    "fontSize": "12px",
                                                    "fontWeight": "600",
                                                }
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        id="humidity-readings-content",
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
                                        ],
                                    ),
                                ]
                            ),
                            # Wind readings card
                            html.Div(
                                id="wind-readings-card",
                                style={
                                    "backgroundColor": "#4a5a6a",
                                    "borderRadius": "8px",
                                    "padding": "10px",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "overflow": "hidden",
                                },
                                children=[
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "alignItems": "center",
                                            "marginBottom": "5px",
                                        },
                                        children=[
                                            html.H5(
                                                "💨 Wind",
                                                style={
                                                    "color": "#9C27B0",
                                                    "margin": "0",
                                                    "fontWeight": "600",
                                                    "fontSize": "13px"
                                                }
                                            ),
                                            html.Button(
                                                "📍",
                                                id="toggle-wind-markers",
                                                n_clicks=0,
                                                style={
                                                    "padding": "4px 8px",
                                                    "borderRadius": "4px",
                                                    "border": "2px solid #9C27B0",
                                                    "backgroundColor": "transparent",
                                                    "color": "#9C27B0",
                                                    "cursor": "pointer",
                                                    "fontSize": "12px",
                                                    "fontWeight": "600",
                                                }
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        id="wind-readings-content",
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
                                        ],
                                    ),
                                ]
                            ),
                        ]
                    ),
                    # Right side: Map with station markers (half width)
                    html.Div(
                        id="realtime-map-panel",
                        style={
                            "flex": "1",
                            "backgroundColor": "#4a5a6a",
                            "borderRadius": "5px",
                            "padding": "10px",
                            "display": "flex",
                            "flexDirection": "column",
                            "minWidth": "400px",
                        },
                        children=[
                            html.H5(
                                "Weather Stations Map",
                                style={
                                    "textAlign": "center",
                                    "margin": "5px 0 10px 0",
                                    "color": "#fff",
                                    "fontWeight": "600",
                                    "fontSize": "14px"
                                }
                            ),
                            html.Div(
                                style={
                                    "flex": "1",
                                    "borderRadius": "5px",
                                    "overflow": "hidden",
                                    "minHeight": "400px",
                                },
                                children=[
                                    dl.Map(
                                        id="realtime-weather-map",
                                        center=sg_center,
                                        zoom=fixed_zoom,
                                        minZoom=fixed_zoom - 1,
                                        maxZoom=fixed_zoom + 3,
                                        maxBounds=sg_bounds,
                                        style={
                                            "width": "100%",
                                            "height": "calc(100vh - 280px)",
                                            "minHeight": "400px",
                                        },
                                        dragging=True,
                                        scrollWheelZoom=True,
                                        zoomControl=True,
                                        children=[
                                            dl.TileLayer(
                                                url=onemap_tiles_url,
                                                attribution='OneMap',
                                                maxNativeZoom=19,
                                            ),
                                            dl.LayerGroup(id="realtime-weather-markers"),
                                            dl.LayerGroup(id="lightning-markers"),
                                            dl.LayerGroup(id="flood-markers"),
                                        ],
                                    )
                                ]
                            ),
                        ]
                    ),
                ]
            ),
        ]
    )
