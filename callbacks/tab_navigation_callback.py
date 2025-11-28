"""
Callback for handling tab navigation between main dashboard and weather forecast page.
"""
from dash import Input, Output, html


def register_tab_navigation_callback(app):
    """
    Register callback to handle navigation between tabs.
    
    Args:
        app: Dash app instance
    """
    @app.callback(
        [Output('main-content-area', 'style'),
         Output('weather-forecast-page', 'style')],
        Input('navigation-tabs', 'value')
    )
    def switch_page(tab_value):
        """
        Switch between main dashboard and weather forecast page.
        
        Args:
            tab_value: Selected tab value ('main' or 'weather-2h')
            
        Returns:
            Tuple of style dictionaries for main content and weather page
        """
        if tab_value == 'weather-2h':
            # Hide main content, show weather page
            main_style = {'display': 'none'}
            weather_style = {
                "display": "block",
                "padding": "20px",
                "height": "calc(100vh - 180px)",
                "width": "100%",
            }
        else:
            # Show main content, hide weather page
            main_style = {
                "display": "flex",
                "width": "100%",
                "gap": "20px",
                "padding": "10px 20px",
                "height": "calc(100vh - 180px)",
                "alignItems": "stretch",
            }
            weather_style = {'display': 'none'}
        
        return main_style, weather_style

