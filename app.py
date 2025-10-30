# Import packages
from dash import Dash, html
import dash_bootstrap_components as dbc
import sys
import logging
from dotenv import load_dotenv
# Load environment variables and logging
load_dotenv(override=True)

from components.banner_component import build_dashboard_banner
from components.map_component import map_component, show_descriptive_stats, search_bar, nearest_mrt_panel
from components.tab_component import display_tabs
from callbacks.map_callback import register_search_callbacks

# Dash instantiation ---------------------------------------------------------#
app = Dash(__name__,
           meta_tags=[{
               "name": "viewport",
               "content": "width=device-width",
               "initial-scale": "1.0"}],
           external_stylesheets=[dbc.themes.DARKLY],
           suppress_callback_exceptions = True, #
           title="SimpleDashboard Demo"
        )
register_search_callbacks(app)

# Dashboard app layout ------------------------------------------------------#
app.layout = html.Div(
    id="root",
    children=[
        # Header/Banner -------------------------------------------------#
        html.Div(
            id="header",
            children=[
                build_dashboard_banner()
            ],
        ),

        # App Container ------------------------------------------#
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    className="row",
                    children=[
                        # Left column for map placement
                        html.Div(
                            id="left-column",
                            className="seven columns",
                            children=[map_component()],
                            style={
                                "display": "inline-block",
                                "padding": "20px 10px 10px 40px",
                                "width": "59%",
                            },
                        ),
                        # Right column for Information around the selected point ----------------------#
                        html.Div(
                            id="Search-bar-container",
                            # Right column for map
                            children= [search_bar(),
                                nearest_mrt_panel(),
                                # Next row
                                #show_descriptive_stats(),
                            ],
                            style={
                                "display": "inline-block",
                                "padding": "20px 20px 10px 10px",
                                "width": "39%",
                            },
                        ),
                    ],
                ),
            ],
        ),
    ]
)

if __name__ == '__main__':
    logging.info(sys.version)

    # If running locally in Anaconda env:
    if "conda-forge" in sys.version:
        app.run(debug=True)
    else:
        app.run(debug=False, host='0.0.0.0', port=8050)
    # Set app title
    app.title = "SG Dashboard"