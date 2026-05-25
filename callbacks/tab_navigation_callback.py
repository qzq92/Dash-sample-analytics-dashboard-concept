"""
Callback for handling tab navigation between dashboard pages.
"""
from dash import Input, Output, State, no_update

from components.realtime_weather_page import realtime_weather_page
from components.weather_indices_page import weather_indices_page
from components.transport_page import transport_page
from components.bus_arrival_page import bus_arrival_page
from components.nearby_transport_page import nearby_transport_page
from components.travel_times_page import travel_times_page
from components.analytics_forecast_page import analytics_forecast_page
from components.traffic_conditions_page import traffic_conditions_page

# Ordered list of tab values and their corresponding page builder functions.
# Index N in _TAB_KEYS maps to index N in _PAGE_BUILDERS.
_TAB_KEYS = [
    "realtime-weather",
    "weather-indices",
    "transport",
    "bus-arrival",
    "nearby-transport",
    "travel-times",
    "analytics-forecast",
    "traffic-conditions",
]
_PAGE_BUILDERS = [
    realtime_weather_page,
    weather_indices_page,
    transport_page,
    bus_arrival_page,
    nearby_transport_page,
    travel_times_page,
    analytics_forecast_page,
    traffic_conditions_page,
]


def register_tab_navigation_callback(app):
    """
    Register callback to handle navigation between tabs.

    Args:
        app: Dash app instance
    """
    @app.callback(
        [Output('main-content-area', 'style'),
         Output('realtime-weather-page', 'style'),
         Output('weather-indices-page', 'style'),
         Output('transport-page', 'style'),
         Output('bus-arrival-page', 'style'),
         Output('nearby-transport-page', 'style'),
         Output('travel-times-page', 'style'),
         Output('analytics-forecast-page', 'style'),
         Output('traffic-conditions-page', 'style'),
         Output('search-bar-section', 'style')],
        Input('navigation-tabs', 'value')
    )
    def switch_page(tab_value):
        """
        Switch between dashboard pages.

        Args:
            tab_value: Selected tab value
                ('main', 'realtime-weather', 'weather-indices', 'transport',
                 'nearby-transport', 'travel-times', 'analytics-forecast')

        Returns:
            Tuple of style dictionaries for each page and search bar
        """
        # Default hidden styles
        main_style = {'display': 'none'}
        realtime_style = {'display': 'none'}
        indices_style = {'display': 'none'}
        transport_style = {'display': 'none'}
        bus_arrival_style = {'display': 'none'}
        nearby_transport_style = {'display': 'none'}
        travel_times_style = {'display': 'none'}
        analytics_forecast_style = {'display': 'none'}
        traffic_conditions_style = {'display': 'none'}
        search_bar_style = {'display': 'none'}

        if tab_value == 'realtime-weather':
            realtime_style = {
                "display": "block",
                "padding": "0.5rem",
                "height": "calc(100vh - 7.5rem)",
                "width": "100%",
            }
        elif tab_value == 'weather-indices':
            indices_style = {
                "display": "block",
                "padding": "0.5rem",
                "height": "calc(100vh - 7.5rem)",
                "width": "100%",
            }
        elif tab_value == 'transport':
            transport_style = {
                "display": "block",
                "padding": "0.5rem",
                "height": "calc(100vh - 7.5rem)",
                "width": "100%",
            }
        elif tab_value == 'bus-arrival':
            bus_arrival_style = {
                "display": "block",
                "padding": "0.5rem",
                "height": "calc(100vh - 7.5rem)",
                "width": "100%",
            }
        elif tab_value == 'nearby-transport':
            nearby_transport_style = {
                "display": "block",
                "padding": "0.5rem",
                "height": "calc(100vh - 7.5rem)",
                "width": "100%",
            }
        elif tab_value == 'travel-times':
            travel_times_style = {
                "display": "block",
                "padding": "0.5rem",
                "height": "calc(100vh - 7.5rem)",
                "width": "100%",
            }
        elif tab_value == 'analytics-forecast':
            analytics_forecast_style = {
                "display": "block",
                "padding": "0.5rem",
                "height": "calc(100vh - 7.5rem)",
                "width": "100%",
            }
        elif tab_value == 'traffic-conditions':
            traffic_conditions_style = {
                "display": "block",
                "padding": "0.5rem",
                "height": "calc(100vh - 7.5rem)",
                "width": "100%",
            }
        else:
            # Main dashboard (search bar is now inside map container)
            main_style = {
                "display": "flex",
                "width": "100%",
                "gap": "0.5rem",
                "padding": "0.25rem 0.5rem",
                "height": "calc(100vh - 7.5rem)",
                "alignItems": "stretch",
            }
            # Keep search bar section hidden (placeholder for callback compatibility)
            search_bar_style = {"display": "none"}

        return (main_style, realtime_style, indices_style, transport_style,
                bus_arrival_style, nearby_transport_style, travel_times_style, analytics_forecast_style, traffic_conditions_style, search_bar_style)

    @app.callback(
        [Output("realtime-weather-page", "children"),
         Output("weather-indices-page", "children"),
         Output("transport-page", "children"),
         Output("bus-arrival-page", "children"),
         Output("nearby-transport-page", "children"),
         Output("travel-times-page", "children"),
         Output("analytics-forecast-page", "children"),
         Output("traffic-conditions-page", "children"),
         Output("initialized-tabs", "data")],
        Input("navigation-tabs", "value"),
        State("initialized-tabs", "data"),
        prevent_initial_call=True,
    )
    def lazy_load_tab(tab_value, initialized_tabs):
        """
        Populate a tab page's children the first time the user visits it.
        Subsequent visits return no_update so the built layout is preserved.
        """
        if tab_value == "main" or tab_value in initialized_tabs:
            return [no_update] * 9  # 8 page children + store

        results = [no_update] * 8
        if tab_value in _TAB_KEYS:
            idx = _TAB_KEYS.index(tab_value)
            # Build only the inner children, not the outer wrapper div
            # (the wrapper div with its id already exists as the placeholder).
            results[idx] = _PAGE_BUILDERS[idx]().children

        return results + [initialized_tabs + [tab_value]]

    # Clientside callback to fix map rendering after tab switch
    # This triggers invalidateSize() on Leaflet maps when tabs change
    app.clientside_callback(
        """
        function(tab_value) {
            // Map ID for each tab
            var tabMapIds = {
                'main': 'sg-map',
                'realtime-weather': 'realtime-weather-map',
                'weather-indices': 'weather-indices-map',
                'transport': 'transport-map',
                'bus-arrival': 'bus-arrival-map',
                'nearby-transport': 'nearby-transport-map'
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
        Output('bus-arrival-map', 'id'),
        Input('navigation-tabs', 'value'),
        prevent_initial_call=True
    )

