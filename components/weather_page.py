"""
Component for the 2-hour weather forecast page.
"""
from dash import html


def weather_forecast_page():
    """
    Create the 2-hour weather forecast page layout.
    This retains the same container styling as the original component.
    
    Returns:
        HTML Div containing the weather forecast section
    """
    return html.Div(
        id="weather-forecast-page",
        style={
            "display": "none",  # Hidden by default, shown when weather tab is selected
            "padding": "20px",
            "height": "calc(100vh - 180px)",
            "width": "100%",
        },
        children=[
            # Weather forecast section with same styling as original
            html.Div(
                id="weather-forecast-section",
                style={
                    "backgroundColor": "#4a5a6a",
                    "borderRadius": "5px",
                    "padding": "10px",
                    "display": "flex",
                    "flexDirection": "column",
                    "height": "100%",
                    "maxWidth": "1200px",
                    "margin": "0 auto",
                },
                children=[
                    html.H4(
                        "Next 2-Hour Weather Forecast",
                        style={
                            "textAlign": "center",
                            "margin": "10px 0",
                            "color": "#fff",
                            "fontWeight": "700"
                        }
                    ),
                    html.Div(
                        id="weather-2h-content",
                        children=[
                            html.P("Loading...", style={"textAlign": "center", "padding": "20px", "color": "#999"})
                        ],
                        style={
                            "padding": "10px 20px",
                            "overflowY": "auto",
                            "flex": "1",
                        }
                    ),
                ]
            ),
        ]
    )

