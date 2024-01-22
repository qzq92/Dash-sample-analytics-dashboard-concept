from dash import Dash, dcc, html, Input, Output, callback

#--Define tab components-------------------------------------------------------
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


# Default display when no tab is selected
def build_default_display():
    return html.Div(
        html.P("Select a tab to display relevant content")
    )

def build_bus_stop_tab():
    return html.Div([

    ])


def build_bicycle_parking_stops_tab():
    return html.Div([

    ])

def build_taxi_stands_tab():
    return html.Div([

    ])

def build_carpark_tab():
    return html.Div([

    ])
def build_traffic_cctv_tab():
    return html.Div([

    ])