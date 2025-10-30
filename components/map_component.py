from dash import html, dcc
import dash_daq as daq
import dash_leaflet as dl



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


def map_component():
    """
    Default display and layout of the map component. No API is needed as this is static rendering of map for quick loading
    Uses OneMap tiles with EPSG:3857 (Web Mercator) projection.
    Coordinates are provided in EPSG:4326 (WGS84 lat/lon) format, which Leaflet converts automatically.
    """
    onemap_tiles_url = "https://www.onemap.gov.sg/maps/tiles/Night/{z}/{x}/{y}.png"
    return dl.Map(
        id="sg-map",
        #center=[1.29027, 103.851959],  # Singapore center in WGS84 [lat, lon]
        center=[1.33663363411169, 103.925744921529],
        zoom=17,
        minZoom=12,
        maxZoom=18,
        style={"width": "100%", "height": "72vh", "margin": "0"},
        children=[
            dl.TileLayer(
                url=onemap_tiles_url,
                attribution='''<img src="https://www.onemap.gov.sg/web-assets/images/logo/om_logo.png" style="height:20px;width:20px;"/>&nbsp;<a href="https://www.onemap.gov.sg/" target="_blank" rel="noopener noreferrer">OneMap</a>&nbsp;&copy;&nbsp;contributors&nbsp;&#124;&nbsp;<a href="https://www.sla.gov.sg/" target="_blank" rel="noopener noreferrer">Singapore Land Authority</a>''',
                maxNativeZoom=19,
            ),
            dl.ScaleControl(imperial=False, position="bottomleft"),
            dl.LocateControl(locateOptions={"enableHighAccuracy": True}),
            dl.LayerGroup(id="markers-layer"),
        ],
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
