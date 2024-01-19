from dash import Dash, dcc, html, Input, Output, callback

@callback(
    Output('tabs-example-content-1', 'children'),
    Input('tabs-example-1', 'value')
)
def render_content(tab):
    if tab == 'bus-stop-tab':
        return html.Div([
            html.H3('Tab content 1'),
        ])
    elif tab == 'bicycle-tab':
        return html.Div([
            html.H3('Tab content 2'),
        ])
    elif tab == 'taxi-stand-tab':
        return html.Div([
            html.H3('Tab content 2'),
        ])
    elif tab == 'carpark-tab':
        return html.Div([
            html.H3('Tab content 2'),
        ])