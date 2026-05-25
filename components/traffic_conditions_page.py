"""
Component for the Traffic Conditions page.
Displays all LTA traffic camera feeds in a grid layout.
"""
from dash import html, dcc
from conf.page_layout_config import PAGE_PADDING, PAGE_HEIGHT


def traffic_conditions_page():
    """
    Create the Traffic Conditions page layout.
    Displays all LTA traffic camera feeds in a 6-column grid.

    Returns:
        HTML Div containing the Traffic Conditions section
    """
    return html.Div(
        id="traffic-conditions-page",
        style={
            "display": "none",  # Hidden by default
            "padding": PAGE_PADDING,
            "height": PAGE_HEIGHT,
            "width": "100%",
        },
        children=[
            html.Div(
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "height": "100%",
                    "gap": "0.75rem",
                },
                children=[
                    # LTA video feed discontinuation notice
                    html.Div(
                        style={
                            "display": "flex",
                            "alignItems": "flex-start",
                            "gap": "0.75rem",
                            "backgroundColor": "#2d2000",
                            "border": "1px solid #b45309",
                            "borderLeft": "4px solid #f59e0b",
                            "borderRadius": "0.5rem",
                            "padding": "0.875rem 1rem",
                        },
                        children=[
                            html.Span(
                                "⚠️",
                                style={"fontSize": "1.1rem", "lineHeight": "1.5", "flexShrink": "0"},
                            ),
                            html.Div(
                                children=[
                                    html.Span(
                                        "LTA Traffic Camera Feed Discontinuation — ",
                                        style={
                                            "fontWeight": "700",
                                            "color": "#fbbf24",
                                            "fontSize": "0.85rem",
                                        },
                                    ),
                                    html.Span(
                                        "The Land Transport Authority (LTA) has announced that it will be "
                                        "switching off most traffic condition video feeds. Some camera feeds "
                                        "displayed here may no longer be available or may show as unavailable.",
                                        style={
                                            "color": "#fde68a",
                                            "fontSize": "0.85rem",
                                            "lineHeight": "1.5",
                                        },
                                    ),
                                ]
                            ),
                        ]
                    ),
                    # Camera grid container
                    html.Div(
                        id="traffic-conditions-content",
                        style={
                            "flex": "1",
                            "backgroundColor": "#2a3a4a",
                            "borderRadius": "0.5rem",
                            "padding": "1rem",
                            "overflowY": "auto",
                        },
                        children=[]  # Will be populated by callback
                    ),
                ]
            ),
            # Interval for auto-refresh (every 2 minutes)
            dcc.Interval(
                id='traffic-conditions-interval',
                interval=2*60*1000,  # Update every 2 minutes
                n_intervals=0
            ),
        ]
    )

