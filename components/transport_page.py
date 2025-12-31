"""
Component for the Transport Information page.
Displays transport-related information including taxi availability.
"""
from dash import html, dcc
import dash_leaflet as dl
from utils.map_utils import (
    get_onemap_attribution,
    SG_MAP_CENTER,
    SG_MAP_DEFAULT_ZOOM,
    SG_MAP_BOUNDS,
    ONEMAP_TILES_URL
)


def transport_page():
    """
    Create the Transport Information page layout.
    Features: Taxi availability display with map.

    Returns:
        HTML Div containing the Transport Information section
    """
    # Use standardized map configuration
    sg_center = SG_MAP_CENTER
    onemap_tiles_url = ONEMAP_TILES_URL
    fixed_zoom = SG_MAP_DEFAULT_ZOOM
    onemap_attribution = get_onemap_attribution()
    sg_bounds = SG_MAP_BOUNDS

    return html.Div(
        id="transport-page",
        style={
            "display": "none",  # Hidden by default
            "padding": "1.25rem",
            "height": "calc(100vh - 7.5rem)",
            "width": "100%",
        },
        children=[
            # Main content container
            html.Div(
                id="transport-content",
                style={
                    "display": "flex",
                    "gap": "1.25rem",
                    "height": "calc(100% - 3.125rem)",
                    "maxWidth": "112.5rem",
                    "margin": "0 auto",
                },
                children=[
                    # Left side: Transport info panel
                    html.Div(
                        id="transport-info-panel",
                        style={
                            "flex": "1",
                            "minWidth": "18.75rem",
                            "maxWidth": "25rem",
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "0.9375rem",
                        },
                        children=[
                            # Taxi Availability card
                            html.Div(
                                id="taxi-availability-card",
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
                                                "🚕 Current Taxi Locations/Stands",
                                                style={
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                    "fontSize": "13px"
                                                }
                                            ),
                                            html.Div(
                                                id="taxi-count-value",
                                                style={
                                                    "color": "#FFD700",
                                                    "fontSize": "1.125rem",
                                                    "fontWeight": "700",
                                                },
                                                children=[
                                                    html.Div(
                                                        html.Span("--", style={"color": "#999"}),
                                                        style={
                                                            "backgroundColor": "rgb(58, 74, 90)",
                                                            "padding": "4px 8px",
                                                            "borderRadius": "4px",
                                                        }
                                                    )
                                                ]
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            # CCTV Traffic Cameras card
                            html.Div(
                                id="cctv-card",
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
                                                "📹 LTA Traffic Cameras",
                                                style={
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                    "fontSize": "13px"
                                                }
                                            ),
                                            html.Div(
                                                id="cctv-count-value",
                                                style={
                                                    "color": "#4CAF50",
                                                    "fontSize": "1.125rem",
                                                    "fontWeight": "700",
                                                },
                                                children=[
                                                    html.Div(
                                                        html.Span("--", style={"color": "#999"}),
                                                        style={
                                                            "backgroundColor": "rgb(58, 74, 90)",
                                                            "padding": "4px 8px",
                                                            "borderRadius": "4px",
                                                        }
                                                    )
                                                ]
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            # SPF Speed Camera card
                            html.Div(
                                id="speed-camera-card",
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
                                                "📸 SPF Speed Camera",
                                                style={
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                    "fontSize": "13px"
                                                }
                                            ),
                                            html.Div(
                                                id="speed-camera-count-value",
                                                style={
                                                    "color": "#A5D6A7",
                                                    "fontSize": "1.125rem",
                                                    "fontWeight": "700",
                                                },
                                                children=[
                                                    html.Div(
                                                        html.Span("--", style={"color": "#999"}),
                                                        style={
                                                            "backgroundColor": "rgb(58, 74, 90)",
                                                            "padding": "4px 8px",
                                                            "borderRadius": "4px",
                                                        }
                                                    )
                                                ]
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            # ERP Gantry card
                            html.Div(
                                id="erp-card",
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
                                                "🚧 ERP Gantries",
                                                style={
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                    "fontSize": "13px"
                                                }
                                            ),
                                            html.Div(
                                                id="erp-count-value",
                                                style={
                                                    "color": "#FF6B6B",
                                                    "fontSize": "1.125rem",
                                                    "fontWeight": "700",
                                                },
                                                children=[
                                                    html.Div(
                                                        html.Span("--", style={"color": "#999"}),
                                                        style={
                                                            "backgroundColor": "rgb(58, 74, 90)",
                                                            "padding": "4px 8px",
                                                            "borderRadius": "4px",
                                                        }
                                                    )
                                                ]
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            # Bicycle Parking card
                            html.Div(
                                id="bicycle-parking-card",
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
                                                "🚴 Bicycle Parking (Sheltered/Unsheltered)",
                                                style={
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                    "fontSize": "13px"
                                                }
                                            ),
                                            html.Div(
                                                id="bicycle-parking-count-value",
                                                style={
                                                    "color": "#9C27B0",
                                                    "fontSize": "1.125rem",
                                                    "fontWeight": "700",
                                                },
                                                children=[
                                                    html.Div(
                                                        html.Span("--/--", style={"color": "#999"}),
                                                        style={
                                                            "backgroundColor": "rgb(58, 74, 90)",
                                                            "padding": "4px 8px",
                                                            "borderRadius": "4px",
                                                        }
                                                    )
                                                ]
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            # VMS card
                            html.Div(
                                id="vms-card",
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
                                                "📺 VMS Display boards",
                                                style={
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                    "fontSize": "13px"
                                                }
                                            ),
                                            html.Div(
                                                id="vms-count-value",
                                                style={
                                                    "color": "#C0C0C0",
                                                    "fontSize": "1.125rem",
                                                    "fontWeight": "700",
                                                },
                                                children=[
                                                    html.Div(
                                                        html.Span("--", style={"color": "#999"}),
                                                        style={
                                                            "backgroundColor": "rgb(58, 74, 90)",
                                                            "padding": "4px 8px",
                                                            "borderRadius": "4px",
                                                        }
                                                    )
                                                ]
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            # Bus Stops card
                            html.Div(
                                id="bus-stops-card",
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
                                                "🚌 Bus Stops",
                                                style={
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                    "fontSize": "13px"
                                                }
                                            ),
                                            html.Div(
                                                id="bus-stops-count-value",
                                                style={
                                                    "color": "#4169E1",
                                                    "fontSize": "1.125rem",
                                                    "fontWeight": "700",
                                                },
                                                children=[
                                                    html.Div(
                                                        html.Span("--", style={"color": "#999"}),
                                                        style={
                                                            "backgroundColor": "rgb(58, 74, 90)",
                                                            "padding": "4px 8px",
                                                            "borderRadius": "4px",
                                                        }
                                                    )
                                                ]
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            # Traffic Incidents card
                            html.Div(
                                id="traffic-incidents-card",
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
                                                "🚦 Traffic Incidents",
                                                style={
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                    "fontSize": "13px"
                                                }
                                            ),
                                            html.Div(
                                                id="traffic-incidents-count-value",
                                                style={
                                                    "color": "#FF9800",
                                                    "fontSize": "1.125rem",
                                                    "fontWeight": "700",
                                                },
                                                children=[
                                                    html.Div(
                                                        html.Span("--", style={"color": "#999"}),
                                                        style={
                                                            "backgroundColor": "rgb(58, 74, 90)",
                                                            "padding": "4px 8px",
                                                            "borderRadius": "4px",
                                                        }
                                                    )
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        id="traffic-incidents-messages",
                                        style={
                                            "maxHeight": "150px",
                                            "overflowY": "auto",
                                            "display": "none",
                                        }
                                    ),
                                ]
                            ),
                        ]
                    ),
                    # Middle: Map
                    html.Div(
                        id="transport-map-panel",
                        style={
                            "flex": "2",
                            "minWidth": "31.25rem",
                            "backgroundColor": "#1a2a3a",
                            "borderRadius": "0.5rem",
                            "overflow": "hidden",
                            "display": "flex",
                            "flexDirection": "column",
                        },
                        children=[
                            # Toggle buttons container above map
                            html.Div(
                                id="transport-toggle-buttons-container",
                                style={
                                    "display": "flex",
                                    "flexDirection": "row",
                                    "gap": "0.625rem",
                                    "padding": "0.9375rem",
                                    "backgroundColor": "#2c3e50",
                                    "borderRadius": "0.5rem 0.5rem 0 0",
                                    "flexWrap": "wrap",
                                    "justifyContent": "flex-start",
                                    "alignItems": "center",
                                },
                                children=[
                                    html.Button(
                                        "Show Current Taxi Locations/Stands",
                                        id="taxi-toggle-btn",
                                        n_clicks=0,
                                        style={
                                            "backgroundColor": "transparent",
                                            "border": "2px solid #FFD700",
                                            "borderRadius": "4px",
                                            "color": "#FFD700",
                                            "cursor": "pointer",
                                            "padding": "4px 10px",
                                            "fontSize": "12px",
                                            "fontWeight": "600",
                                        },
                                    ),
                                    html.Button(
                                        "Show LTA Traffic Cameras Location",
                                        id="cctv-toggle-btn",
                                        n_clicks=0,
                                        style={
                                            "backgroundColor": "transparent",
                                            "border": "2px solid #4CAF50",
                                            "borderRadius": "4px",
                                            "color": "#4CAF50",
                                            "cursor": "pointer",
                                            "padding": "4px 10px",
                                            "fontSize": "12px",
                                            "fontWeight": "600",
                                        },
                                    ),
                                    html.Button(
                                        "Show ERP Gantries Location",
                                        id="erp-toggle-btn",
                                        n_clicks=0,
                                        style={
                                            "backgroundColor": "transparent",
                                            "border": "2px solid #FF6B6B",
                                            "borderRadius": "4px",
                                            "color": "#FF6B6B",
                                            "cursor": "pointer",
                                            "padding": "4px 10px",
                                            "fontSize": "12px",
                                            "fontWeight": "600",
                                        },
                                    ),
                                    html.Button(
                                        "Show Traffic Incidents",
                                        id="traffic-incidents-toggle-btn",
                                        n_clicks=0,
                                        style={
                                            "backgroundColor": "transparent",
                                            "border": "2px solid #FF9800",
                                            "borderRadius": "4px",
                                            "color": "#FF9800",
                                            "cursor": "pointer",
                                            "padding": "4px 10px",
                                            "fontSize": "12px",
                                            "fontWeight": "600",
                                        },
                                    ),
                                    html.Button(
                                        "Show Bicycle Parking Locations",
                                        id="bicycle-parking-toggle-btn",
                                        n_clicks=0,
                                        style={
                                            "backgroundColor": "transparent",
                                            "border": "2px solid #9C27B0",
                                            "borderRadius": "4px",
                                            "color": "#9C27B0",
                                            "cursor": "pointer",
                                            "padding": "4px 10px",
                                            "fontSize": "12px",
                                            "fontWeight": "600",
                                        },
                                    ),
                                    html.Button(
                                        "Show VMS Display boards Locations",
                                        id="vms-toggle-btn",
                                        n_clicks=0,
                                        style={
                                            "backgroundColor": "transparent",
                                            "border": "2px solid #C0C0C0",
                                            "borderRadius": "4px",
                                            "color": "#C0C0C0",
                                            "cursor": "pointer",
                                            "padding": "4px 10px",
                                            "fontSize": "12px",
                                            "fontWeight": "600",
                                        },
                                    ),
                                    html.Button(
                                        "Show SPF Speed Camera Locations",
                                        id="speed-camera-toggle-btn",
                                        n_clicks=0,
                                        style={
                                            "backgroundColor": "transparent",
                                            "border": "2px solid #81C784",
                                            "borderRadius": "4px",
                                            "color": "#81C784",
                                            "cursor": "pointer",
                                            "padding": "4px 10px",
                                            "fontSize": "12px",
                                            "fontWeight": "600",
                                        },
                                    ),
                                    html.Button(
                                        "Show Bus Stop Locations",
                                        id="bus-stops-toggle-btn",
                                        n_clicks=0,
                                        style={
                                            "backgroundColor": "transparent",
                                            "border": "2px solid #4169E1",
                                            "borderRadius": "4px",
                                            "color": "#4169E1",
                                            "cursor": "pointer",
                                            "padding": "4px 10px",
                                            "fontSize": "12px",
                                            "fontWeight": "600",
                                        },
                                    ),
                                ]
                            ),
                            html.Div(
                                style={
                                    "position": "relative",
                                    "width": "100%",
                                    "height": "100%",
                                    "flex": "1",
                                    "minHeight": "25rem",
                                },
                                children=[
                                    dl.Map(
                                        id="transport-map",
                                        center=sg_center,
                                        zoom=fixed_zoom,
                                        minZoom=10,
                                        maxZoom=19,
                                        maxBounds=sg_bounds,
                                        maxBoundsViscosity=1.0,
                                        style={
                                            "width": "100%",
                                            "height": "100%",
                                            "backgroundColor": "#1a2a3a",
                                        },
                                        children=[
                                            dl.TileLayer(
                                                url=onemap_tiles_url,
                                                attribution=onemap_attribution,
                                                maxNativeZoom=19,
                                            ),
                                            dl.LayerGroup(id="taxi-markers"),
                                            dl.LayerGroup(id="cctv-markers"),
                                            dl.LayerGroup(id="erp-markers"),
                                            dl.LayerGroup(id="speed-band-markers"),
                                            dl.LayerGroup(id="speed-camera-markers"),
                                            dl.LayerGroup(id="traffic-incidents-markers"),
                                            dl.LayerGroup(id="bicycle-parking-markers"),
                                            dl.LayerGroup(id="vms-markers"),
                                            dl.LayerGroup(id="bus-stops-markers"),
                                        ],
                                        zoomControl=True,
                                        dragging=True,
                                        scrollWheelZoom=True,
                                    ),
                                    # Taxi legend overlay
                                    html.Div(
                                        id="taxi-legend",
                                        style={
                                            "position": "absolute",
                                            "top": "10px",
                                            "right": "10px",
                                            "backgroundColor": "rgba(26, 42, 58, 0.9)",
                                            "borderRadius": "8px",
                                            "padding": "10px",
                                            "zIndex": "1000",
                                            "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.3)",
                                            "display": "none",  # Hidden by default, shown when taxi toggle is on
                                        },
                                        children=[
                                            html.Div(
                                                style={
                                                    "fontSize": "12px",
                                                    "fontWeight": "600",
                                                    "color": "#fff",
                                                    "marginBottom": "8px",
                                                    "borderBottom": "1px solid #4a5a6a",
                                                    "paddingBottom": "4px",
                                                },
                                                children="Taxi Legend"
                                            ),
                                            html.Div(
                                                style={
                                                    "display": "flex",
                                                    "alignItems": "center",
                                                    "marginBottom": "6px",
                                                },
                                                children=[
                                                    html.Div(
                                                        style={
                                                            "width": "12px",
                                                            "height": "12px",
                                                            "borderRadius": "50%",
                                                            "backgroundColor": "#FFD700",
                                                            "marginRight": "8px",
                                                        }
                                                    ),
                                                    html.Span(
                                                        "Taxi Locations",
                                                        style={
                                                            "color": "#fff",
                                                            "fontSize": "11px",
                                                        }
                                                    ),
                                                ]
                                            ),
                                            html.Div(
                                                style={
                                                    "display": "flex",
                                                    "alignItems": "center",
                                                },
                                                children=[
                                                    html.Div(
                                                        style={
                                                            "width": "0",
                                                            "height": "0",
                                                            "borderLeft": "6px solid transparent",
                                                            "borderRight": "6px solid transparent",
                                                            "borderBottom": "12px solid #FFA500",
                                                            "marginRight": "8px",
                                                        }
                                                    ),
                                                    html.Span(
                                                        "Taxi Stands",
                                                        style={
                                                            "color": "#fff",
                                                            "fontSize": "11px",
                                                        }
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                    # Bicycle parking legend overlay
                                    html.Div(
                                        id="bicycle-parking-legend",
                                        style={
                                            "position": "absolute",
                                            "top": "120px",  # Position below taxi legend
                                            "right": "10px",
                                            "backgroundColor": "rgba(26, 42, 58, 0.9)",
                                            "borderRadius": "8px",
                                            "padding": "10px",
                                            "zIndex": "1000",
                                            "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.3)",
                                            "display": "none",  # Hidden by default, shown when bicycle parking toggle is on
                                        },
                                        children=[
                                            html.Div(
                                                style={
                                                    "fontSize": "12px",
                                                    "fontWeight": "600",
                                                    "color": "#fff",
                                                    "marginBottom": "8px",
                                                    "borderBottom": "1px solid #4a5a6a",
                                                    "paddingBottom": "4px",
                                                },
                                                children="Bicycle Parking Legend"
                                            ),
                                            html.Div(
                                                id="bicycle-parking-legend-content",
                                                children=[]
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                        ]
                    ),
                    # Right side: MRT Line Operational Details
                    html.Div(
                        id="mrt-operational-details-panel",
                        style={
                            "flex": "1",
                            "minWidth": "18.75rem",
                            "maxWidth": "25rem",
                            "backgroundColor": "#4a5a6a",
                            "borderRadius": "0.5rem",
                            "padding": "0.9375rem",
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "0.9375rem",
                            "overflowY": "auto",
                        },
                        children=[
                            html.Div(
                                style={
                                    "borderBottom": "0.0625rem solid #5a6a7a",
                                    "paddingBottom": "0.625rem",
                                    "marginBottom": "0.625rem",
                                },
                                children=[
                                    html.H5(
                                        "🚇 Rail Operational Status",
                                        style={
                                            "margin": "0",
                                            "color": "#fff",
                                            "fontWeight": "600",
                                        }
                                    ),
                                ]
                            ),
                            html.Div(
                                id="mrt-line-status-display",
                                style={
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "gap": "0.625rem",
                                },
                                children=[
                                    html.P(
                                        "Loading MRT line status...",
                                        style={
                                            "color": "#999",
                                            "textAlign": "center",
                                            "fontSize": "0.75rem",
                                        }
                                    )
                                ]
                            ),
                        ]
                    ),
                ]
            ),
            # Store for toggle states
            dcc.Store(id="taxi-toggle-state", data=False),
            dcc.Store(id="cctv-toggle-state", data=False),
            dcc.Store(id="erp-toggle-state", data=False),
            dcc.Store(id="speed-band-toggle-state", data=False),
            dcc.Store(id="speed-camera-toggle-state", data=False),
            dcc.Store(id="traffic-incidents-toggle-state", data=False),
            dcc.Store(id="bicycle-parking-toggle-state", data=False),
            dcc.Store(id="vms-toggle-state", data=False),
            dcc.Store(id="bus-stops-toggle-state", data=False),
            # Interval for auto-refresh
            dcc.Interval(
                id='transport-interval',
                interval=2*60*1000,  # Update every 2 minutes
                n_intervals=0
            ),
        ]
    )
