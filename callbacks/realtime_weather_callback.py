"""
Callback functions for handling realtime weather readings from data.gov.sg v2 API.
References:
- Air Temperature: https://api-open.data.gov.sg/v2/real-time/api/air-temperature
- Rainfall: https://api-open.data.gov.sg/v2/real-time/api/rainfall
- Relative Humidity: https://api-open.data.gov.sg/v2/real-time/api/relative-humidity
- Wind Speed: https://api-open.data.gov.sg/v2/real-time/api/wind-speed
"""
import os
import time
import requests
from dash import Input, Output, State, html, callback_context
from dotenv import load_dotenv
import dash_leaflet as dl
from conf.windspeed_icon import get_windspeed_icon, get_windspeed_description

load_dotenv(override=True)


def fetch_realtime_data(endpoint):
    """
    Fetch realtime weather data from data.gov.sg v2 API.

    Args:
        endpoint: API endpoint (e.g., 'air-temperature', 'rainfall')

    Returns:
        Dictionary containing weather data or None if error
    """
    api_key = os.getenv('DATA_GOV_API')
    if not api_key:
        print("DATA_GOV_API environment variable not set")
        return None

    # Only support v2 API endpoints
    supported = ['air-temperature', 'rainfall', 'relative-humidity', 'wind-speed']
    if endpoint not in supported:
        print(f"Unsupported endpoint: {endpoint}")
        return None

    url = f"https://api-open.data.gov.sg/v2/real-time/api/{endpoint}"
    headers = {
        "X-API-Key": api_key,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        print(f"Realtime {endpoint} API failed: status={res.status_code}")
    except (requests.exceptions.RequestException, ValueError) as error:
        print(f"Error calling {endpoint} API: {error}")
    return None


def build_station_lookup(data):
    """Build a lookup dictionary from station_id to station metadata."""
    if not data or 'data' not in data or 'stations' not in data['data']:
        return {}
    stations = data['data']['stations']
    return {s['id']: s for s in stations}


def _create_reading_div(name, display_value, color):
    """Create a single reading row with name and value."""
    return html.Div(
        [
            html.Span(
                name,
                style={
                    "fontSize": "11px",
                    "color": "#ccc",
                    "flex": "1",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis",
                    "whiteSpace": "nowrap",
                }
            ),
            html.Span(
                display_value,
                style={
                    "fontSize": "12px",
                    "fontWeight": "600",
                    "color": color,
                    "marginLeft": "8px",
                    "whiteSpace": "nowrap",
                }
            ),
        ],
        style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "space-between",
            "padding": "4px 8px",
            "backgroundColor": "#3a4a5a",
            "borderRadius": "4px",
            "marginBottom": "4px",
        }
    )


def _build_grid_content(reading_divs, timestamp):
    """Build single column content with optional timestamp footer."""
    content = [
        html.Div(
            reading_divs,
            style={
                "display": "flex",
                "flexDirection": "column",
                "flex": "1",
                "overflowY": "auto",
                "overflowX": "hidden",
            }
        )
    ]
    if timestamp:
        content.append(
            html.Div(
                f"Updated: {timestamp}",
                style={
                    "fontSize": "10px",
                    "color": "#888",
                    "marginTop": "5px",
                    "textAlign": "right",
                    "fontStyle": "italic",
                    "flexShrink": "0",
                }
            )
        )
    return html.Div(
        content,
        style={
            "display": "flex",
            "flexDirection": "column",
            "height": "100%",
            "overflow": "hidden",
        }
    )


def _get_error_div():
    """Return error message div."""
    return html.P("Error retrieving data", style={"color": "#f44", "fontSize": "12px"})


def format_readings_grid(data, unit, color):
    """
    Format readings data as a compact grid. Handles v2 API response structure.

    Args:
        data: API response data
        unit: Unit of measurement (e.g., '°C', 'mm', '%')
        color: Text color for values

    Returns:
        HTML Div with grid of readings
    """
    if not data or 'data' not in data:
        return _get_error_div()

    api_data = data['data']
    if 'readings' not in api_data or not api_data['readings']:
        return _get_error_div()

    # Extract unit from API response
    api_unit = api_data.get('readingUnit', '')
    if api_unit:
        unit = _normalize_unit(api_unit, unit)

    reading_item = api_data['readings'][0]
    readings = reading_item.get('data', [])
    if not readings:
        return _get_error_div()

    stations = build_station_lookup(data)
    readings_sorted = sorted(
        [(stations.get(reading.get('stationId', ''), {}).get('name', reading.get('stationId', '')),
          reading.get('value', 'N/A')) for reading in readings],
        key=lambda x: x[0].lower()
    )

    def format_value(val):
        return f"{val}{unit}" if unit == '°C' else f"{val} {unit}"

    reading_divs = [_create_reading_div(n, format_value(v), color) for n, v in readings_sorted]
    return _build_grid_content(reading_divs, reading_item.get('timestamp', ''))


def _normalize_unit(api_unit, default_unit):
    """Normalize API unit to display format."""
    lower = api_unit.lower()
    if lower == "percentage":
        return "%"
    if lower in ["deg code", "deg c", "degc"]:
        return "°C"
    return api_unit if api_unit else default_unit


def _convert_to_kmh(speed_val, speed_unit):
    """Convert speed to km/h if needed."""
    if speed_unit.lower() == 'knots':
        try:
            return round(float(speed_val) * 1.852, 1)
        except (ValueError, TypeError):
            return speed_val
    return speed_val


def format_wind_readings(speed_data):
    """
    Format wind readings with speed and description. Handles v2 API response.

    Args:
        speed_data: Wind speed API response

    Returns:
        HTML Div with grid of wind readings
    """
    if not speed_data or 'data' not in speed_data:
        return _get_error_div()

    api_data = speed_data['data']
    if 'readings' not in api_data or not api_data['readings']:
        return _get_error_div()

    reading_item = api_data['readings'][0]
    speed_readings = reading_item.get('data', [])
    if not speed_readings:
        return _get_error_div()

    stations = build_station_lookup(speed_data)
    speed_unit = api_data.get('readingUnit', 'km/h')

    readings_sorted = []
    for reading in speed_readings:
        station_id = reading.get('stationId', '')
        speed_kmh = _convert_to_kmh(reading.get('value', 0), speed_unit)
        name = stations.get(station_id, {}).get('name', station_id)
        readings_sorted.append((name, speed_kmh))
    readings_sorted.sort(key=lambda x: x[0].lower())

    reading_divs = []
    for name, speed_kmh in readings_sorted:
        icon = get_windspeed_icon(speed_kmh)
        desc = get_windspeed_description(speed_kmh)
        display = f"{icon}{speed_kmh} km/h ({desc})"
        reading_divs.append(_create_reading_div(name, display, "#9C27B0"))

    return _build_grid_content(reading_divs, reading_item.get('timestamp', ''))


def _get_station_location(station):
    """Extract lat/lon from station data."""
    if 'labelLocation' in station:
        lat = station['labelLocation'].get('latitude')
        lon = station['labelLocation'].get('longitude')
    else:
        lat = station.get('location', {}).get('latitude')
        lon = station.get('location', {}).get('longitude')
    return lat, lon


def _create_marker(position, bg_color, tooltip_text, marker_id):
    """Create a pin marker with tooltip (no text displayed on map)."""
    lat, lon = position
    # Pin marker with colored circle
    marker_html = (
        f'<div style="width:14px;height:14px;background:{bg_color};'
        f'border-radius:50%;border:2px solid #fff;'
        f'box-shadow:0 2px 5px rgba(0,0,0,0.4);cursor:pointer;"></div>'
    )
    return dl.DivMarker(
        id=marker_id,
        position=[lat, lon],
        iconOptions={
            'className': 'weather-pin',
            'html': marker_html,
            'iconSize': [18, 18],
            'iconAnchor': [9, 9],
        },
        children=[dl.Tooltip(tooltip_text)]
    )


def create_temp_markers(data):
    """Create temperature markers for map (orange pins with tooltip)."""
    markers = []
    if not data or 'data' not in data:
        return markers

    api_data = data['data']
    stations = api_data.get('stations', [])
    readings = {}

    if 'readings' in api_data and api_data['readings']:
        for reading in api_data['readings'][0].get('data', []):
            readings[reading.get('stationId', '')] = reading.get('value', 'N/A')

    for station in stations:
        pos = _get_station_location(station)
        if pos[0] and pos[1]:
            station_id = station.get('id', '')
            name = station.get('name', 'Unknown')
            temp = readings.get(station_id, 'N/A')
            markers.append(_create_marker(
                pos, "#FF9800", f"{name}: {temp}°C", f"temp-{station_id}"
            ))
    return markers


def create_rainfall_markers(data):
    """Create rainfall markers for map (blue pins with tooltip)."""
    markers = []
    if not data or 'data' not in data:
        return markers

    api_data = data['data']
    stations = api_data.get('stations', [])
    readings = {}

    if 'readings' in api_data and api_data['readings']:
        for reading in api_data['readings'][0].get('data', []):
            readings[reading.get('stationId', '')] = reading.get('value', 0)

    for station in stations:
        pos = _get_station_location(station)
        if pos[0] and pos[1]:
            station_id = station.get('id', '')
            name = station.get('name', 'Unknown')
            rainfall = readings.get(station_id, 0)
            markers.append(_create_marker(
                pos, "#2196F3", f"{name}: {rainfall} mm", f"rain-{station_id}"
            ))
    return markers


def create_humidity_markers(data):
    """Create humidity markers for map (cyan pins with tooltip)."""
    markers = []
    if not data or 'data' not in data:
        return markers

    api_data = data['data']
    stations = api_data.get('stations', [])
    readings = {}

    if 'readings' in api_data and api_data['readings']:
        for reading in api_data['readings'][0].get('data', []):
            readings[reading.get('stationId', '')] = reading.get('value', 'N/A')

    for station in stations:
        pos = _get_station_location(station)
        if pos[0] and pos[1]:
            station_id = station.get('id', '')
            name = station.get('name', 'Unknown')
            humidity = readings.get(station_id, 'N/A')
            markers.append(_create_marker(
                pos, "#00BCD4", f"{name}: {humidity}%", f"humid-{station_id}"
            ))
    return markers


def create_wind_markers(data):
    """Create wind speed markers for map (purple pins with tooltip)."""
    markers = []
    if not data or 'data' not in data:
        return markers

    api_data = data['data']
    stations = api_data.get('stations', [])
    speed_unit = api_data.get('readingUnit', 'km/h')
    readings = {}

    if 'readings' in api_data and api_data['readings']:
        for reading in api_data['readings'][0].get('data', []):
            speed_kmh = _convert_to_kmh(reading.get('value', 0), speed_unit)
            readings[reading.get('stationId', '')] = speed_kmh

    for station in stations:
        pos = _get_station_location(station)
        if pos[0] and pos[1]:
            station_id = station.get('id', '')
            name = station.get('name', 'Unknown')
            speed = readings.get(station_id, 0)
            desc = get_windspeed_description(speed)
            markers.append(_create_marker(
                pos, "#9C27B0", f"{name}: {speed} km/h ({desc})", f"wind-{station_id}"
            ))
    return markers


def register_realtime_weather_callbacks(app):
    """
    Register callbacks for realtime weather readings.

    Args:
        app: Dash app instance
    """
    @app.callback(
        Output('temperature-readings-content', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_temperature_readings(n_intervals):
        """Update temperature readings periodically."""
        _ = n_intervals
        data = fetch_realtime_data('air-temperature')
        return format_readings_grid(data, '°C', '#FF9800')

    @app.callback(
        Output('rainfall-readings-content', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_rainfall_readings(n_intervals):
        """Update rainfall readings periodically."""
        _ = n_intervals
        data = fetch_realtime_data('rainfall')
        # Pass default unit, but format_readings_grid will try to extract from API first
        return format_readings_grid(data, 'mm', '#2196F3')

    @app.callback(
        Output('humidity-readings-content', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_humidity_readings(n_intervals):
        """Update humidity readings periodically."""
        _ = n_intervals
        data = fetch_realtime_data('relative-humidity')
        return format_readings_grid(data, '%', '#00BCD4')

    @app.callback(
        Output('wind-readings-content', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_wind_readings(n_intervals):
        """Update wind readings periodically."""
        _ = n_intervals
        speed_data = fetch_realtime_data('wind-speed')
        return format_wind_readings(speed_data)

    @app.callback(
        [Output('active-marker-type', 'data'),
         Output('toggle-temp-markers', 'style'),
         Output('toggle-rainfall-markers', 'style'),
         Output('toggle-humidity-markers', 'style'),
         Output('toggle-wind-markers', 'style')],
        [Input('toggle-temp-markers', 'n_clicks'),
         Input('toggle-rainfall-markers', 'n_clicks'),
         Input('toggle-humidity-markers', 'n_clicks'),
         Input('toggle-wind-markers', 'n_clicks')],
        [State('active-marker-type', 'data')],
        prevent_initial_call=True
    )
    def toggle_marker_type(temp_c, rain_c, humid_c, wind_c, current_store):
        """Handle toggle button clicks - exclusive selection with toggle off."""
        _ = (temp_c, rain_c, humid_c, wind_c)  # Clicks tracked via callback_context
        ctx = callback_context
        if not ctx.triggered:
            return ({'type': None, 'ts': time.time()},) + _get_btn_styles(None)

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        marker_map = {
            'toggle-temp-markers': 'temperature',
            'toggle-rainfall-markers': 'rainfall',
            'toggle-humidity-markers': 'humidity',
            'toggle-wind-markers': 'wind',
        }
        clicked_type = marker_map.get(button_id)

        # Get current active type from store
        current_active = None
        if current_store and isinstance(current_store, dict):
            current_active = current_store.get('type')

        # Toggle off if clicking the same button, otherwise switch to new type
        if clicked_type == current_active:
            new_active = None
        else:
            new_active = clicked_type

        # Include timestamp to force store update and trigger map refresh
        new_store = {'type': new_active, 'ts': time.time()}
        return (new_store,) + _get_btn_styles(new_active)

    @app.callback(
        Output('realtime-weather-markers', 'children'),
        Input('active-marker-type', 'data')
    )
    def update_realtime_map_markers(marker_store):
        """Update map markers immediately when toggle changes."""
        # Extract marker type from store
        marker_type = None
        if marker_store and isinstance(marker_store, dict):
            marker_type = marker_store.get('type')

        if not marker_type:
            return []  # No markers when nothing is active

        # Map marker type to endpoint and color
        marker_config = {
            'temperature': ('air-temperature', create_temp_markers),
            'rainfall': ('rainfall', create_rainfall_markers),
            'humidity': ('relative-humidity', create_humidity_markers),
            'wind': ('wind-speed', create_wind_markers),
        }

        if marker_type in marker_config:
            endpoint, create_fn = marker_config[marker_type]
            data = fetch_realtime_data(endpoint)
            if data:
                return create_fn(data)
        return []


def _get_btn_styles(active_type):
    """Return button styles tuple based on active marker type."""
    colors = {
        'temperature': '#FF9800',
        'rainfall': '#2196F3',
        'humidity': '#00BCD4',
        'wind': '#9C27B0',
    }

    def make_style(btn_type):
        color = colors[btn_type]
        is_active = btn_type == active_type
        return {
            "padding": "4px 10px",
            "borderRadius": "4px",
            "border": f"2px solid {color}",
            "backgroundColor": color if is_active else "transparent",
            "color": "#fff" if is_active else color,
            "cursor": "pointer",
            "fontSize": "11px",
            "fontWeight": "600",
        }

    return (
        make_style('temperature'),
        make_style('rainfall'),
        make_style('humidity'),
        make_style('wind'),
    )
