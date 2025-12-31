"""
Component for train service alerts display on the main dashboard.
"""
from dash import html


def train_service_alerts_component():
    """
    Create the train service alerts component for the main dashboard.
    
    Returns:
        HTML Div containing the train service alerts section
    """
    return html.Div(
        id="train-service-alerts-container",
        style={
            "backgroundColor": "#4a5a6a",
            "borderRadius": "8px",
            "padding": "0.25rem",
            "display": "flex",
            "flexDirection": "column",
            "gap": "8px",
        },
        children=[
            html.Div(
                style={
                    "display": "flex",
                    "flexDirection": "row",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                },
                children=[
                    html.Span(
                        "🚇 MRT/LRT service alerts",
                        style={
                            "color": "#fff",
                            "fontWeight": "600",
                            "fontSize": "13px"
                        }
                    ),
                    html.Div(style={"flex": "1"}),  # Spacer
                ]
            ),
            html.Div(
                id="train-service-alerts-content",
                style={
                    "flex": "1",
                    "overflowY": "auto",
                    "overflowX": "hidden",
                    "minHeight": "0",
                },
                children=[
                    html.Div(
                        id="train-service-alerts-status",
                        children=[
                            html.P("Loading...", style={
                                "color": "#999",
                                "fontSize": "0.75rem"
                            })
                        ]
                    )
                ]
            )
        ]
    )

