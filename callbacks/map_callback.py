from dash import Dash, dcc, html, Input, Output, callback
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import requests


def search_location_via_onemap_info(searchVal: str, returnGeom : str ="Y", getAddrDetails: str = "N", onemap_url = "https://www.onemap.gov.sg/api/common/elastic/search?"):

    searchVal = str(searchVal)
    # Space replacement for url construct
    searchVal = searchVal.strip().replace(" ","%20")

    # Construct search url
    onemap_search_url = onemap_url + f"searchVal={searchVal}&returnGeom={returnGeom}&getAddrDetails={getAddrDetails}"
    print(onemap_search_url)

    req_headers = {"User-agent": "qzq_test",
                   "Content-Type": "application/json"
                  }
    res = requests.request("GET", onemap_search_url, headers=req_headers)
    # Check the status code before extending the number of posts
    if res.status_code == 200:
        print(f"Request successful with status code {res.status_code}")
        the_json = res.json()
        # Page 1 is the default return
        nearest_match = the_json["results"][0]
        
        return nearest_match
    else:
        print(f"Return unsuccessful with status code {res.status_code}")
        # Raise if HTTPError occured
        res.raise_for_status()

        return {}

# Callback for map update using input search string of address to 
@callback(
Output(component_id="onestreetmap", component_property='figure'),
[Input("input_search", 'clickData')])
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