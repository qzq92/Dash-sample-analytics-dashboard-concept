"""
Component for the MRT/LRT Station Crowd page.
Displays real-time crowd density levels for MRT and LRT stations.
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


def mrt_crowd_page():
    """
    Create the MRT/LRT Station Crowd page layout.
    Features: Real-time crowd density levels displayed on map and in list format.

    Returns:
        HTML Div containing the MRT/LRT Station Crowd page section
    """
    # Use standardized map configuration
    sg_center = SG_MAP_CENTER
    onemap_tiles_url = ONEMAP_TILES_URL
    fixed_zoom = SG_MAP_DEFAULT_ZOOM
    onemap_attribution = get_onemap_attribution()
    sg_bounds = SG_MAP_BOUNDS

    return html.Div(
        id="mrt-crowd-page",
        style={
            "display": "none",  # Hidden by default
            "padding": "20px",
            "height": "calc(100vh - 120px)",
            "width": "100%",
        },
        children=[
            # Main content container
            html.Div(
                id="mrt-crowd-content",
                style={
                    "display": "flex",
                    "gap": "20px",
                    "height": "calc(100% - 50px)",
                    "maxWidth": "1800px",
                    "margin": "0 auto",
                },
                children=[
                    # Left side: Station Crowd Information Panel
                    html.Div(
                        id="mrt-crowd-info-panel",
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
                                        "🚇 MRT/LRT Station Crowd",
                                        style={
                                            "margin": "0",
                                            "color": "#fff",
                                            "fontWeight": "600",
                                        }
                                    ),
                                ]
                            ),
                            # Train line filter
                            html.Div(
                                [
                                    html.Label(
                                        "Filter by Train Line:",
                                        style={
                                            "color": "#fff",
                                            "fontSize": "0.875rem",
                                            "fontWeight": "600",
                                            "marginBottom": "0.5rem",
                                        }
                                    ),
                                    dcc.Dropdown(
                                        id="mrt-crowd-line-filter",
                                        options=[
                                            {"label": "All Lines", "value": "all"},
                                            {"label": "North South Line (NSL)", "value": "NSL"},
                                            {"label": "East West Line (EWL)", "value": "EWL"},
                                            {"label": "Circle Line (CCL)", "value": "CCL"},
                                            {"label": "Downtown Line (DTL)", "value": "DTL"},
                                            {"label": "North East Line (NEL)", "value": "NEL"},
                                            {"label": "Thomson-East Coast Line (TEL)", "value": "TEL"},
                                            {"label": "Bukit Panjang LRT (BPL)", "value": "BPL"},
                                            {"label": "Sengkang LRT (SKL)", "value": "SKL"},
                                            {"label": "Punggol LRT (PGL)", "value": "PGL"},
                                        ],
                                        value="all",
                                        style={
                                            "backgroundColor": "#2a3a4a",
                                            "color": "#fff",
                                        },
                                        clearable=False,
                                    ),
                                ],
                                style={"marginBottom": "0.625rem"}
                            ),
                            # Station count
                            html.Div(
                                id="mrt-crowd-count-value",
                                style={
                                    "color": "#00BCD4",
                                    "fontSize": "1.125rem",
                                    "fontWeight": "700",
                                    "marginBottom": "0.625rem",
                                },
                                children=[
                                    html.Div(
                                        html.Span("Loading crowd data...", style={"color": "#999"}),
                                        style={
                                            "backgroundColor": "rgb(58, 74, 90)",
                                            "padding": "4px 8px",
                                            "borderRadius": "4px",
                                        }
                                    )
                                ]
                            ),
                            # Station list
                            html.Div(
                                id="mrt-crowd-station-list",
                                style={
                                    "flex": "1",
                                    "overflowY": "auto",
                                    "minHeight": "0",
                                },
                                children=[
                                    html.P(
                                        "Loading station crowd data...",
                                        style={
                                            "color": "#999",
                                            "textAlign": "center",
                                            "padding": "20px",
                                        }
                                    )
                                ]
                            ),
                            # Legend
                            html.Div(
                                id="mrt-crowd-legend",
                                style={
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "gap": "0.625rem",
                                    "padding": "0.625rem",
                                    "backgroundColor": "rgba(42, 54, 66, 0.8)",
                                    "borderRadius": "8px",
                                    "border": "2px solid rgba(255, 255, 255, 0.2)",
                                },
                                children=[
                                    html.P("Crowd Level Legend", style={
                                        "color": "#fff",
                                        "fontSize": "0.875rem",
                                        "fontWeight": "700",
                                        "marginBottom": "10px",
                                        "marginTop": "0",
                                        "textAlign": "center",
                                    }),
                                    html.Div([
                                        html.Div([
                                            html.Div(style={
                                                "width": "20px",
                                                "height": "20px",
                                                "backgroundColor": "#32CD32",
                                                "marginRight": "8px",
                                                "borderRadius": "4px",
                                            }),
                                            html.Span("Low", style={
                                                "color": "#ddd",
                                                "fontSize": "0.75rem",
                                            })
                                        ], style={"display": "flex", "alignItems": "center", "marginBottom": "6px"}),
                                        html.Div([
                                            html.Div(style={
                                                "width": "20px",
                                                "height": "20px",
                                                "backgroundColor": "#FFD700",
                                                "marginRight": "8px",
                                                "borderRadius": "4px",
                                            }),
                                            html.Span("Moderate", style={
                                                "color": "#ddd",
                                                "fontSize": "0.75rem",
                                            })
                                        ], style={"display": "flex", "alignItems": "center", "marginBottom": "6px"}),
                                        html.Div([
                                            html.Div(style={
                                                "width": "20px",
                                                "height": "20px",
                                                "backgroundColor": "#FF4500",
                                                "marginRight": "8px",
                                                "borderRadius": "4px",
                                            }),
                                            html.Span("High", style={
                                                "color": "#ddd",
                                                "fontSize": "0.75rem",
                                            })
                                        ], style={"display": "flex", "alignItems": "center"}),
                                    ]),
                                    html.Div(
                                        "Data updates every 10 minutes",
                                        style={
                                            "color": "#aaa",
                                            "fontSize": "0.6875rem",
                                            "fontStyle": "italic",
                                            "marginTop": "0.3125rem",
                                            "paddingTop": "0.625rem",
                                            "borderTop": "1px solid rgba(255, 255, 255, 0.1)",
                                            "textAlign": "center",
                                            "lineHeight": "1.4"
                                        }
                                    )
                                ]
                            ),
                        ]
                    ),
                    # Middle: Map
                    html.Div(
                        id="mrt-crowd-map-panel",
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
                                    dcc.Loading(
                                        id="mrt-crowd-map-loading",
                                        type="circle",
                                        color="#00BCD4",
                                        children=[
                                            dl.Map(
                                                id="mrt-crowd-map",
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
                                                    dl.LayerGroup(id="mrt-crowd-map-markers"),
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
                ]
            ),
            # Store for crowd data
            dcc.Store(id="mrt-crowd-data-store", data=None),
            # Interval for auto-refresh (every 10 minutes as per API update frequency)
            dcc.Interval(
                id='mrt-crowd-interval',
                interval=10*60*1000,  # Update every 10 minutes
                n_intervals=0
            ),
        ]
    )

