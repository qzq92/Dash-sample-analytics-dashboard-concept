from dash import html, dcc
import dash_daq as daq
import dash_leaflet as dl
import os


def radius_selection_button():
    return html.Div(
        id="Select-options",
        children=[
            dcc.RadioItems(['500 m radius', '1 km radius'], '500 m radius', inline=True)
        ],
        style={"textAlign": "right"},
    )


def build_search_bar():
    return dcc.Input(
        id="input_search",
        type="text",
        placeholder="Search address or place (OneMap)",
        debounce=True,
        style={"width": "100%", "marginBottom": "8px"},
    )


def map_component():
    """
    Default display and layout of the map component. No API is needed as this is static rendering of map for quick loading
    """
    onemap_tiles_url = "ttps://www.onemap.gov.sg/maps/tiles/Night/{z}/{x}/{y}.png"
    return dl.Map(
        id="sg-map",
        center=[1.29027, 103.851959],
        zoom=12,
        maxZoom=12,
        style={"width": "100%", "height": "72vh", "margin": "0"},
        children=[
            dl.TileLayer(
                url=onemap_tiles_url,
                attribution="Map data © contributors, tiles © OneMap Singapore",
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
