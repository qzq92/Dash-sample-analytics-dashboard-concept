from dash import html, dcc

# Glossy tab styling
TAB_STYLE = {
    "padding": "12px 24px",
    "backgroundColor": "transparent",
    "border": "none",
    "borderRadius": "8px",
    "color": "#a0aec0",
    "fontWeight": "500",
    "fontSize": "14px",
    "cursor": "pointer",
    "transition": "all 0.3s ease",
    "marginRight": "8px",
}

TAB_SELECTED_STYLE = {
    "padding": "12px 24px",
    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "border": "none",
    "borderRadius": "8px",
    "color": "#ffffff",
    "fontWeight": "600",
    "fontSize": "14px",
    "boxShadow": "0 4px 15px rgba(102, 126, 234, 0.4)",
    "cursor": "pointer",
    "marginRight": "8px",
}


def build_dashboard_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.H2("Situation Dashboard"),
            # Navigation tabs with glossy styling
            html.Div(
                dcc.Tabs(
                    id="navigation-tabs",
                    value="main",
                    className="glossy-tabs",
                    children=[
                        dcc.Tab(
                            label="🏠 Main Dashboard",
                            value="main",
                            style=TAB_STYLE,
                            selected_style=TAB_SELECTED_STYLE,
                        ),
                        dcc.Tab(
                            label="🌦️ 2-Hour Weather Forecast",
                            value="weather-2h",
                            style=TAB_STYLE,
                            selected_style=TAB_SELECTED_STYLE,
                        ),
                        dcc.Tab(
                            label="📡 Realtime Weather Metrics",
                            value="realtime-weather",
                            style=TAB_STYLE,
                            selected_style=TAB_SELECTED_STYLE,
                        ),
                        dcc.Tab(
                            label="📊 Realtime Exposure Indexes",
                            value="weather-indices",
                            style=TAB_STYLE,
                            selected_style=TAB_SELECTED_STYLE,
                        ),
                    ],
                    style={
                        "height": "auto",
                        "border": "none",
                    }
                ),
                style={
                    "flex": "1",
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "padding": "10px 0",
                }
            ),
            html.A(
                html.Img(
                    id="plotly-logo",
                    src=r"../assets/dash-logo.png",
                    style={"height": "40px"},
                ),
                href="https://plotly.com/dash/",
            ),
        ],
        style={
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "center",
            "padding": "0 20px",
            "background": "linear-gradient(180deg, #1a202c 0%, #2d3748 100%)",
            "borderBottom": "1px solid #4a5568",
        },
    )