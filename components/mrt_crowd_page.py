"""
Component for the MRT/LRT Station Crowd page.
Displays real-time crowd density levels for MRT and LRT stations.
"""
from dash import html, dcc


def mrt_crowd_page():
    """
    Create the MRT/LRT Station Crowd page layout.
    Features: Real-time crowd density levels displayed in card format.

    Returns:
        HTML Div containing the MRT/LRT Station Crowd page section
    """
    return html.Div(
        id="mrt-crowd-page",
        style={
            "display": "none",  # Hidden by default
            "padding": "1.25rem",
            "height": "calc(100vh - 7.5rem)",
            "width": "100%",
        },
        children=[
            # Main content container
            html.Div(
                id="mrt-crowd-content",
                style={
                    "height": "calc(100% - 3.125rem)",
                    "maxWidth": "112.5rem",
                    "margin": "0 auto",
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "1.25rem",
                },
                children=[
                    # Header with toggle button
                    html.Div(
                        style={
                            "display": "flex",
                            "justifyContent": "space-between",
                            "alignItems": "center",
                            "marginBottom": "0.625rem",
                        },
                        children=[
                            # Toggle button (Header removed as requested)
                            html.Div(
                                [
                                    html.Button(
                                        "View: By Line",
                                        id="mrt-crowd-view-toggle",
                                        n_clicks=0,
                                        style={
                                            "padding": "0.5rem 1rem",
                                            "backgroundColor": "#00BCD4",
                                            "color": "#fff",
                                            "border": "none",
                                            "borderRadius": "0.25rem",
                                            "cursor": "pointer",
                                            "fontWeight": "600",
                                            "fontSize": "0.875rem",
                                            "transition": "background-color 0.2s",
                                        }
                                    ),
                                ],
                                style={"marginLeft": "auto"} # Push to right
                            ),
                        ]
                    ),
                    # Cards Container (Expandable cards will be injected here)
                    html.Div(
                        id="mrt-crowd-station-list",
                        style={
                            "flex": "1",
                            "overflowY": "auto",
                            "minHeight": "0",
                        },
                        children=[
                            html.P(
                                "Loading station crowd data...",
                                style={
                                    "color": "#999",
                                    "textAlign": "center",
                                    "padding": "1.25rem",
                                }
                            )
                        ]
                    ),
                ]
            ),
            # Hidden divs to maintain callback compatibility
            html.Div(id="mrt-crowd-count-value", style={"display": "none"}),
            # Store for crowd data
            dcc.Store(id="mrt-crowd-data-store", data=None),
            # Interval for auto-refresh (every 10 minutes as per API update frequency)
            dcc.Interval(
                id='mrt-crowd-interval',
                interval=10*60*1000,  # Update every 10 minutes
                n_intervals=0
            ),
        ]
    )

