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


def fetch_flood_alerts():
    """
    Fetch flood alerts from data.gov.sg v2 API.
    Reference: https://api-open.data.gov.sg/v2/real-time/api/weather/flood-alerts

    Returns:
        Dictionary containing flood alert data or None if error
    """
    api_key = os.getenv('DATA_GOV_API')
    if not api_key:
        print("DATA_GOV_API environment variable not set")
        return None

    url = "https://api-open.data.gov.sg/v2/real-time/api/weather/flood-alerts"
    headers = {
        "X-API-Key": api_key,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        print(f"Flood alerts API failed: status={res.status_code}")
    except (requests.exceptions.RequestException, ValueError) as error:
        print(f"Error calling flood alerts API: {error}")
    return None


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


def fetch_lightning_data():
    """
    Fetch lightning observations from data.gov.sg weather API.

    Returns:
        Dictionary containing lightning data or None if error
    """
    api_key = os.getenv('DATA_GOV_API')
    if not api_key:
        print("DATA_GOV_API environment variable not set")
        return None

    url = "https://api-open.data.gov.sg/v2/real-time/api/weather?api=lightning"
    headers = {
        "X-API-Key": api_key,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        print(f"Lightning API failed: status={res.status_code}")
    except (requests.exceptions.RequestException, ValueError) as error:
        print(f"Error calling lightning API: {error}")
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


def _create_lightning_marker(lat, lon, reading_info, marker_index):
    """Create a single lightning marker."""
    marker_html = (
        '<div style="width:20px;height:20px;background:#FFD700;'
        'border-radius:3px;border:2px solid #fff;'
        'box-shadow:0 2px 8px rgba(255,215,0,0.6);'
        'cursor:pointer;display:flex;align-items:center;'
        'justify-content:center;font-size:14px;color:#fff;'
        'font-weight:bold;">⚡</div>'
    )
    text = reading_info.get('text', 'Lightning')
    lightning_type = reading_info.get('type', 'C')
    datetime_str = reading_info.get('datetime', '')
    tooltip_text = f"{text} ({lightning_type})\n{datetime_str}"
    marker_id = f"lightning-{lat}-{lon}-{marker_index}"

    return dl.DivMarker(
        id=marker_id,
        position=[lat, lon],
        iconOptions={
            'className': 'lightning-pin',
            'html': marker_html,
            'iconSize': [24, 24],
            'iconAnchor': [12, 12],
        },
        children=[dl.Tooltip(tooltip_text)]
    )


def _process_lightning_reading(reading, marker_index):
    """Process a single lightning reading and return marker if valid."""
    location = reading.get('location', {})
    # Handle typo in API: 'longtitude' instead of 'longitude'
    lat_str = location.get('latitude')
    lon_str = location.get('longtitude') or location.get('longitude')

    if not lat_str or not lon_str:
        return None, marker_index

    try:
        lat = float(lat_str)
        lon = float(lon_str)
        reading_info = {
            'text': reading.get('text', 'Lightning'),
            'type': reading.get('type', 'C'),
            'datetime': reading.get('datetime', '')
        }

        marker = _create_lightning_marker(lat, lon, reading_info, marker_index)
        return marker, marker_index + 1
    except (ValueError, TypeError):
        return None, marker_index


def create_lightning_markers(data):
    """Create lightning markers for map (yellow/white flash icons)."""
    markers = []
    if not data or 'data' not in data:
        return markers

    records = data['data'].get('records', [])
    if not records:
        return markers

    marker_index = 0
    # Extract readings from all records
    for record in records:
        item = record.get('item', {})
        readings = item.get('readings', [])
        if not readings:
            continue

        for reading in readings:
            marker, marker_index = _process_lightning_reading(reading, marker_index)
            if marker:
                markers.append(marker)

    return markers


def _create_single_flood_marker(lat, lon, description, instruction, marker_index):
    """Create a single flood marker."""
    # Combine description and instruction for tooltip
    if description and instruction:
        tooltip_text = f"{description} {instruction}"
    elif description:
        tooltip_text = description
    elif instruction:
        tooltip_text = instruction
    else:
        tooltip_text = "Flood alert"

    # Create flood marker (red circle with wave icon)
    marker_html = (
        '<div style="width:20px;height:20px;background:#ff4444;'
        'border-radius:50%;border:2px solid #fff;'
        'box-shadow:0 2px 8px rgba(255,68,68,0.6);'
        'cursor:pointer;display:flex;align-items:center;'
        'justify-content:center;font-size:14px;color:#fff;'
        'font-weight:bold;">🌊</div>'
    )
    marker_id = f"flood-{lat}-{lon}-{marker_index}"

    return dl.DivMarker(
        id=marker_id,
        position=[lat, lon],
        iconOptions={
            'className': 'flood-pin',
            'html': marker_html,
            'iconSize': [24, 24],
            'iconAnchor': [12, 12],
        },
        children=[dl.Tooltip(tooltip_text)]
    )


def create_flood_markers(data):
    """Create flood markers for map from circle coordinates."""
    markers = []
    if not data or 'data' not in data:
        return markers

    records = data['data'].get('records', [])
    if not records:
        return markers

    # Extract first record
    first_record = records[0]
    item = first_record.get('item', {})
    readings = item.get('readings', [])

    if not readings:
        return markers

    marker_index = 0
    for reading in readings:
        area = reading.get('area', {})
        circle = area.get('circle', [])

        # Circle format: [latitude, longitude, radius]
        if circle and len(circle) >= 2:
            try:
                lat = float(circle[0])
                lon = float(circle[1])
                description = reading.get('description', 'Flood alert')
                instruction = reading.get('instruction', '')

                markers.append(_create_single_flood_marker(
                    lat, lon, description, instruction, marker_index
                ))
                marker_index += 1
            except (ValueError, TypeError):
                continue

    return markers


def format_lightning_indicator(data):
    """Format lightning status indicator."""
    if not data or 'data' not in data:
        return html.Div(
            [
                html.Span("⚡", style={"fontSize": "16px"}),
                html.Span("Error", style={"color": "#ff6b6b"})
            ],
            style={
                "display": "inline-flex",
                "alignItems": "center",
                "gap": "8px",
                "padding": "6px 12px",
                "borderRadius": "6px",
                "fontSize": "12px",
                "fontWeight": "600",
                "backgroundColor": "#3a4a5a",
            }
        )

    records = data['data'].get('records', [])
    if not records:
        return html.Div(
            [
                html.Span("⚡", style={"fontSize": "16px"}),
                html.Span("No lightning detected", style={"color": "#888"})
            ],
            style={
                "display": "inline-flex",
                "alignItems": "center",
                "gap": "8px",
                "padding": "6px 12px",
                "borderRadius": "6px",
                "fontSize": "12px",
                "fontWeight": "600",
                "backgroundColor": "#3a4a5a",
            }
        )

    # Check if any record has readings
    has_readings = False
    for record in records:
        item = record.get('item', {})
        readings = item.get('readings', [])
        if readings:
            has_readings = True
            break

    if has_readings:
        return html.Div(
            [
                html.Span("⚡", style={"fontSize": "16px"}),
                html.Span("Lightning detected", style={"color": "#FFD700"})
            ],
            style={
                "display": "inline-flex",
                "alignItems": "center",
                "gap": "8px",
                "padding": "6px 12px",
                "borderRadius": "6px",
                "fontSize": "12px",
                "fontWeight": "600",
                "backgroundColor": "#3a4a5a",
                "border": "1px solid #FFD700",
            }
        )

    return html.Div(
        [
            html.Span("⚡", style={"fontSize": "16px"}),
            html.Span("No lightning detected", style={"color": "#888"})
        ],
        style={
            "display": "inline-flex",
            "alignItems": "center",
            "gap": "8px",
            "padding": "6px 12px",
            "borderRadius": "6px",
            "fontSize": "12px",
            "fontWeight": "600",
            "backgroundColor": "#3a4a5a",
        }
    )


def format_flood_indicator(data):
    """Format flood status indicator from v2 API response."""
    if not data or 'data' not in data:
        return html.Div(
            [
                html.Span("🌊", style={"fontSize": "16px"}),
                html.Span("No flooding notice at the moment", style={"color": "#888"})
            ],
            style={
                "display": "inline-flex",
                "alignItems": "center",
                "gap": "8px",
                "padding": "6px 12px",
                "borderRadius": "6px",
                "fontSize": "12px",
                "fontWeight": "600",
                "backgroundColor": "#3a4a5a",
            }
        )

    records = data['data'].get('records', [])
    if not records:
        return html.Div(
            [
                html.Span("🌊", style={"fontSize": "16px"}),
                html.Span("No flooding notice at the moment", style={"color": "#888"})
            ],
            style={
                "display": "inline-flex",
                "alignItems": "center",
                "gap": "8px",
                "padding": "6px 12px",
                "borderRadius": "6px",
                "fontSize": "12px",
                "fontWeight": "600",
                "backgroundColor": "#3a4a5a",
            }
        )

    # Extract first record
    first_record = records[0]
    item = first_record.get('item', {})
    readings = item.get('readings', [])

    if not readings:
        return html.Div(
            [
                html.Span("🌊", style={"fontSize": "16px"}),
                html.Span("No flooding notice at the moment", style={"color": "#888"})
            ],
            style={
                "display": "inline-flex",
                "alignItems": "center",
                "gap": "8px",
                "padding": "6px 12px",
                "borderRadius": "6px",
                "fontSize": "12px",
                "fontWeight": "600",
                "backgroundColor": "#3a4a5a",
            }
        )

    # Combine description and instruction for each reading
    alert_messages = []
    for reading in readings:
        description = reading.get('description', '')
        instruction = reading.get('instruction', '')

        # Combine description and instruction as a sentence
        if description and instruction:
            alert_text = f"{description} {instruction}"
        elif description:
            alert_text = description
        elif instruction:
            alert_text = instruction
        else:
            alert_text = "Flood alert"

        alert_messages.append(alert_text)

    if not alert_messages:
        return html.Div(
            [
                html.Span("🌊", style={"fontSize": "16px"}),
                html.Span("No flooding notice at the moment", style={"color": "#888"})
            ],
            style={
                "display": "inline-flex",
                "alignItems": "center",
                "gap": "8px",
                "padding": "6px 12px",
                "borderRadius": "6px",
                "fontSize": "12px",
                "fontWeight": "600",
                "backgroundColor": "#3a4a5a",
            }
        )

    # Show flood alert (limit to first alert for indicator)
    alert_text = alert_messages[0]
    if len(alert_messages) > 1:
        alert_text += f" (+{len(alert_messages) - 1} more)"

    return html.Div(
        [
            html.Span("🌊", style={"fontSize": "16px"}),
            html.Span(alert_text, style={"color": "#ff6b6b"})
        ],
        style={
            "display": "inline-flex",
            "alignItems": "center",
            "gap": "8px",
            "padding": "6px 12px",
            "borderRadius": "6px",
            "fontSize": "12px",
            "fontWeight": "600",
            "backgroundColor": "#3a4a5a",
            "border": "1px solid #ff6b6b",
        }
    )


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

    @app.callback(
        Output('lightning-indicator', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_lightning_indicator(n_intervals):
        """Update lightning status indicator periodically."""
        _ = n_intervals
        data = fetch_lightning_data()
        return format_lightning_indicator(data)

    @app.callback(
        Output('lightning-markers', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_lightning_markers(n_intervals):
        """Update lightning markers on map periodically."""
        _ = n_intervals
        data = fetch_lightning_data()
        if data:
            return create_lightning_markers(data)
        return []

    @app.callback(
        Output('flood-indicator', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_flood_indicator(n_intervals):
        """Update flood status indicator periodically."""
        _ = n_intervals
        data = fetch_flood_alerts()
        return format_flood_indicator(data)

    @app.callback(
        Output('flood-markers', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_flood_markers(n_intervals):
        """Update flood markers on map periodically."""
        _ = n_intervals
        data = fetch_flood_alerts()
        if data:
            return create_flood_markers(data)
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
