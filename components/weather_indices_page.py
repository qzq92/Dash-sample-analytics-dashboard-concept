"""
Component for the Pollutant & Exposure Indexes page.
Displays various exposure indexes across Singapore.
"""
from dash import html, dcc
import dash_leaflet as dl


def weather_indices_page():
    """
    Create the Pollutant & Exposure Indexes page layout.
    Features: UV Index, WBGT, and other exposure indexes.

    Returns:
        HTML Div containing the Pollutant & Exposure Indexes section
    """
    # Singapore center coordinates
    sg_center = [1.36, 103.82]
    onemap_tiles_url = "https://www.onemap.gov.sg/maps/tiles/Night/{z}/{x}/{y}.png"
    fixed_zoom = 12

    # Map bounds to restrict view to Singapore area
    sg_bounds = [[1.1304753, 103.6020882], [1.492007, 104.145897]]

    return html.Div(
        id="weather-indices-page",
        style={
            "display": "none",  # Hidden by default
            "padding": "20px",
            "height": "calc(100vh - 120px)",
            "width": "100%",
        },
        children=[
            # Store for active marker type on map
            dcc.Store(id="exposure-marker-type", data={'type': None, 'ts': 0}),
            # Header
            html.H4(
                "Pollutant & Exposure Indexes",
                style={
                    "textAlign": "center",
                    "margin": "0 0 15px 0",
                    "color": "#fff",
                    "fontWeight": "700"
                }
            ),
            # Main content container: map on left, indices on right
            html.Div(
                id="weather-indices-content",
                style={
                    "display": "flex",
                    "gap": "20px",
                    "height": "calc(100% - 50px)",
                    "maxWidth": "1800px",
                    "margin": "0 auto",
                },
                children=[
                    # Left side: Indices panels
                    html.Div(
                        id="weather-indices-panel",
                        style={
                            "flex": "1",
                            "minWidth": "350px",
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "15px",
                            "overflowY": "auto",
                        },
                        children=[
                            # UV Index card
                            html.Div(
                                id="uv-index-card",
                                style={
                                    "backgroundColor": "#4a5a6a",
                                    "borderRadius": "8px",
                                    "padding": "15px",
                                    "display": "flex",
                                    "flexDirection": "column",
                                },
                                children=[
                                    # Header with toggle button
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "alignItems": "center",
                                            "borderBottom": "1px solid #5a6a7a",
                                            "paddingBottom": "8px",
                                            "marginBottom": "10px",
                                        },
                                        children=[
                                            html.H5(
                                                "☀️ UV Index Today (Daylight hourly trend)",
                                                style={
                                                    "margin": "0",
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                }
                                            ),
                                            # Note: UV doesn't have station locations
                                        ]
                                    ),
                                    html.Div(
                                        id="uv-index-content",
                                        style={
                                            "flex": "1",
                                            "overflowY": "auto",
                                        },
                                        children=[
                                            html.P(
                                                "Loading UV data...",
                                                style={
                                                    "color": "#ccc",
                                                    "textAlign": "center",
                                                    "padding": "20px",
                                                }
                                            )
                                        ]
                                    ),
                                ]
                            ),
                            # WBGT (Wet Bulb Globe Temperature) card
                            html.Div(
                                id="wbgt-index-card",
                                style={
                                    "backgroundColor": "#4a5a6a",
                                    "borderRadius": "8px",
                                    "padding": "15px",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "flex": "1",
                                    "minHeight": "300px",
                                },
                                children=[
                                    # Header with toggle button
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "alignItems": "center",
                                            "borderBottom": "1px solid #5a6a7a",
                                            "paddingBottom": "8px",
                                            "marginBottom": "10px",
                                        },
                                        children=[
                                            html.H5(
                                                "🌡️ Wet-Bulb Globe Temperature (WBGT) (Heat Stress) across detected areas",
                                                style={
                                                    "margin": "0",
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                }
                                            ),
                                            html.Button(
                                                "📍",
                                                id="wbgt-map-toggle",
                                                n_clicks=0,
                                                style={
                                                    "backgroundColor": "transparent",
                                                    "border": "1px solid #6a7a8a",
                                                    "borderRadius": "4px",
                                                    "color": "#ccc",
                                                    "cursor": "pointer",
                                                    "padding": "4px 8px",
                                                    "fontSize": "14px",
                                                },
                                                title="Show WBGT stations on map"
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        id="wbgt-index-content",
                                        style={
                                            "flex": "1",
                                            "overflowY": "auto",
                                            "overflowX": "hidden",
                                            "minHeight": "0",
                                        },
                                        children=[
                                            html.P(
                                                "Loading WBGT data...",
                                                style={
                                                    "color": "#ccc",
                                                    "textAlign": "center",
                                                    "padding": "20px",
                                                }
                                            )
                                        ]
                                    ),
                                ]
                            ),
                        ]
                    ),
                    # Right side: Map with legend
                    html.Div(
                        id="weather-indices-map-panel",
                        style={
                            "flex": "1.5",
                            "minWidth": "400px",
                            "backgroundColor": "#1a2a3a",
                            "borderRadius": "8px",
                            "overflow": "hidden",
                            "display": "flex",
                            "flexDirection": "column",
                        },
                        children=[
                            # Pollutant Legend Banner
                            html.Div(
                                id="pollutant-legend",
                                style={
                                    "backgroundColor": "#2a3a4a",
                                    "padding": "8px 12px",
                                    "borderBottom": "1px solid #3a4a5a",
                                    "flexShrink": "0",
                                },
                                children=[
                                    html.Div(
                                        "Pollutant Abbreviations",
                                        style={
                                            "fontSize": "11px",
                                            "fontWeight": "700",
                                            "color": "#60a5fa",
                                            "marginBottom": "6px",
                                        }
                                    ),
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "flexWrap": "wrap",
                                            "gap": "8px 16px",
                                            "fontSize": "10px",
                                            "color": "#ccc",
                                        },
                                        children=[
                                            html.Span([
                                                html.Strong("PSI", style={"color": "#fff"}),
                                                " = Pollutant Standards Index"
                                            ]),
                                            html.Span([
                                                html.Strong("PM2.5", style={"color": "#fff"}),
                                                " = Particulate Matter ≤2.5µm"
                                            ]),
                                            html.Span([
                                                html.Strong("PM10", style={"color": "#fff"}),
                                                " = Particulate Matter ≤10µm"
                                            ]),
                                            html.Span([
                                                html.Strong("SO₂", style={"color": "#fff"}),
                                                " = Sulphur Dioxide"
                                            ]),
                                            html.Span([
                                                html.Strong("CO", style={"color": "#fff"}),
                                                " = Carbon Monoxide"
                                            ]),
                                            html.Span([
                                                html.Strong("O₃", style={"color": "#fff"}),
                                                " = Ozone"
                                            ]),
                                            html.Span([
                                                html.Strong("NO₂", style={"color": "#fff"}),
                                                " = Nitrogen Dioxide"
                                            ]),
                                        ]
                                    ),
                                ]
                            ),
                            # Map
                            html.Div(
                                style={
                                    "flex": "1",
                                    "minHeight": "0",
                                },
                                children=[
                                    dl.Map(
                                        id="weather-indices-map",
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
                                            dl.LayerGroup(
                                                id="weather-indices-markers"
                                            ),
                                            dl.LayerGroup(
                                                id="psi-markers"
                                            ),
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
            # Interval for auto-refresh
            dcc.Interval(
                id='weather-indices-interval',
                interval=60*1000,  # Update every 60 seconds
                n_intervals=0
            ),
        ]
    )
