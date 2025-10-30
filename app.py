# Import packages
from dash import Dash, html
import dash_bootstrap_components as dbc
import sys
import logging
from dotenv import load_dotenv
# Load environment variables and logging
load_dotenv()

from components.banner_component import build_dashboard_banner
from components.map_component import map_component, show_descriptive_stats, radius_selection_button, build_search_bar
from components.tab_component import display_tabs

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
                            id="Descriptive-stats-content-container",
                            # Right column for map
                            children=[
                                # First row
                                build_search_bar(),
                                radius_selection_button(),
                                # Next row
                                #show_descriptive_stats(),
                                # Next div showing details in tab format(bus,bicycle,taxi,carpark and nearby available cctv footage)
                                #display_tabs(),
                                #Content of tab
                                html.Div(id='tab-content')
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