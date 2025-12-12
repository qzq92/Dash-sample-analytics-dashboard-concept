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
            "padding": "20px",
            "height": "calc(100vh - 120px)",
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
                                    "borderRadius": "0.5rem",
                                    "padding": "0.9375rem",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "overflow": "hidden",
                                },
                                children=[
                                    # Header with toggle button
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "alignItems": "center",
                                            "borderBottom": "0.0625rem solid #5a6a7a",
                                            "paddingBottom": "0.625rem",
                                            "marginBottom": "0.9375rem",
                                        },
                                        children=[
                                            html.H5(
                                                "🚕 Taxi Availability",
                                                style={
                                                    "margin": "0",
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                }
                                            ),
                                            html.Button(
                                                "Show on Map",
                                                id="taxi-toggle-btn",
                                                n_clicks=0,
                                                style={
                                                    "backgroundColor": "#FFD700",
                                                    "border": "none",
                                                    "borderRadius": "0.25rem",
                                                    "color": "#000",
                                                    "cursor": "pointer",
                                                    "padding": "0.375rem 0.75rem",
                                                    "fontSize": "0.75rem",
                                                    "fontWeight": "600",
                                                },
                                            ),
                                        ]
                                    ),
                                    # Taxi count display
                                    html.Div(
                                        id="taxi-count-display",
                                        style={
                                            "width": "100%",
                                            "boxSizing": "border-box",
                                            "overflow": "hidden",
                                        },
                                        children=[
                                            html.P(
                                                "Click 'Show on Map' to load taxi locations",
                                                style={
                                                    "color": "#999",
                                                    "textAlign": "center",
                                                    "padding": "1.25rem",
                                                    "fontStyle": "italic",
                                                    "fontSize": "0.75rem",
                                                }
                                            )
                                        ]
                                    ),
                                ]
                            ),
                            # CCTV Traffic Cameras card
                            html.Div(
                                id="cctv-card",
                                style={
                                    "backgroundColor": "#4a5a6a",
                                    "borderRadius": "0.5rem",
                                    "padding": "0.9375rem",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "overflow": "hidden",
                                },
                                children=[
                                    # Header with toggle button
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "alignItems": "center",
                                            "borderBottom": "0.0625rem solid #5a6a7a",
                                            "paddingBottom": "0.625rem",
                                            "marginBottom": "0.9375rem",
                                        },
                                        children=[
                                            html.H5(
                                                "📹 Traffic Cameras",
                                                style={
                                                    "margin": "0",
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                }
                                            ),
                                            html.Button(
                                                "Show on Map",
                                                id="cctv-toggle-btn",
                                                n_clicks=0,
                                                style={
                                                    "backgroundColor": "#4CAF50",
                                                    "border": "none",
                                                    "borderRadius": "4px",
                                                    "color": "#fff",
                                                    "cursor": "pointer",
                                                    "padding": "6px 12px",
                                                    "fontSize": "12px",
                                                    "fontWeight": "600",
                                                },
                                            ),
                                        ]
                                    ),
                                    # CCTV count display
                                    html.Div(
                                        id="cctv-count-display",
                                        style={
                                            "width": "100%",
                                            "boxSizing": "border-box",
                                            "overflow": "hidden",
                                        },
                                        children=[
                                            html.P(
                                                "Click 'Show on Map' to load camera locations",
                                                style={
                                                    "color": "#999",
                                                    "textAlign": "center",
                                                    "padding": "1.25rem",
                                                    "fontStyle": "italic",
                                                    "fontSize": "0.75rem",
                                                }
                                            )
                                        ]
                                    ),
                                ]
                            ),
                            # ERP Gantry card
                            html.Div(
                                id="erp-card",
                                style={
                                    "backgroundColor": "#4a5a6a",
                                    "borderRadius": "0.5rem",
                                    "padding": "0.9375rem",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "overflow": "hidden",
                                },
                                children=[
                                    # Header with toggle button
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "alignItems": "center",
                                            "borderBottom": "0.0625rem solid #5a6a7a",
                                            "paddingBottom": "0.625rem",
                                            "marginBottom": "0.9375rem",
                                        },
                                        children=[
                                            html.H5(
                                                "🚧 ERP Gantries",
                                                style={
                                                    "margin": "0",
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                }
                                            ),
                                            html.Button(
                                                "Show on Map",
                                                id="erp-toggle-btn",
                                                n_clicks=0,
                                                style={
                                                    "backgroundColor": "#FF6B6B",
                                                    "border": "none",
                                                    "borderRadius": "4px",
                                                    "color": "#fff",
                                                    "cursor": "pointer",
                                                    "padding": "6px 12px",
                                                    "fontSize": "12px",
                                                    "fontWeight": "600",
                                                },
                                            ),
                                        ]
                                    ),
                                    # ERP count display
                                    html.Div(
                                        id="erp-count-display",
                                        style={
                                            "width": "100%",
                                            "boxSizing": "border-box",
                                            "overflow": "hidden",
                                        },
                                        children=[
                                            html.P(
                                                "Click 'Show on Map' to load gantry locations",
                                                style={
                                                    "color": "#999",
                                                    "textAlign": "center",
                                                    "padding": "1.25rem",
                                                    "fontStyle": "italic",
                                                    "fontSize": "0.75rem",
                                                }
                                            )
                                        ]
                                    ),
                                ]
                            ),
                            # PUB CCTV section
                            html.Div(
                                style={
                                    "flex": "1",
                                    "backgroundColor": "#2c3e50",
                                    "borderRadius": "0.5rem",
                                    "padding": "0.9375rem",
                                    "minHeight": "6.25rem",
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
                                            "borderBottom": "0.0625rem solid #5a6a7a",
                                            "paddingBottom": "0.625rem",
                                            "marginBottom": "0.9375rem",
                                        },
                                        children=[
                                            html.H5(
                                                "📹 PUB CCTV",
                                                style={
                                                    "margin": "0",
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                }
                                            ),
                                            html.Button(
                                                "Show on Map",
                                                id="pub-cctv-toggle-btn",
                                                n_clicks=0,
                                                style={
                                                    "backgroundColor": "#00BCD4",
                                                    "border": "none",
                                                    "borderRadius": "4px",
                                                    "color": "#fff",
                                                    "cursor": "pointer",
                                                    "padding": "6px 12px",
                                                    "fontSize": "12px",
                                                    "fontWeight": "600",
                                                },
                                            ),
                                        ]
                                    ),
                                    # PUB CCTV count display
                                    html.Div(
                                        id="pub-cctv-count-display",
                                        style={
                                            "width": "100%",
                                            "boxSizing": "border-box",
                                            "overflow": "hidden",
                                        },
                                        children=[
                                            html.P(
                                                "Click 'Show on Map' to load CCTV locations",
                                                style={
                                                    "color": "#999",
                                                    "textAlign": "center",
                                                    "padding": "1.25rem",
                                                    "fontStyle": "italic",
                                                    "fontSize": "0.75rem",
                                                }
                                            )
                                        ]
                                    ),
                                ]
                            ),
                        ]
                    ),
                    # Right side: Map
                    html.Div(
                        id="transport-map-panel",
                        style={
                            "flex": "2",
                            "minWidth": "31.25rem",
                            "backgroundColor": "#1a2a3a",
                            "borderRadius": "0.5rem",
                            "overflow": "hidden",
                        },
                        children=[
                            dl.Map(
                                id="transport-map",
                                center=sg_center,
                                zoom=fixed_zoom,
                                minZoom=fixed_zoom,
                                maxZoom=fixed_zoom,
                                maxBounds=sg_bounds,
                                maxBoundsViscosity=1.0,
                                style={
                                    "width": "100%",
                                    "height": "100%",
                                    "minHeight": "25rem",
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
                                    dl.LayerGroup(id="pub-cctv-markers"),
                                ],
                                zoomControl=True,
                                dragging=True,
                                scrollWheelZoom=True,
                            ),
                        ]
                    ),
                ]
            ),
            # Store for toggle states
            dcc.Store(id="taxi-toggle-state", data=False),
            dcc.Store(id="cctv-toggle-state", data=False),
            dcc.Store(id="erp-toggle-state", data=False),
            dcc.Store(id="pub-cctv-toggle-state", data=False),
            # Interval for auto-refresh
            dcc.Interval(
                id='transport-interval',
                interval=60*1000,  # Update every 60 seconds
                n_intervals=0
            ),
        ]
    )
