import dash_html_components as html

def build_dashboard_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("Simple Dashboard Demo"),
                    html.H6("Showcasing nearby transportation option and activities"),
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.Button(
                        id="learn-more-button", children="LEARN MORE", n_clicks=0
                    ),
                    html.A(
                        html.Img(src=r"../assets/dash-logo.png"),
                        href="https://plotly.com/dash/",
                    ),
                ],
            ),
        ],
    )