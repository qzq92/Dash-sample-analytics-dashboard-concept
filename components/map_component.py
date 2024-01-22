import dash
import dash_core_components as dcc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import dash_daq as daq
import dash_html_components as html

def build_dashboard_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("Simple Dashboard Demo"),
                    html.H6("Showcasing nearby transportation option and activities"),
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.Button(
                        id="learn-more-button", children="LEARN MORE", n_clicks=0
                    ),
                    html.A(
                        html.Img(src=r"assets/dash-logo.png"),
                        href="https://plotly.com/dash/",
                    ),
                ],
            ),
        ],
    )

def radius_selection_button():
    return html.Div(
        id="Select-options",
        children=[   
            dcc.RadioItems(['500m Radius', '1Km Radius'], '500m Radius', inline=True)
        ],
        style={"textAlign": "right"},
    ),


def fig_map(mapbox_default_key: str):

    # Display traffic cam locations based on existing known data
    traffic_cam_locations_df = pd.read_csv("data/traffic_cam_locations.csv")
    # Set mapbox key for plotly express to facilitate switch to other mapbox style as necessary
    px.set_mapbox_access_token(mapbox_default_key)
    fig = px.scatter_mapbox(traffic_cam_locations_df,
                            lat="Lat",
                            lon="Lon",
                            zoom=7,
                            center=dict(lon=103.851959, lat=1.290270),
                            mapbox_style="open-street-map",
                            title="Map of Singapore",
                            hover_name="Description of Location" #Appear in tooltip
                            )

    # Limit map bounds
    fig.update(mapbox_bounds={"west":1.25, "east":1.35, "south":104, "north":103})
    fig.update(margin={"l":0, "r":0, "b":0, "t":0})
    return fig



def build_street_map_component(mapbox_default_key: str):
    return html.Div(
        id="left-column",
        children=[
            # Search bar
            dcc.Input(
                id="input_search",
                type="text",
                placeholder="input search location",
            ),
            html.Div(
                id="osm-map-container",
                children=[
                    html.P("Click on anywhere on the map"),
                    dcc.Graph(
                        id="map",
                        config={'scrollZoom': True},
                        figure=fig_map(mapbox_default_key)
                    ),
                ],
            ),
        ],
        style={
            "display": "inline-block",
            "padding": "20px 10px 10px 40px",
            "width": "59%",
        },
        className="seven columns",
    )


def display_nearby_artefacts(id: str, label: str, value: str, size: int=50,):
    return html.Div([daq.LEDDisplay(
        id=id,
        label=label,
        value=value,
        size=size)],
    style={'display': 'flex', 'justify-content': 'center'})


def show_descriptive_stats():
    return html.Div(
        id="Descriptive-stats",
        children=[
            # Bus stop
            display_nearby_artefacts(
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

def display_tabs():
    # To show clickable tabs
    return html.Div(
        id = "tabs",
        classname="tabs",
        children = dcc.Tabs(
            id="multi-tabs",
            value="tab2",
            className="custom-tabs",
            # Define constituent tabs
            children=[
                dcc.Tab(
                    id="bus-stop-tab",
                    label="Nearest bus stop",
                    value="bus-stop-tab",
                ),
                dcc.Tab(
                    id="bicycle-tab",
                    label="Nearest bicycle parking",
                    value="bicycle-tab",
                ),
                dcc.Tab(
                    id="taxi-stand-tab",
                    label="Nearest taxi stand",
                    value="taxi-stand-tab",
                ),
                dcc.Tab(
                    id="carpark-tab",
                    label="Nearest carpark",
                    value="carpark-tab",
                ),
                dcc.Tab(
                    id="traffic-cctv-tab",
                    label="Nearest available CCTV footage",
                    value="cctv-tab",
                ),
            ]
        )
    )
