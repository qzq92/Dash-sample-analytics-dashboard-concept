"""
Component for the realtime weather metrics page.
Displays live weather station data across Singapore.
"""
from dash import html, dcc
import dash_leaflet as dl
from utils.map_utils import get_onemap_attribution


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
    fixed_zoom = 11  # Zoomed out 1 level from previous (was 12)
    onemap_attribution = get_onemap_attribution()

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
            # Main content: readings grid on left, map and indicators on right
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
                    # Left side: Weather readings panels in 2x2 grid (3/10 width)
                    html.Div(
                        id="realtime-readings-panel",
                        style={
                            "flex": "3",
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "12px",
                            "minWidth": "300px",
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
                                    "gap": "8px",
                                },
                                children=[
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "flexDirection": "row",
                                            "alignItems": "center",
                                            "justifyContent": "space-between",
                                        },
                                        children=[
                                            html.Span(
                                                "🌡️ Temperature",
                                                style={
                                                    "color": "#FF9800",
                                                    "fontWeight": "600",
                                                    "fontSize": "13px"
                                                }
                                            ),
                                            html.Div(
                                                id="temperature-readings-content",
                                                children=[
                                                    html.Span("Loading...", style={
                                                        "color": "#999",
                                                        "fontSize": "12px"
                                                    })
                                                ],
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        id="temp-sensor-values",
                                        style={
                                            "display": "none",
                                            "backgroundColor": "#3a4a5a",
                                            "borderRadius": "5px",
                                            "padding": "10px",
                                            "maxHeight": "200px",
                                            "overflowY": "auto",
                                        },
                                        children=[
                                            html.Div(id="temp-sensor-content", children=[
                                                html.P("Loading...", style={
                                                    "color": "#999",
                                                    "fontSize": "12px",
                                                    "textAlign": "center"
                                                })
                                            ])
                                        ]
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
                                    "gap": "8px",
                                },
                                children=[
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "flexDirection": "row",
                                            "alignItems": "center",
                                            "justifyContent": "space-between",
                                        },
                                        children=[
                                            html.Span(
                                                "🌧️ Rainfall",
                                                style={
                                                    "color": "#2196F3",
                                                    "fontWeight": "600",
                                                    "fontSize": "13px"
                                                }
                                            ),
                                            html.Div(
                                                id="rainfall-readings-content",
                                                children=[
                                                    html.Span("Loading...", style={
                                                        "color": "#999",
                                                        "fontSize": "12px"
                                                    })
                                                ],
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        id="rainfall-sensor-values",
                                        style={
                                            "display": "none",
                                            "backgroundColor": "#3a4a5a",
                                            "borderRadius": "5px",
                                            "padding": "10px",
                                            "maxHeight": "200px",
                                            "overflowY": "auto",
                                        },
                                        children=[
                                            html.Div(id="rainfall-sensor-content", children=[
                                                html.P("Loading...", style={
                                                    "color": "#999",
                                                    "fontSize": "12px",
                                                    "textAlign": "center"
                                                })
                                            ])
                                        ]
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
                                    "gap": "8px",
                                },
                                children=[
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "flexDirection": "row",
                                            "alignItems": "center",
                                            "justifyContent": "space-between",
                                        },
                                        children=[
                                            html.Span(
                                                "💧 Humidity",
                                                style={
                                                    "color": "#00BCD4",
                                                    "fontWeight": "600",
                                                    "fontSize": "13px"
                                                }
                                            ),
                                            html.Div(
                                                id="humidity-readings-content",
                                                children=[
                                                    html.Span("Loading...", style={
                                                        "color": "#999",
                                                        "fontSize": "12px"
                                                    })
                                                ],
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        id="humidity-sensor-values",
                                        style={
                                            "display": "none",
                                            "backgroundColor": "#3a4a5a",
                                            "borderRadius": "5px",
                                            "padding": "10px",
                                            "maxHeight": "200px",
                                            "overflowY": "auto",
                                        },
                                        children=[
                                            html.Div(id="humidity-sensor-content", children=[
                                                html.P("Loading...", style={
                                                    "color": "#999",
                                                    "fontSize": "12px",
                                                    "textAlign": "center"
                                                })
                                            ])
                                        ]
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
                                    "gap": "8px",
                                },
                                children=[
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "flexDirection": "row",
                                            "alignItems": "center",
                                            "justifyContent": "space-between",
                                        },
                                        children=[
                                            html.Span(
                                                "💨 Wind",
                                                style={
                                                    "color": "#4CAF50",
                                                    "fontWeight": "600",
                                                    "fontSize": "13px"
                                                }
                                            ),
                                            html.Div(
                                                id="wind-readings-content",
                                                children=[
                                                    html.Span("Loading...", style={
                                                        "color": "#999",
                                                        "fontSize": "12px"
                                                    })
                                                ],
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        id="wind-sensor-values",
                                        style={
                                            "display": "none",
                                            "backgroundColor": "#3a4a5a",
                                            "borderRadius": "5px",
                                            "padding": "10px",
                                            "maxHeight": "200px",
                                            "overflowY": "auto",
                                        },
                                        children=[
                                            html.Div(id="wind-sensor-content", children=[
                                                html.P("Loading...", style={
                                                    "color": "#999",
                                                    "fontSize": "12px",
                                                    "textAlign": "center"
                                                })
                                            ])
                                        ]
                                    ),
                                ]
                            ),
                        ]
                    ),
                    # Right side: Map with station markers and indicators (7/10 width total)
                    html.Div(
                        style={
                            "flex": "7",
                            "display": "flex",
                            "gap": "10px",
                            "minWidth": "600px",
                        },
                        children=[
                            # Map panel (2/3 of right side)
                            html.Div(
                                id="realtime-map-panel",
                                style={
                                    "flex": "2",
                                    "backgroundColor": "#4a5a6a",
                                    "borderRadius": "5px",
                                    "padding": "10px",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "position": "relative",
                                },
                                children=[
                                    # Header with reading type toggles and 2H forecast toggle
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "alignItems": "center",
                                            "margin": "0 0 10px 0",
                                        },
                                        children=[
                                            html.Div(
                                                style={
                                                    "display": "flex",
                                                    "alignItems": "center",
                                                    "gap": "8px",
                                                    "flexWrap": "wrap",
                                                },
                                                children=[
                                                    html.Button(
                                                        "🌡️ Temperature",
                                                        id="toggle-temp-readings",
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
                                                    html.Button(
                                                        "🌧️ Rainfall",
                                                        id="toggle-rainfall-readings",
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
                                                    html.Button(
                                                        "💧 Humidity",
                                                        id="toggle-humidity-readings",
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
                                                    html.Button(
                                                        "💨 Wind",
                                                        id="toggle-wind-readings",
                                                        n_clicks=0,
                                                        style={
                                                            "padding": "4px 8px",
                                                            "borderRadius": "4px",
                                                            "border": "2px solid #4CAF50",
                                                            "backgroundColor": "transparent",
                                                            "color": "#4CAF50",
                                                            "cursor": "pointer",
                                                            "fontSize": "12px",
                                                            "fontWeight": "600",
                                                        }
                                                    ),
                                                ]
                                            ),
                                            html.Button(
                                                "🌦️ Show 2H Forecast",
                                                id="toggle-2h-forecast",
                                                n_clicks=0,
                                                style={
                                                    "padding": "6px 12px",
                                                    "borderRadius": "6px",
                                                    "border": "2px solid #60a5fa",
                                                    "backgroundColor": "transparent",
                                                    "color": "#60a5fa",
                                                    "cursor": "pointer",
                                                    "fontSize": "12px",
                                                    "fontWeight": "600",
                                                }
                                            ),
                                        ]
                                    ),
                                    # Map
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
                                                    "height": "100%",
                                                    "minHeight": "400px",
                                                },
                                                dragging=True,
                                                scrollWheelZoom=True,
                                                zoomControl=True,
                                                children=[
                                                    dl.TileLayer(
                                                        url=onemap_tiles_url,
                                                        attribution=onemap_attribution,
                                                        maxNativeZoom=19,
                                                    ),
                                                    dl.LayerGroup(id="realtime-weather-markers"),
                                                    dl.LayerGroup(id="lightning-markers"),
                                                    dl.LayerGroup(id="flood-markers"),
                                                    dl.LayerGroup(id="weather-2h-markers"),
                                                    dl.LayerGroup(id="sensor-markers"),
                                                ],
                                            )
                                        ]
                                    ),
                                ]
                            ),
                            # Indicators panel (Lightning and Flood in single column) (1/3 of right side)
                            html.Div(
                                style={
                                    "flex": "1",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "gap": "10px",
                                    "height": "100%",
                                },
                                children=[
                                    # Alerts title
                                    html.H5(
                                        "Alerts",
                                        style={
                                            "color": "#fff",
                                            "margin": "0 0 10px 0",
                                            "fontWeight": "600",
                                            "fontSize": "14px"
                                        }
                                    ),
                                    # Lightning indicator card (mimics metrics design)
                                    html.Div(
                                        id="lightning-indicator-container",
                                        style={
                                            "flex": "1",
                                            "backgroundColor": "#4a5a6a",
                                            "borderRadius": "8px",
                                            "padding": "10px",
                                            "display": "flex",
                                            "flexDirection": "column",
                                            "overflow": "hidden",
                                        },
                                        children=[
                                            html.H5(
                                                "⚡ Lightning",
                                                style={
                                                    "color": "#FFD700",
                                                    "margin": "0 0 5px 0",
                                                    "fontWeight": "600",
                                                    "fontSize": "13px"
                                                }
                                            ),
                                            html.Div(
                                                id="lightning-indicator",
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
                                    # Flood indicator card (mimics metrics design)
                                    html.Div(
                                        id="flood-indicator-container",
                                        style={
                                            "flex": "1",
                                            "backgroundColor": "#4a5a6a",
                                            "borderRadius": "8px",
                                            "padding": "10px",
                                            "display": "flex",
                                            "flexDirection": "column",
                                            "overflow": "hidden",
                                        },
                                        children=[
                                            html.H5(
                                                "🌊 Flood Alert",
                                                style={
                                                    "color": "#ff6b6b",
                                                    "margin": "0 0 5px 0",
                                                    "fontWeight": "600",
                                                    "fontSize": "13px"
                                                }
                                            ),
                                            html.Div(
                                                id="flood-indicator",
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
                                    # Wind speed legend (underneath alerts)
                                    html.Div(
                                        id="wind-speed-legend",
                                        style={
                                            "marginTop": "10px",
                                        },
                                        children=[
                                            html.P("Loading...", style={
                                                "color": "#999",
                                                "fontSize": "11px",
                                                "textAlign": "center",
                                                "margin": "0"
                                            })
                                        ]
                                    ),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
            # Store for 2H forecast toggle state
            dcc.Store(id="2h-forecast-toggle-state", data=False),
            # Interval for auto-refresh
            dcc.Interval(
                id='realtime-weather-interval',
                interval=60*1000,  # Update every 60 seconds
                n_intervals=0
            ),
        ]
    )
