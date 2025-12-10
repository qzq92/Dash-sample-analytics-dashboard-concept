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

    # Clientside callback to fix map rendering after tab switch
    # This triggers invalidateSize() on Leaflet maps when tabs change
    app.clientside_callback(
        """
        function(tab_value) {
            // Map ID for each tab
            var tabMapIds = {
                'main': 'sg-map',
                'weather-2h': 'weather-2h-map',
                'realtime-weather': 'realtime-weather-map',
                'weather-indices': 'weather-indices-map'
            };
            
            var targetMapId = tabMapIds[tab_value];
            if (!targetMapId) {
                return window.dash_clientside.no_update;
            }
            
            // Function to invalidate map size
            function invalidateMapSize() {
                var mapContainer = document.getElementById(targetMapId);
                if (mapContainer) {
                    // Try to find the Leaflet map instance
                    // Leaflet stores the map instance on the container element
                    if (mapContainer._leaflet_map) {
                        mapContainer._leaflet_map.invalidateSize();
                    } else {
                        // Fallback: trigger window resize event which Leaflet listens to
                        window.dispatchEvent(new Event('resize'));
                    }
                }
            }
            
            // Delay to ensure DOM is fully updated after display:none -> display:flex/block
            setTimeout(invalidateMapSize, 100);
            setTimeout(invalidateMapSize, 300);
            setTimeout(invalidateMapSize, 500);
            
            return window.dash_clientside.no_update;
        }
        """,
        Output('weather-2h-map', 'id'),
        Input('navigation-tabs', 'value'),
        prevent_initial_call=True
    )

