"""
Component for the Transport Information page.
Displays transport-related information including taxi availability.
"""
from dash import html, dcc
import dash_leaflet as dl


def transport_page():
    """
    Create the Transport Information page layout.
    Features: Taxi availability display with map.

    Returns:
        HTML Div containing the Transport Information section
    """
    # Singapore center coordinates
    sg_center = [1.36, 103.82]
    onemap_tiles_url = "https://www.onemap.gov.sg/maps/tiles/Night/{z}/{x}/{y}.png"
    fixed_zoom = 12

    # Map bounds to restrict view to Singapore area
    sg_bounds = [[1.1304753, 103.6020882], [1.492007, 104.145897]]

    return html.Div(
        id="transport-page",
        style={
            "display": "none",  # Hidden by default
            "padding": "20px",
            "height": "calc(100vh - 120px)",
            "width": "100%",
        },
        children=[
            # Header
            html.H4(
                "Transport Information",
                style={
                    "textAlign": "center",
                    "margin": "0 0 15px 0",
                    "color": "#fff",
                    "fontWeight": "700"
                }
            ),
            # Main content container
            html.Div(
                id="transport-content",
                style={
                    "display": "flex",
                    "gap": "20px",
                    "height": "calc(100% - 50px)",
                    "maxWidth": "1800px",
                    "margin": "0 auto",
                },
                children=[
                    # Left side: Transport info panel
                    html.Div(
                        id="transport-info-panel",
                        style={
                            "flex": "1",
                            "minWidth": "300px",
                            "maxWidth": "400px",
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "15px",
                        },
                        children=[
                            # Taxi Availability card
                            html.Div(
                                id="taxi-availability-card",
                                style={
                                    "backgroundColor": "#4a5a6a",
                                    "borderRadius": "8px",
                                    "padding": "15px",
                                },
                                children=[
                                    # Header with toggle button
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "alignItems": "center",
                                            "borderBottom": "1px solid #5a6a7a",
                                            "paddingBottom": "10px",
                                            "marginBottom": "15px",
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
                                                    "borderRadius": "4px",
                                                    "color": "#000",
                                                    "cursor": "pointer",
                                                    "padding": "6px 12px",
                                                    "fontSize": "12px",
                                                    "fontWeight": "600",
                                                },
                                            ),
                                        ]
                                    ),
                                    # Taxi count display
                                    html.Div(
                                        id="taxi-count-display",
                                        children=[
                                            html.P(
                                                "Click 'Show on Map' to load taxi locations",
                                                style={
                                                    "color": "#999",
                                                    "textAlign": "center",
                                                    "padding": "20px",
                                                    "fontStyle": "italic",
                                                    "fontSize": "12px",
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
                                    "borderRadius": "8px",
                                    "padding": "15px",
                                },
                                children=[
                                    # Header with toggle button
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "alignItems": "center",
                                            "borderBottom": "1px solid #5a6a7a",
                                            "paddingBottom": "10px",
                                            "marginBottom": "15px",
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
                                        children=[
                                            html.P(
                                                "Click 'Show on Map' to load camera locations",
                                                style={
                                                    "color": "#999",
                                                    "textAlign": "center",
                                                    "padding": "20px",
                                                    "fontStyle": "italic",
                                                    "fontSize": "12px",
                                                }
                                            )
                                        ]
                                    ),
                                ]
                            ),
                            # Empty container for future use
                            html.Div(
                                id="transport-extra-container",
                                style={
                                    "flex": "1",
                                    "backgroundColor": "#2c3e50",
                                    "borderRadius": "8px",
                                    "padding": "15px",
                                    "minHeight": "100px",
                                },
                                children=[
                                    html.P(
                                        "Additional transport information",
                                        style={
                                            "color": "#666",
                                            "textAlign": "center",
                                            "padding": "20px",
                                            "fontStyle": "italic",
                                            "fontSize": "12px",
                                        }
                                    )
                                ]
                            ),
                        ]
                    ),
                    # Right side: Map
                    html.Div(
                        id="transport-map-panel",
                        style={
                            "flex": "2",
                            "minWidth": "500px",
                            "backgroundColor": "#1a2a3a",
                            "borderRadius": "8px",
                            "overflow": "hidden",
                        },
                        children=[
                            dl.Map(
                                id="transport-map",
                                center=sg_center,
                                zoom=fixed_zoom,
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
                                        attribution="&copy; OneMap Singapore"
                                    ),
                                    dl.LayerGroup(id="taxi-markers"),
                                    dl.LayerGroup(id="cctv-markers"),
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
            # Interval for auto-refresh
            dcc.Interval(
                id='transport-interval',
                interval=60*1000,  # Update every 60 seconds
                n_intervals=0
            ),
        ]
    )

