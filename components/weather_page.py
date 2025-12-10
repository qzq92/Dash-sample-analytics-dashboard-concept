"""
Component for the 2-hour weather forecast page.
"""
from dash import html
import dash_leaflet as dl


def weather_forecast_page():
    """
    Create the 2-hour weather forecast page layout.
    Features side-by-side layout: weather info on left, static map with icons on right.

    Returns:
        HTML Div containing the weather forecast section with map
    """
    # Singapore center coordinates (Adjusted to frame Singapore nicely)
    sg_center = [1.36, 103.82]
    onemap_tiles_url = "https://www.onemap.gov.sg/maps/tiles/Night/{z}/{x}/{y}.png"
    fixed_zoom = 12

    # Map bounds to restrict view to Singapore area (approximate)
    sg_bounds = [[1.1304753, 103.6020882], [1.492007, 104.145897]]

    return html.Div(
        id="weather-forecast-page",
        style={
            "display": "none",  # Hidden by default, shown when weather tab is selected
            "padding": "10px",
            "height": "calc(100vh - 180px)",
            "width": "100%",
        },
        children=[
            # Main content: side-by-side layout
            html.Div(
                id="weather-forecast-section",
                style={
                    "display": "flex",
                    "gap": "10px",
                    "height": "calc(100% - 50px)",
                    "maxWidth": "1600px",
                    "margin": "0 auto",
                },
                children=[
                    # Left side: Weather info grid (4 columns x 12+ rows)
                    html.Div(
                        id="weather-info-panel",
                        style={
                            "flex": "1.2",
                            "backgroundColor": "#4a5a6a",
                            "borderRadius": "5px",
                            "padding": "6px",
                            "display": "flex",
                            "flexDirection": "column",
                            "minWidth": "500px",
                        },
                        children=[
                            html.H5(
                                "Area Forecasts",
                                style={
                                    "textAlign": "center",
                                    "margin": "3px 0 6px 0",
                                    "color": "#fff",
                                    "fontWeight": "600",
                                    "fontSize": "14px"
                                }
                            ),
                            html.Div(
                                id="weather-2h-content",
                                children=[
                                    html.P("Loading...", style={"textAlign": "center", "padding": "20px", "color": "#999"})
                                ],
                                style={
                                    "padding": "3px",
                                    "overflowY": "auto",
                                    "flex": "1",
                                }
                            ),
                        ]
                    ),
                    # Right side: Static map with weather icons
                    html.Div(
                        id="weather-map-panel",
                        style={
                            "flex": "1.5",
                            "backgroundColor": "#4a5a6a",
                            "borderRadius": "5px",
                            "padding": "6px",
                            "display": "flex",
                            "flexDirection": "column",
                            "minWidth": "400px",
                        },
                        children=[
                            html.H5(
                                "Weather Map",
                                style={
                                    "textAlign": "center",
                                    "margin": "3px 0 6px 0",
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
                                        id="weather-2h-map",
                                        center=sg_center,
                                        zoom=fixed_zoom,
                                        minZoom=11,
                                        maxZoom=14,
                                        maxBounds=sg_bounds,
                                        style={
                                            "width": "100%",
                                            "height": "calc(100vh - 280px)",
                                            "minHeight": "400px",
                                            "backgroundColor": "#1a2a3a",  # Match dark theme/sea color
                                        },
                                        dragging=True,
                                        touchZoom=False,
                                        scrollWheelZoom=True,
                                        doubleClickZoom=False,
                                        boxZoom=False,
                                        keyboard=False,
                                        zoomControl=True,
                                        children=[
                                            dl.TileLayer(
                                                url=onemap_tiles_url,
                                                attribution='<img src="https://www.onemap.gov.sg/web-assets/images/logo/om_logo.png" style="height:20px;width:20px;"/>&nbsp;<a href="https://www.onemap.gov.sg/" target="_blank" rel="noopener noreferrer">OneMap</a>',
                                                maxNativeZoom=19,
                                            ),
                                            dl.LayerGroup(id="weather-markers-layer"),
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
