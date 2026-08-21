"""Reusable map and nearby-stats UI components for the main dashboard."""

from dash import html, dcc
import dash_daq as daq
import dash_leaflet as dl
from utils.map_utils import get_onemap_attribution



def search_bar():
    """
    Search bar component with integrated dropdown for displaying top 5 search results from OneMap API.
    """
    return dcc.Dropdown(
        id="input_search",
        placeholder="Search address or location in Singapore",
        style={"width": "100%", "marginBottom": "0.5rem"},
        searchable=True,
        clearable=True,
        optionHeight=40,
        maxHeight=240,
    )


def nearest_mrt_panel():
    """Return a placeholder container for nearest MRT station details."""
    return html.Div(
        id="nearest-mrt-panel",
        children=[],
        style={"marginTop": "0.5rem"}
    )


def carpark_availability_panel():
    """
    Panel component for displaying carpark availability information.
    Automatically shows carparks within 500m of the map center.
    """
    return html.Div(
        [
            html.Div(
                id="carpark-availability-panel",
                children=[
                    html.Div(
                        "Carparks within 500m of map center will be displayed here",
                        style={
                            "padding": "0.625rem",
                            "color": "#999",
                            "fontSize": "0.875rem",
                            "fontStyle": "italic"
                        }
                    )
                ],
                style={"marginTop": "0.5rem"}
            )
        ]
    )


def map_component(lat=None, lon=None):
    """
    Default display and layout of the map component. No API is needed as this is static rendering of map for quick loading
    Coordinates are provided in EPSG:4326 (WGS84 lat/lon) format, which Leaflet converts automatically.
    
    The initial center coordinates are used only for initial rendering.
    """
    from utils.map_utils import (
        SG_MAP_CENTER,
        SG_MAP_DEFAULT_ZOOM,
        SG_MAP_MIN_ZOOM,
        SG_MAP_MAX_ZOOM,
        SG_MAP_BOUNDS,
        ONEMAP_TILES_URL
    )
    
    # Use standardized center if not provided
    if lat is None or lon is None:
        lat, lon = SG_MAP_CENTER
    
    onemap_tiles_url = ONEMAP_TILES_URL
    onemap_attribution = get_onemap_attribution()
    return html.Div([
        # Store component to hold map coordinates that can be updated by callbacks
        dcc.Store(
            id="map-coordinates-store",
            data={"lat": lat, "lon": lon}
        ),
        dl.Map(
            id="sg-map",
            center=[lat, lon],  # Initial center, will be updated by callback
            zoom=SG_MAP_DEFAULT_ZOOM,
            minZoom=SG_MAP_MIN_ZOOM,
            maxZoom=SG_MAP_MAX_ZOOM,
            # Map bounds to restrict view to Singapore area
            maxBounds=SG_MAP_BOUNDS,
            style={"width": "100%", "height": "100%", "margin": "0"},
            children=[
                dl.TileLayer(
                    url=onemap_tiles_url,
                    attribution=onemap_attribution,
                    maxNativeZoom=18,
                ),
                dl.ScaleControl(imperial=False, position="bottomleft"),
                dl.LayerGroup(id="main-psi-markers"),
                dl.LayerGroup(id="weather-2h-markers"),
                dl.LayerGroup(id="mrt-crowd-markers"),
                dl.LayerGroup(id="main-traffic-incidents-markers"),
            ],
        ),
        html.Div(
            id="mrt-crowd-legend",
            style={
                "position": "absolute",
                "top": "0.625rem",
                "left": "0.625rem",
                "backgroundColor": "rgba(26, 42, 58, 0.92)",
                "borderRadius": "0.5rem",
                "padding": "0.5rem 0.625rem",
                "zIndex": "1000",
                "boxShadow": "0 0.125rem 0.5rem rgba(0, 0, 0, 0.3)",
                "display": "none",
                "minWidth": "8.5rem",
            },
            children=[
                html.Div(
                    "MRT/LRT Crowd",
                    style={
                        "fontSize": "0.75rem",
                        "fontWeight": "600",
                        "color": "#fff",
                        "marginBottom": "0.375rem",
                    },
                ),
                html.Div(
                    style={"display": "flex", "alignItems": "center", "gap": "0.375rem", "marginBottom": "0.25rem"},
                    children=[
                        html.Div(style={"width": "0.625rem", "height": "0.625rem", "borderRadius": "50%", "backgroundColor": "#32CD32"}),
                        html.Span("Low", style={"color": "#fff", "fontSize": "0.6875rem"}),
                    ],
                ),
                html.Div(
                    style={"display": "flex", "alignItems": "center", "gap": "0.375rem", "marginBottom": "0.25rem"},
                    children=[
                        html.Div(style={"width": "0.625rem", "height": "0.625rem", "borderRadius": "50%", "backgroundColor": "#FFD700"}),
                        html.Span("Moderate", style={"color": "#fff", "fontSize": "0.6875rem"}),
                    ],
                ),
                html.Div(
                    style={"display": "flex", "alignItems": "center", "gap": "0.375rem"},
                    children=[
                        html.Div(style={"width": "0.625rem", "height": "0.625rem", "borderRadius": "50%", "backgroundColor": "#FF4500"}),
                        html.Span("High", style={"color": "#fff", "fontSize": "0.6875rem"}),
                    ],
                ),
            ],
        ),
    ], style={"width": "100%", "height": "100%", "display": "flex", "flexDirection": "column", "position": "relative"})


def map_coordinates_display():
    """
    Component to display the current map center coordinates (lat/lon) underneath the map.
    """
    return html.Div(
        id="map-coordinates-display",
        children=[
            html.Div(
                "Lat: --, Lon: --",
                id="coordinates-text",
                style={
                    "padding": "0.5rem 0.75rem",
                    "backgroundColor": "#2c3e50",
                    "borderRadius": "0.25rem",
                    "fontSize": "0.8125rem",
                    "color": "#fff",
                    "fontFamily": "monospace",
                    "textAlign": "center",
                    "border": "0.0625rem solid #444"
                }
            )
        ],
        style={
            "marginTop": "8px",
            "width": "100%"
        }
    )


def display_artefacts(id: str, label: str, value: str, size: int=50,):
    """Function which display artefacts as value using daq's LEDDisplay library.
    Args:
        id (str): HTML division id for dash callback decorator.
        label (str): Name of value artefact.
        value (str): Value artefact to be displayed.
        size (int, optional): Size of display. Defaults to 50.

    Returns:
        html.Div: HTML Division utilising LEDDisplay to show input display value.
    """
    return html.Div(
        [daq.LEDDisplay(
            id=id,
            label=label,
            value=value,
            size=size)
        ],
    style={'display': 'flex', 'justify-content': 'center'}
    )


def display_nearby_artefacts(id: str, label: str, value: str, size: int = 50,):
    """Backward-compatible wrapper around `display_artefacts` for nearby metrics."""
    return display_artefacts(id=id, label=label, value=value, size=size)


def show_descriptive_stats():
    """Render LED artefacts summarizing nearby transport amenities."""
    return html.Div(
        id="Descriptive-stats",
        children=[
            # Bus stop
            display_artefacts(
                id="nearby-bus-stop-led",
                label="Number of nearby bus stops",
                value="0",
            ),
            # Taxi stand
            display_nearby_artefacts(
                id="nearby-taxi-stand-led",
                label="Number of nearby taxi stands",
                value="0",
            ),
            # Nearby Parking area
            display_nearby_artefacts(
                id="nearby-carpark-led",
                label="Number of nearby carparks",
                value="0",
            ),
        ]
    )
