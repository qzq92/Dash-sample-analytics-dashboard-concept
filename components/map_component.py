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
        style={"width": "100%", "marginBottom": "8px"},
        searchable=True,
        clearable=True,
        optionHeight=40,
        maxHeight=240,
    )


def nearest_mrt_panel():
    return html.Div(
        id="nearest-mrt-panel",
        children=[],
        style={"marginTop": "8px"}
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
                            "padding": "10px",
                            "color": "#999",
                            "fontSize": "14px",
                            "fontStyle": "italic"
                        }
                    )
                ],
                style={"marginTop": "8px"}
            )
        ]
    )


def map_component(lat=1.35, lon=103.81):
    """
    Default display and layout of the map component. No API is needed as this is static rendering of map for quick loading
    Coordinates are provided in EPSG:4326 (WGS84 lat/lon) format, which Leaflet converts automatically.
    
    Note: The map center will be updated via callback when search bar value changes.
    The initial center coordinates are used only for initial rendering.
    """
    onemap_tiles_url = "https://www.onemap.gov.sg/maps/tiles/Night/{z}/{x}/{y}.png"
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
            zoom=12,
            minZoom=11,
            maxZoom=20,
            # Map bounds to restrict view to Singapore area
            maxBounds=[[1.1304753, 103.6020882], [1.492007, 104.145897]],
            style={"width": "100%", "height": "100%", "margin": "0"},
            children=[
                dl.TileLayer(
                    url=onemap_tiles_url,
                    attribution=onemap_attribution,
                    maxNativeZoom=19,
                ),
                dl.ScaleControl(imperial=False, position="bottomleft"),
                dl.LocateControl(locateOptions={"enableHighAccuracy": True}),
                dl.LayerGroup(id="markers-layer"),
                dl.LayerGroup(id="bus-stop-markers"),
                dl.LayerGroup(id="carpark-markers"),
            ],
        )
    ], style={"width": "100%", "height": "100%", "display": "flex", "flexDirection": "column"})


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
                    "padding": "8px 12px",
                    "backgroundColor": "#2c3e50",
                    "borderRadius": "4px",
                    "fontSize": "13px",
                    "color": "#fff",
                    "fontFamily": "monospace",
                    "textAlign": "center",
                    "border": "1px solid #444"
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
    # Wrapper to maintain existing references; delegates to display_artefacts
    return display_artefacts(id=id, label=label, value=value, size=size)


def show_descriptive_stats():
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

            # Bicycle Parking area
            display_nearby_artefacts(
                id="nearby-bicycle-parking-led",
                label="Number of nearby bicycle parking points",
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
