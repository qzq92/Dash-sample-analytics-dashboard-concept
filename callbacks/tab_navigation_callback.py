"""
Callback for handling tab navigation between dashboard pages.
"""
from dash import Input, Output


def register_tab_navigation_callback(app):
    """
    Register callback to handle navigation between tabs.

    Args:
        app: Dash app instance
    """
    @app.callback(
        [Output('main-content-area', 'style'),
         Output('weather-forecast-page', 'style'),
         Output('realtime-weather-page', 'style'),
         Output('weather-indices-page', 'style'),
         Output('search-bar-section', 'style')],
        Input('navigation-tabs', 'value')
    )
    def switch_page(tab_value):
        """
        Switch between dashboard pages.

        Args:
            tab_value: Selected tab value
                ('main', 'weather-2h', 'realtime-weather', 'weather-indices')

        Returns:
            Tuple of style dictionaries for each page and search bar
        """
        # Default hidden styles
        main_style = {'display': 'none'}
        weather_2h_style = {'display': 'none'}
        realtime_style = {'display': 'none'}
        indices_style = {'display': 'none'}
        search_bar_style = {'display': 'none'}

        if tab_value == 'weather-2h':
            weather_2h_style = {
                "display": "block",
                "padding": "20px",
                "height": "calc(100vh - 120px)",
                "width": "100%",
            }
        elif tab_value == 'realtime-weather':
            realtime_style = {
                "display": "block",
                "padding": "20px",
                "height": "calc(100vh - 120px)",
                "width": "100%",
            }
        elif tab_value == 'weather-indices':
            indices_style = {
                "display": "block",
                "padding": "20px",
                "height": "calc(100vh - 120px)",
                "width": "100%",
            }
        else:
            # Main dashboard - show search bar
            main_style = {
                "display": "flex",
                "width": "100%",
                "gap": "20px",
                "padding": "10px 20px",
                "height": "calc(100vh - 180px)",
                "alignItems": "stretch",
            }
            search_bar_style = {
                "padding": "15px 40px",
                "backgroundColor": "#2c3e50",
                "borderBottom": "1px solid #444",
            }

        return (main_style, weather_2h_style, realtime_style,
                indices_style, search_bar_style)

    # Clientside callback to fix map rendering after tab switch and force center
    app.clientside_callback(
        """
        function(tab_value) {
            var mapTabs = ['weather-2h', 'realtime-weather', 'weather-indices'];
            if (mapTabs.includes(tab_value)) {
                // Delay to ensure DOM is fully updated
                setTimeout(function() {
                    // Find all Leaflet map containers and invalidate size
                    var maps = [
                        'weather-2h-map',
                        'realtime-weather-map',
                        'weather-indices-map'
                    ];
                    maps.forEach(function(id) {
                        var mapEl = document.getElementById(id);
                        if (mapEl) {
                            // Trigger resize event for simple fix
                            window.dispatchEvent(new Event('resize'));
                        }
                    });
                }, 200);
                
                // Second check for reliability
                setTimeout(function() {
                    window.dispatchEvent(new Event('resize'));
                }, 500);
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output('weather-2h-map', 'id'),
        Input('navigation-tabs', 'value'),
        prevent_initial_call=True
    )

