"""
Component for the Nearby Transportation and Parking Info page.
Displays nearby transportation options and parking facilities.
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


def nearby_transport_page():
    """
    Create the Nearby Transportation and Parking Info page layout.
    Features: Nearby bus stops, MRT/LRT stations, taxi stands, carparks, and bicycle parking.

    Returns:
        HTML Div containing the Nearby Transportation and Parking Info section
    """
    # Use standardized map configuration
    sg_center = SG_MAP_CENTER
    onemap_tiles_url = ONEMAP_TILES_URL
    fixed_zoom = SG_MAP_DEFAULT_ZOOM
    onemap_attribution = get_onemap_attribution()
    sg_bounds = SG_MAP_BOUNDS

    return html.Div(
        id="nearby-transport-page",
        style={
            "display": "none",  # Hidden by default
            "padding": "20px",
            "height": "calc(100vh - 120px)",
            "width": "100%",
        },
        children=[
            # Main content container
            html.Div(
                id="nearby-transport-content",
                style={
                    "display": "flex",
                    "gap": "20px",
                    "height": "calc(100% - 50px)",
                    "maxWidth": "1800px",
                    "margin": "0 auto",
                },
                children=[
                    # Left side: Info panel with tabs
                    html.Div(
                        id="nearby-transport-info-panel",
                        style={
                            "width": "30%",
                            "minWidth": "300px",
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "15px",
                            "backgroundColor": "#1a2a3a",
                            "borderRadius": "8px",
                            "padding": "15px",
                            "overflowY": "auto",
                        },
                        children=[
                            html.H3(
                                "Nearby Facilities",
                                style={
                                    "color": "#fff",
                                    "margin": "0 0 15px 0",
                                    "fontSize": "18px",
                                    "fontWeight": "600",
                                }
                            ),
                            # Nearby facilities containers (row-wise)
                            html.Div(
                                id="nearby-facilities-containers",
                                style={
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "gap": "10px",
                                    "flex": "1",
                                    "overflowY": "auto",
                                },
                                children=[
                                    # Row 1: MRT, Carpark, Bus Stop
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "gap": "10px",
                                            "width": "100%",
                                        },
                                        children=[
                                            # Nearest MRT column
                                            html.Div(
                                                id="nearby-transport-mrt-column",
                                                style={
                                                    "flex": "1",
                                                    "backgroundColor": "#2c3e50",
                                                    "borderRadius": "5px",
                                                    "padding": "15px",
                                                    "minHeight": "150px"
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
                                                        id="nearby-transport-mrt-content",
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
                                                id="nearby-transport-carpark-column",
                                                style={
                                                    "flex": "1",
                                                    "backgroundColor": "#2c3e50",
                                                    "borderRadius": "5px",
                                                    "padding": "15px",
                                                    "minHeight": "150px"
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
                                                        id="nearby-transport-carpark-content",
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
                                                id="nearby-transport-bus-stop-column",
                                                style={
                                                    "flex": "1",
                                                    "backgroundColor": "#2c3e50",
                                                    "borderRadius": "5px",
                                                    "padding": "15px",
                                                    "minHeight": "150px"
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
                                                        id="nearby-transport-bus-stop-content",
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
                                    # Row 2: Taxi Stands, Bicycle Parking
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "gap": "10px",
                                            "width": "100%",
                                        },
                                        children=[
                                            # Taxi Stands column
                                            html.Div(
                                                id="nearby-transport-taxi-stand-column",
                                                style={
                                                    "flex": "1",
                                                    "backgroundColor": "#2c3e50",
                                                    "borderRadius": "5px",
                                                    "padding": "15px",
                                                    "minHeight": "150px"
                                                },
                                                children=[
                                                    html.H4(
                                                        "Nearby 300m Taxi Stands",
                                                        style={
                                                            "textAlign": "center",
                                                            "marginBottom": "10px",
                                                            "color": "#fff",
                                                            "fontWeight": "700",
                                                            "fontSize": "14px"
                                                        }
                                                    ),
                                                    html.Div(
                                                        id="nearby-transport-taxi-stand-content",
                                                        style={
                                                            "overflowY": "auto",
                                                            "overflowX": "hidden",
                                                            "maxHeight": "calc(100% - 40px)"
                                                        },
                                                        children=[
                                                            html.P(
                                                                "Select a location to view nearest taxi stands",
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
                                            # Bicycle Parking column
                                            html.Div(
                                                id="nearby-transport-bicycle-column",
                                                style={
                                                    "flex": "1",
                                                    "backgroundColor": "#2c3e50",
                                                    "borderRadius": "5px",
                                                    "padding": "15px",
                                                    "minHeight": "150px"
                                                },
                                                children=[
                                                    html.H4(
                                                        "Nearby 100m Bicycle Parking Spots",
                                                        style={
                                                            "textAlign": "center",
                                                            "marginBottom": "10px",
                                                            "color": "#fff",
                                                            "fontWeight": "700",
                                                            "fontSize": "14px"
                                                        }
                                                    ),
                                                    html.Div(
                                                        id="nearby-transport-bicycle-content",
                                                        style={
                                                            "overflowY": "auto",
                                                            "overflowX": "hidden",
                                                            "maxHeight": "calc(100% - 40px)"
                                                        },
                                                        children=[
                                                            html.P(
                                                                "Select a location to view nearest bicycle parking",
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
                            # EV Charging Points column
                            html.Div(
                                id="nearby-transport-ev-charging-column",
                                style={
                                    "flex": "1",
                                    "backgroundColor": "#2c3e50",
                                    "borderRadius": "5px",
                                    "padding": "15px",
                                    "minHeight": "150px"
                                },
                                children=[
                                    html.H4(
                                        "Nearby EV Charging Points",
                                        style={
                                            "textAlign": "center",
                                            "marginBottom": "10px",
                                            "color": "#fff",
                                            "fontWeight": "700",
                                            "fontSize": "14px"
                                        }
                                    ),
                                    html.Div(
                                        id="nearby-transport-ev-charging-content",
                                        style={
                                            "overflowY": "auto",
                                            "overflowX": "hidden",
                                            "maxHeight": "calc(100% - 40px)"
                                        },
                                        children=[
                                            html.P(
                                                "Select a location to view nearby EV charging points",
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
                    # Right side: Search bar and Map
                    html.Div(
                        id="nearby-transport-map-panel",
                        style={
                            "flex": "1",
                            "minWidth": "500px",
                            "display": "flex",
                            "flexDirection": "column",
                            "height": "100%",
                            "gap": "10px",
                        },
                        children=[
                            # Search bar above map
                            html.Div(
                                id="nearby-transport-search-bar",
                                style={
                                    "flexShrink": "0",
                                },
                                children=[
                                    dcc.Dropdown(
                                        id="nearby-transport-search",
                                        placeholder="Search address or location in Singapore",
                                        style={"width": "100%", "marginBottom": "8px"},
                                        searchable=True,
                                        clearable=True,
                                        optionHeight=40,
                                        maxHeight=240,
                                    )
                                ]
                            ),
                            # Map container
                            html.Div(
                                style={
                                    "flex": "1",
                                    "minHeight": "0",
                                    "backgroundColor": "#1a2a3a",
                                    "borderRadius": "8px",
                                    "overflow": "hidden",
                                },
                                children=[
                                    dl.Map(
                                        id="nearby-transport-map",
                                        center=sg_center,
                                        zoom=fixed_zoom,
                                        minZoom=10,
                                        maxZoom=19,
                                        maxBounds=sg_bounds,
                                        maxBoundsViscosity=1.0,
                                        style={
                                            "width": "100%",
                                            "height": "100%",
                                            "minHeight": "400px",
                                            "backgroundColor": "#1a2a3a",
                                        },
                                        children=[
                                    dl.TileLayer(
                                        url=onemap_tiles_url,
                                        attribution=onemap_attribution,
                                        maxNativeZoom=19,
                                    ),
                                    dl.LayerGroup(id="nearby-transport-search-marker"),
                                    dl.LayerGroup(id="nearby-bus-stop-markers"),
                                    dl.LayerGroup(id="nearby-mrt-markers"),
                                    dl.LayerGroup(id="nearby-taxi-stand-markers"),
                                    dl.LayerGroup(id="nearby-carpark-markers"),
                                    dl.LayerGroup(id="nearby-bicycle-markers"),
                                    dl.LayerGroup(id="nearby-ev-charging-markers"),
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
            # Store for search location
            dcc.Store(id="nearby-transport-location-store", data=None),
            # Interval for auto-refresh
            dcc.Interval(
                id='nearby-transport-interval',
                interval=2*60*1000,  # Update every 2 minutes
                n_intervals=0
            ),
        ]
    )

