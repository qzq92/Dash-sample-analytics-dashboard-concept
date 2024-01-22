from dash import Dash, dcc, html, Input, Output, callback

# This script governs the building and rendering of detailed nearby bus stop, bicycle parking spots, taxi stand and carpark locations and other relevant info. 

#--Define tab-------------------------------------------------------------------

# Default display when no tab is selected
def build_default_display():
    return html.Div(
        html.P("Select a tab to display relevant content")
    )

def build_bus_stop_tab():
    pass


def build_bicycle_parking_stops_tab():
    pass



# Define callback when tabs are selected
@callback(
    Output('tab-content', 'children'),
    Input('multi-tabs', 'value')
)
def render_content(tab):
    if tab == 'bus-stop-tab':
        return build_bus_stop_tab()
    elif tab == 'bicycle-tab':
        return build_bicycle_parking_stops_tab()
    elif tab == 'taxi-stand-tab':
        return build_taxi_stands_tab()
    elif tab == 'carpark-tab':
        return build_carpark_tab()
    elif tab == "traffic-cctv-tab"
        return build_traffic_cctv_tab()
    else:
        return build_default_display()