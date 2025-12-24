"""
Component for the Speed Band on the Roads page.
Displays traffic speed band data on a map.
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


def speed_band_page():
    """
    Create the Speed Band on the Roads page layout.
    Features: Traffic speed band data displayed as color-coded polylines on map.

    Returns:
        HTML Div containing the Speed Band page section
    """
    # Use standardized map configuration
    sg_center = SG_MAP_CENTER
    onemap_tiles_url = ONEMAP_TILES_URL
    fixed_zoom = SG_MAP_DEFAULT_ZOOM
    onemap_attribution = get_onemap_attribution()
    sg_bounds = SG_MAP_BOUNDS

    return html.Div(
        id="speed-band-page",
        style={
            "display": "none",  # Hidden by default
            "padding": "20px",
            "height": "calc(100vh - 120px)",
            "width": "100%",
        },
        children=[
            # Main content container
            html.Div(
                id="speed-band-content",
                style={
                    "display": "flex",
                    "gap": "20px",
                    "height": "calc(100% - 50px)",
                    "maxWidth": "1800px",
                    "margin": "0 auto",
                },
                children=[
                    # Left side: Speed Band Information Panel
                    html.Div(
                        id="speed-band-info-panel",
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
                                        "🏎️ Speed Band on the Roads",
                                        style={
                                            "margin": "0",
                                            "color": "#fff",
                                            "fontWeight": "600",
                                        }
                                    ),
                                ]
                            ),
                            html.Div(
                                id="speed-band-count-value",
                                style={
                                    "color": "#00BCD4",
                                    "fontSize": "1.125rem",
                                    "fontWeight": "700",
                                    "marginBottom": "0.625rem",
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
                            html.Div(
                                id="speed-band-info-display",
                                style={
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "gap": "0.625rem",
                                },
                                children=[
                                    html.P(
                                        "Loading speed band information...",
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
                    # Middle: Map
                    html.Div(
                        id="speed-band-map-panel",
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
                                        id="speed-band-map",
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
                                            dl.LayerGroup(id="speed-band-map-markers"),
                                        ],
                                        zoomControl=True,
                                        dragging=True,
                                        scrollWheelZoom=True,
                                    ),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
            # Store for speed band data
            dcc.Store(id="speed-band-page-toggle-state", data=True),
            # Interval for auto-refresh
            dcc.Interval(
                id='speed-band-interval',
                interval=2*60*1000,  # Update every 2 minutes
                n_intervals=0
            ),
        ]
    )

