from dash import html

def build_dashboard_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.H2("Singapore City Dashboard (Simplified)"),
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
            "padding": "0 10px",
        },
    )