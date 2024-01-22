from dash import Dash, dcc, html, Input, Output, callback
from .conf.api_key import OSM_API_TOKEN
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go


#SG FIX LAT



@callback(
# Define Output/Input(id, value)
Output(component_id="onestreetmap", component_property='figure'),
[Input("onestreetmap", 'clickData')])
def update_map(n_clicks):
    map_figure = {
        'data': [
            go.Scattermapbox(
                lat=[32],
                lon=[-110],
                mode='markers',
                marker=dict(
                    size=4
                )
            )
        ],
        # Map layout
        'layout': go.Layout(
            autosize=True,
            hovermode='closest',
            mapbox=dict(
                accesstoken=OSM_API_TOKEN,
                center=dict(
                    lat=40,
                    lon=-100
                ),
                zoom=8
            )
        )}

    fig.update_layout(map_figure)
    return fig