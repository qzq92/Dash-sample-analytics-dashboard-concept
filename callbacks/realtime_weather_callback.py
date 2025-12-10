"""
Callback functions for handling realtime weather readings from data.gov.sg v2 API.
References:
- Air Temperature: https://api-open.data.gov.sg/v2/real-time/api/air-temperature
- Rainfall: https://api-open.data.gov.sg/v2/real-time/api/rainfall
- Relative Humidity: https://api-open.data.gov.sg/v2/real-time/api/relative-humidity
- Wind Speed: https://api-open.data.gov.sg/v2/real-time/api/wind-speed

Uses ThreadPoolExecutor for async API fetching to improve performance.
"""
import time
from dash import Input, Output, State, html, callback_context
import dash_leaflet as dl
from conf.windspeed_icon import get_windspeed_icon, get_windspeed_description, WINDSPEED_THRESHOLDS
from utils.async_fetcher import fetch_url, fetch_async, get_default_headers

# API URLs
API_BASE = "https://api-open.data.gov.sg/v2/real-time/api"
FLOOD_ALERTS_URL = f"{API_BASE}/weather/flood-alerts"
LIGHTNING_URL = f"{API_BASE}/weather?api=lightning"
SUPPORTED_ENDPOINTS = ['air-temperature', 'rainfall', 'relative-humidity', 'wind-speed']


def fetch_flood_alerts():
    """
    Fetch flood alerts from data.gov.sg v2 API (threaded).
    Reference: https://api-open.data.gov.sg/v2/real-time/api/weather/flood-alerts

    Returns:
        Dictionary containing flood alert data or None if error
    """
    return fetch_url(FLOOD_ALERTS_URL, get_default_headers())


def fetch_flood_alerts_async():
    """
    Fetch flood alerts asynchronously (returns Future).
    Call .result() to get the data when needed.
    """
    return fetch_async(FLOOD_ALERTS_URL, get_default_headers())


def fetch_realtime_data(endpoint):
    """
    Fetch realtime weather data from data.gov.sg v2 API.

    Args:
        endpoint: API endpoint (e.g., 'air-temperature', 'rainfall')

    Returns:
        Dictionary containing weather data or None if error
    """
    if endpoint not in SUPPORTED_ENDPOINTS:
        print(f"Unsupported endpoint: {endpoint}")
        return None

    url = f"{API_BASE}/{endpoint}"
    return fetch_url(url, get_default_headers())


def fetch_realtime_data_async(endpoint):
    """
    Fetch realtime weather data asynchronously (returns Future).
    Call .result() to get the data when needed.
    """
    if endpoint not in SUPPORTED_ENDPOINTS:
        print(f"Unsupported endpoint: {endpoint}")
        return None

    url = f"{API_BASE}/{endpoint}"
    return fetch_async(url, get_default_headers())


def fetch_lightning_data():
    """
    Fetch lightning observations from data.gov.sg weather API.

    Returns:
        Dictionary containing lightning data or None if error
    """
    return fetch_url(LIGHTNING_URL, get_default_headers())


def fetch_lightning_data_async():
    """
    Fetch lightning data asynchronously (returns Future).
    Call .result() to get the data when needed.
    """
    return fetch_async(LIGHTNING_URL, get_default_headers())


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
    Format readings data to show average value. Handles v2 API response structure.

    Args:
        data: API response data
        unit: Unit of measurement (e.g., '°C', 'mm', '%')
        color: Text color for values

    Returns:
        HTML Div with average value display
    """
    if not data or 'data' not in data:
        return html.Div(
            html.Span("Error loading data", style={"color": "#ff6b6b", "fontSize": "12px"}),
            style={
                "padding": "6px 8px",
                "backgroundColor": "#3a4a5a",
                "borderRadius": "4px",
            }
        )

    api_data = data['data']
    if 'readings' not in api_data or not api_data['readings']:
        return html.Div(
            html.Span("No data available", style={"color": "#888", "fontSize": "12px"}),
            style={
                "padding": "6px 8px",
                "backgroundColor": "#3a4a5a",
                "borderRadius": "4px",
            }
        )

    # Extract unit from API response
    api_unit = api_data.get('readingUnit', '')
    if api_unit:
        unit = _normalize_unit(api_unit, unit)

    reading_item = api_data['readings'][0]
    readings = reading_item.get('data', [])
    if not readings:
        return html.Div(
            html.Span("No readings available", style={"color": "#888", "fontSize": "12px"}),
            style={
                "padding": "6px 8px",
                "backgroundColor": "#3a4a5a",
                "borderRadius": "4px",
            }
        )

    # Calculate average
    values = []
    for reading in readings:
        val = reading.get('value')
        if val is not None:
            try:
                values.append(float(val))
            except (ValueError, TypeError):
                pass

    if not values:
        return html.Div(
            html.Span("No valid readings", style={"color": "#888", "fontSize": "12px"}),
            style={
                "padding": "6px 8px",
                "backgroundColor": "#3a4a5a",
                "borderRadius": "4px",
            }
        )

    avg_value = sum(values) / len(values)
    formatted_avg = f"{avg_value:.1f}{unit}" if unit == '°C' else f"{avg_value:.1f} {unit}"

    return html.Div(
        [
            html.Span(formatted_avg, style={
                "fontSize": "14px",
                "fontWeight": "600",
                "color": color,
            }),
        ],
        style={
            "padding": "6px 8px",
            "backgroundColor": "#3a4a5a",
            "borderRadius": "4px",
            "borderLeft": f"3px solid {color}",
        }
    )


def format_sensor_values_grid(data, unit, color):
    """
    Format readings data as a grid for sensor values display (used in toggle sections).
    Handles v2 API response structure.

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


def _create_wind_speed_legend():
    """
    Create a legend showing wind speed icons and their descriptions.
    
    Returns:
        HTML Div containing the wind speed legend
    """
    # Group thresholds by icon to avoid duplicates
    icon_map = {}
    for min_speed, max_speed, icon, description in WINDSPEED_THRESHOLDS:
        if icon not in icon_map:
            icon_map[icon] = []
        icon_map[icon].append((min_speed, max_speed, description))
    
    legend_items = []
    for icon, ranges in sorted(icon_map.items()):
        # Get unique descriptions for this icon
        descriptions = list({desc for _, _, desc in ranges})
        desc_text = ", ".join(descriptions)
        legend_items.append(
            html.Div(
                [
                    html.Span(icon, style={"fontSize": "20px", "marginRight": "10px"}),
                    html.Span(desc_text, style={"fontSize": "13px", "color": "#ddd", "fontWeight": "500"})
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "padding": "8px 12px",
                    "marginBottom": "6px",
                    "backgroundColor": "#2a3a4a",
                    "borderRadius": "4px",
                }
            )
        )
    
    return html.Div(
        [
            html.Div(
                "Wind Speed Legend",
                style={
                    "fontSize": "16px",
                    "fontWeight": "700",
                    "color": "#4CAF50",
                    "marginBottom": "12px",
                    "textAlign": "center",
                    "paddingBottom": "8px",
                    "borderBottom": "2px solid #4CAF50",
                }
            ),
            html.Div(
                legend_items,
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "4px",
                }
            )
        ],
        style={
            "padding": "16px",
            "backgroundColor": "#4a5a6a",
            "borderRadius": "8px",
            "border": "2px solid #4CAF50",
            "boxShadow": "0 2px 8px rgba(76, 175, 80, 0.2)",
        }
    )


def format_wind_readings(speed_data):
    """
    Format wind readings to show average value. Handles v2 API response.

    Args:
        speed_data: Wind speed API response

    Returns:
        HTML Div with average wind speed display
    """
    if not speed_data or 'data' not in speed_data:
        return html.Div(
            html.Span("Error loading data", style={"color": "#ff6b6b", "fontSize": "12px"}),
            style={
                "padding": "6px 8px",
                "backgroundColor": "#3a4a5a",
                "borderRadius": "4px",
            }
        )

    api_data = speed_data['data']
    if 'readings' not in api_data or not api_data['readings']:
        return html.Div(
            html.Span("No data available", style={"color": "#888", "fontSize": "12px"}),
            style={
                "padding": "6px 8px",
                "backgroundColor": "#3a4a5a",
                "borderRadius": "4px",
            }
        )

    reading_item = api_data['readings'][0]
    speed_readings = reading_item.get('data', [])
    if not speed_readings:
        return html.Div(
            html.Span("No readings available", style={"color": "#888", "fontSize": "12px"}),
            style={
                "padding": "6px 8px",
                "backgroundColor": "#3a4a5a",
                "borderRadius": "4px",
            }
        )

    speed_unit = api_data.get('readingUnit', 'km/h')

    # Calculate average
    speeds = []
    for reading in speed_readings:
        speed_kmh = _convert_to_kmh(reading.get('value', 0), speed_unit)
        try:
            speeds.append(float(speed_kmh))
        except (ValueError, TypeError):
            pass

    if not speeds:
        return html.Div(
            html.Span("No valid readings", style={"color": "#888", "fontSize": "12px"}),
            style={
                "padding": "6px 8px",
                "backgroundColor": "#3a4a5a",
                "borderRadius": "4px",
            }
        )

    avg_speed = sum(speeds) / len(speeds)
    icon = get_windspeed_icon(avg_speed)
    formatted_avg = f"{icon} {avg_speed:.1f} km/h"

    return html.Div(
        [
            html.Span(formatted_avg, style={
                "fontSize": "14px",
                "fontWeight": "600",
                "color": "#4CAF50",
            }),
        ],
        style={
            "padding": "6px 8px",
            "backgroundColor": "#3a4a5a",
            "borderRadius": "4px",
            "borderLeft": "3px solid #4CAF50",
        }
    )


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


def _create_textbox_marker(position, name, value, color, marker_id):
    """Create a textbox marker showing name and value."""
    lat, lon = position
    # Textbox marker with name and value
    marker_html = (
        f'<div style="background:{color};color:#fff;padding:4px 8px;'
        f'border-radius:4px;border:2px solid #fff;'
        f'box-shadow:0 2px 8px rgba(0,0,0,0.3);'
        f'font-size:11px;font-weight:600;white-space:nowrap;'
        f'text-align:center;">{name}<br/>{value}</div>'
    )
    return dl.DivMarker(
        id=marker_id,
        position=[lat, lon],
        iconOptions={
            'className': 'sensor-textbox',
            'html': marker_html,
            'iconSize': [80, 40],
            'iconAnchor': [40, 20],
        }
    )


def create_sensor_textbox_markers(data, sensor_type, unit, color):
    """Create textbox markers for sensor locations showing name and value."""
    markers = []
    if not data or 'data' not in data:
        return markers

    api_data = data['data']
    stations = api_data.get('stations', [])
    readings = {}

    if 'readings' in api_data and api_data['readings']:
        reading_item = api_data['readings'][0]
        for reading in reading_item.get('data', []):
            station_id = reading.get('stationId', '')
            value = reading.get('value', 'N/A')
            if value != 'N/A':
                if unit == '°C':
                    formatted_value = f"{value}{unit}"
                else:
                    formatted_value = f"{value} {unit}"
            else:
                formatted_value = 'N/A'
            readings[station_id] = formatted_value

    for station in stations:
        pos = _get_station_location(station)
        if pos[0] and pos[1]:
            station_id = station.get('id', '')
            name = station.get('name', 'Unknown')
            value = readings.get(station_id, 'N/A')
            marker_id = f"sensor-{sensor_type}-{station_id}"
            markers.append(_create_textbox_marker(
                pos, name, value, color, marker_id
            ))
    return markers


def create_wind_textbox_markers(data):
    """Create wind speed textbox markers for map."""
    markers = []
    if not data or 'data' not in data:
        return markers

    api_data = data['data']
    stations = api_data.get('stations', [])
    readings = {}
    speed_unit = api_data.get('readingUnit', 'km/h')

    if 'readings' in api_data and api_data['readings']:
        reading_item = api_data['readings'][0]
        for reading in reading_item.get('data', []):
            station_id = reading.get('stationId', '')
            speed_kmh = _convert_to_kmh(reading.get('value', 0), speed_unit)
            icon = get_windspeed_icon(speed_kmh)
            formatted_value = f"{icon} {speed_kmh} km/h"
            readings[station_id] = formatted_value

    for station in stations:
        pos = _get_station_location(station)
        if pos[0] and pos[1]:
            station_id = station.get('id', '')
            name = station.get('name', 'Unknown')
            value = readings.get(station_id, 'N/A')
            marker_id = f"sensor-wind-{station_id}"
            markers.append(_create_textbox_marker(
                pos, name, value, "#4CAF50", marker_id
            ))
    return markers


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
                pos, "#4CAF50", f"{name}: {speed} km/h ({desc})", f"wind-{station_id}"
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
    """
    Format lightning indicator with each alert as a sub-div (mimics metrics design).
    Returns HTML content for the lightning indicator.
    """
    if not data or 'data' not in data:
        return html.Div(
            [
                html.Div(
                    [
                        html.Span("⚡ Error loading lightning data", style={
                            "fontSize": "11px",
                            "color": "#ff6b6b",
                            "fontWeight": "600",
                        }),
                    ],
                    style={
                        "padding": "6px 8px",
                        "backgroundColor": "#3a4a5a",
                        "borderRadius": "4px",
                        "borderLeft": "3px solid #ff6b6b",
                    }
                )
            ]
        )

    records = data['data'].get('records', [])
    if not records:
        return html.Div(
            [
                html.Div(
                    [
                        html.Span("⚡ No lightning detected", style={
                            "fontSize": "11px",
                            "color": "#888",
                            "fontWeight": "600",
                        }),
                    ],
                    style={
                        "padding": "6px 8px",
                        "backgroundColor": "#3a4a5a",
                        "borderRadius": "4px",
                        "borderLeft": "3px solid #888",
                    }
                )
            ]
        )

    # Collect all lightning readings
    lightning_readings = []
    for record in records:
        item = record.get('item', {})
        readings = item.get('readings', [])
        for reading in readings:
            text = reading.get('text', 'Lightning')
            lightning_type = reading.get('type', 'C')
            datetime_str = reading.get('datetime', '')
            location = reading.get('location', {})
            lat = location.get('latitude', '')
            lon = location.get('longtitude') or location.get('longitude', '')
            
            lightning_readings.append({
                'text': text,
                'type': lightning_type,
                'datetime': datetime_str,
                'location': f"Lat: {lat}, Lon: {lon}" if lat and lon else "Location unknown"
            })

    if not lightning_readings:
        return html.Div(
            [
                html.Div(
                    [
                        html.Span("⚡ No lightning detected", style={
                            "fontSize": "11px",
                            "color": "#888",
                            "fontWeight": "600",
                        }),
                    ],
                    style={
                        "padding": "6px 8px",
                        "backgroundColor": "#3a4a5a",
                        "borderRadius": "4px",
                        "borderLeft": "3px solid #888",
                    }
                )
            ]
        )

    # Create sub-divs for each lightning alert (mimics reading items)
    alert_divs = []
    for reading in lightning_readings:
        alert_divs.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(f"⚡ {reading['text']}", style={
                                "fontSize": "11px",
                                "color": "#FFD700",
                                "fontWeight": "600",
                            }),
                        ],
                        style={"marginBottom": "2px"}
                    ),
                    html.Div(
                        [
                            html.Span(f"Type: {reading['type']}", style={
                                "fontSize": "11px",
                                "color": "#ccc",
                            }),
                            html.Span(f" | {reading['datetime']}", style={
                                "fontSize": "11px",
                                "color": "#888",
                            }),
                        ],
                        style={"marginLeft": "4px"}
                    ),
                    html.Div(
                        html.Span(reading['location'], style={
                            "fontSize": "10px",
                            "color": "#888",
                            "marginLeft": "4px",
                        }),
                    ),
                ],
                style={
                    "padding": "6px 8px",
                    "backgroundColor": "#3a4a5a",
                    "borderRadius": "4px",
                    "marginBottom": "4px",
                    "borderLeft": "3px solid #FFD700",
                }
            )
        )

    return html.Div(alert_divs)


def format_flood_indicator(data):
    """
    Format flood indicator with each alert as a sub-div (mimics metrics design).
    Returns HTML content for the flood indicator.
    """
    if not data or 'data' not in data:
        return html.Div(
            [
                html.Div(
                    [
                        html.Span("🌊 No flooding notice at the moment", style={
                            "fontSize": "11px",
                            "color": "#888",
                            "fontWeight": "600",
                        }),
                    ],
                    style={
                        "padding": "6px 8px",
                        "backgroundColor": "#3a4a5a",
                        "borderRadius": "4px",
                        "borderLeft": "3px solid #888",
                    }
                )
            ]
        )

    records = data['data'].get('records', [])
    if not records:
        return html.Div(
            [
                html.Div(
                    [
                        html.Span("🌊 No flooding notice at the moment", style={
                            "fontSize": "11px",
                            "color": "#888",
                            "fontWeight": "600",
                        }),
                    ],
                    style={
                        "padding": "6px 8px",
                        "backgroundColor": "#3a4a5a",
                        "borderRadius": "4px",
                        "borderLeft": "3px solid #888",
                    }
                )
            ]
        )

    # Extract first record
    first_record = records[0]
    item = first_record.get('item', {})
    readings = item.get('readings', [])

    if not readings:
        return html.Div(
            [
                html.Div(
                    [
                        html.Span("🌊 No flooding notice at the moment", style={
                            "fontSize": "11px",
                            "color": "#888",
                            "fontWeight": "600",
                        }),
                    ],
                    style={
                        "padding": "6px 8px",
                        "backgroundColor": "#3a4a5a",
                        "borderRadius": "4px",
                        "borderLeft": "3px solid #888",
                    }
                )
            ]
        )

    # Collect all flood alerts
    flood_alerts = []
    for reading in readings:
        description = reading.get('description', '')
        instruction = reading.get('instruction', '')
        area = reading.get('area', {})
        circle = area.get('circle', {})
        center = circle.get('center', {})
        lat = center.get('latitude', '')
        lon = center.get('longitude', '')

        # Combine description and instruction as a sentence
        if description and instruction:
            alert_text = f"{description} {instruction}"
        elif description:
            alert_text = description
        elif instruction:
            alert_text = instruction
        else:
            alert_text = "Flood alert"

        location = f"Lat: {lat}, Lon: {lon}" if lat and lon else "Location unknown"
        flood_alerts.append({
            'text': alert_text,
            'location': location
        })

    if not flood_alerts:
        return html.Div(
            [
                html.Div(
                    [
                        html.Span("🌊 No flooding notice at the moment", style={
                            "fontSize": "11px",
                            "color": "#888",
                            "fontWeight": "600",
                        }),
                    ],
                    style={
                        "padding": "6px 8px",
                        "backgroundColor": "#3a4a5a",
                        "borderRadius": "4px",
                        "borderLeft": "3px solid #888",
                    }
                )
            ]
        )

    # Create sub-divs for each flood alert (mimics reading items)
    alert_divs = []
    for alert in flood_alerts:
        alert_divs.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(f"🌊 {alert['text']}", style={
                                "fontSize": "11px",
                                "color": "#ff6b6b",
                                "fontWeight": "600",
                            }),
                        ],
                        style={"marginBottom": "2px"}
                    ),
                    html.Div(
                        html.Span(alert['location'], style={
                            "fontSize": "10px",
                            "color": "#888",
                            "marginLeft": "4px",
                        }),
                    ),
                ],
                style={
                    "padding": "6px 8px",
                    "backgroundColor": "#3a4a5a",
                    "borderRadius": "4px",
                    "marginBottom": "4px",
                    "borderLeft": "3px solid #ff6b6b",
                }
            )
        )

    return html.Div(alert_divs)


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
        Output('wind-speed-legend', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_wind_speed_legend(n_intervals):
        """Update wind speed legend periodically."""
        _ = n_intervals
        return _create_wind_speed_legend()

    # Toggle callbacks for sensor values sections
    @app.callback(
        Output('temp-sensor-values', 'style'),
        Input('toggle-temp-readings', 'n_clicks'),
        prevent_initial_call=True
    )
    def toggle_temp_sensor_values(n_clicks):
        """Toggle temperature sensor values section visibility."""
        if n_clicks and n_clicks % 2 == 1:
            return {"display": "block", "backgroundColor": "#3a4a5a",
                    "borderRadius": "5px", "padding": "10px", "maxHeight": "200px", "overflowY": "auto"}
        return {"display": "none"}

    @app.callback(
        Output('rainfall-sensor-values', 'style'),
        Input('toggle-rainfall-readings', 'n_clicks'),
        prevent_initial_call=True
    )
    def toggle_rainfall_sensor_values(n_clicks):
        """Toggle rainfall sensor values section visibility."""
        if n_clicks and n_clicks % 2 == 1:
            return {"display": "block", "backgroundColor": "#3a4a5a",
                    "borderRadius": "5px", "padding": "10px", "maxHeight": "200px", "overflowY": "auto"}
        return {"display": "none"}

    @app.callback(
        Output('humidity-sensor-values', 'style'),
        Input('toggle-humidity-readings', 'n_clicks'),
        prevent_initial_call=True
    )
    def toggle_humidity_sensor_values(n_clicks):
        """Toggle humidity sensor values section visibility."""
        if n_clicks and n_clicks % 2 == 1:
            return {"display": "block", "backgroundColor": "#3a4a5a",
                    "borderRadius": "5px", "padding": "10px", "maxHeight": "200px", "overflowY": "auto"}
        return {"display": "none"}

    @app.callback(
        Output('wind-sensor-values', 'style'),
        Input('toggle-wind-readings', 'n_clicks'),
        prevent_initial_call=True
    )
    def toggle_wind_sensor_values(n_clicks):
        """Toggle wind sensor values section visibility."""
        if n_clicks and n_clicks % 2 == 1:
            return {"display": "block", "backgroundColor": "#3a4a5a",
                    "borderRadius": "5px", "padding": "10px", "maxHeight": "200px", "overflowY": "auto"}
        return {"display": "none"}

    @app.callback(
        Output('sensor-markers', 'children'),
        [Input('toggle-temp-readings', 'n_clicks'),
         Input('toggle-rainfall-readings', 'n_clicks'),
         Input('toggle-humidity-readings', 'n_clicks'),
         Input('toggle-wind-readings', 'n_clicks')],
        prevent_initial_call=True
    )
    def update_sensor_markers(_temp_clicks, _rain_clicks, _humid_clicks, _wind_clicks):
        """Update sensor markers based on which toggle is active."""
        ctx = callback_context
        if not ctx.triggered:
            return []

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        n_clicks = ctx.triggered[0]['value']

        # Only show markers if the button was clicked an odd number of times (toggled on)
        if n_clicks and n_clicks % 2 == 1:
            if button_id == 'toggle-temp-readings':
                data = fetch_realtime_data('air-temperature')
                return create_sensor_textbox_markers(data, 'air-temperature', '°C', '#FF9800')
            if button_id == 'toggle-rainfall-readings':
                data = fetch_realtime_data('rainfall')
                return create_sensor_textbox_markers(data, 'rainfall', 'mm', '#2196F3')
            if button_id == 'toggle-humidity-readings':
                data = fetch_realtime_data('relative-humidity')
                return create_sensor_textbox_markers(data, 'relative-humidity', '%', '#00BCD4')
            if button_id == 'toggle-wind-readings':
                speed_data = fetch_realtime_data('wind-speed')
                return create_wind_textbox_markers(speed_data)

        # If toggled off, clear markers
        return []

    # Callbacks to populate sensor values when sections are visible
    @app.callback(
        Output('temp-sensor-content', 'children'),
        [Input('temp-sensor-values', 'style'),
         Input('interval-component', 'n_intervals')]
    )
    def update_temp_sensor_content(style, _n_intervals):
        """Update temperature sensor values when section is visible."""
        if style and style.get('display') == 'none':
            return html.P("Loading...", style={"color": "#999", "fontSize": "12px", "textAlign": "center"})
        data = fetch_realtime_data('air-temperature')
        return format_sensor_values_grid(data, '°C', '#FF9800')

    @app.callback(
        Output('rainfall-sensor-content', 'children'),
        [Input('rainfall-sensor-values', 'style'),
         Input('interval-component', 'n_intervals')]
    )
    def update_rainfall_sensor_content(style, _n_intervals):
        """Update rainfall sensor values when section is visible."""
        if style and style.get('display') == 'none':
            return html.P("Loading...", style={"color": "#999", "fontSize": "12px", "textAlign": "center"})
        data = fetch_realtime_data('rainfall')
        return format_sensor_values_grid(data, 'mm', '#2196F3')

    @app.callback(
        Output('humidity-sensor-content', 'children'),
        [Input('humidity-sensor-values', 'style'),
         Input('interval-component', 'n_intervals')]
    )
    def update_humidity_sensor_content(style, _n_intervals):
        """Update humidity sensor values when section is visible."""
        if style and style.get('display') == 'none':
            return html.P("Loading...", style={"color": "#999", "fontSize": "12px", "textAlign": "center"})
        data = fetch_realtime_data('relative-humidity')
        return format_sensor_values_grid(data, '%', '#00BCD4')

    @app.callback(
        Output('wind-sensor-content', 'children'),
        [Input('wind-sensor-values', 'style'),
         Input('interval-component', 'n_intervals')]
    )
    def update_wind_sensor_content(style, _n_intervals):
        """Update wind sensor values when section is visible."""
        if style and style.get('display') == 'none':
            return html.P("Loading...", style={"color": "#999", "fontSize": "12px", "textAlign": "center"})
        speed_data = fetch_realtime_data('wind-speed')
        if not speed_data or 'data' not in speed_data:
            return _get_error_div()

        api_data = speed_data['data']
        if 'readings' not in api_data or not api_data['readings']:
            return _get_error_div()

        reading_item = api_data['readings'][0]
        speed_readings = reading_item.get('data', [])
        if not speed_readings:
            return _get_error_div()

        _ = build_station_lookup(speed_data)  # For station name lookup
        speed_unit = api_data.get('readingUnit', 'km/h')

        readings_sorted = []
        for reading in speed_readings:
            station_id = reading.get('stationId', '')
            speed_kmh = _convert_to_kmh(reading.get('value', 0), speed_unit)
            name = station_id  # Simplified for sensor values
            readings_sorted.append((name, speed_kmh))
        readings_sorted.sort(key=lambda x: x[0].lower())

        reading_divs = []
        for name, speed_kmh in readings_sorted:
            icon = get_windspeed_icon(speed_kmh)
            display = f"{icon} {speed_kmh} km/h"
            reading_divs.append(_create_reading_div(name, display, "#4CAF50"))

        return _build_grid_content(reading_divs, reading_item.get('timestamp', ''))

    @app.callback(
        [Output('readings-section', 'style'),
         Output('toggle-readings', 'children')],
        Input('toggle-readings', 'n_clicks'),
        State('readings-toggle-state', 'data')
    )
    def toggle_readings_section(n_clicks, current_state):
        """Toggle visibility of readings section."""
        if n_clicks is None or n_clicks == 0:
            return {'display': 'none'}, "📊 Show Readings"
        
        is_visible = not current_state if current_state else True
        
        if is_visible:
            return {'display': 'block', 'marginBottom': '10px', 'backgroundColor': '#3a4a5a', 'borderRadius': '5px', 'padding': '10px', 'maxHeight': '300px', 'overflowY': 'auto'}, "📊 Hide Readings"
        return {'display': 'none'}, "📊 Show Readings"

    @app.callback(
        Output('readings-toggle-state', 'data'),
        Input('toggle-readings', 'n_clicks'),
        State('readings-toggle-state', 'data')
    )
    def update_readings_toggle_state(n_clicks, current_state):
        """Update readings toggle state in store."""
        if n_clicks is None or n_clicks == 0:
            return False
        return not current_state if current_state else True

    @app.callback(
        Output('readings-content', 'children'),
        Input('realtime-weather-interval', 'n_intervals'),
        State('readings-toggle-state', 'data')
    )
    def update_all_readings(_n_intervals, is_visible):
        """Update all readings content when section is visible."""
        if not is_visible:
            return html.P("Loading...", style={"color": "#999", "fontSize": "12px", "textAlign": "center"})
        
        # Fetch all readings data
        temp_data = fetch_realtime_data('air-temperature')
        rain_data = fetch_realtime_data('rainfall')
        humid_data = fetch_realtime_data('relative-humidity')
        wind_data = fetch_realtime_data('wind-speed')
        
        # Format all readings
        all_readings = []
        
        # Temperature readings
        if temp_data and 'data' in temp_data:
            api_data = temp_data['data']
            if 'readings' in api_data and api_data['readings']:
                reading_item = api_data['readings'][0]
                readings = reading_item.get('data', [])
                stations = build_station_lookup(temp_data)
                unit = _normalize_unit(api_data.get('readingUnit', ''), '°C')
                for reading in sorted(readings, key=lambda x: stations.get(x.get('stationId', ''), {}).get('name', '').lower()):
                    station_id = reading.get('stationId', '')
                    name = stations.get(station_id, {}).get('name', station_id)
                    value = reading.get('value', 'N/A')
                    all_readings.append({
                        'type': '🌡️ Temperature',
                        'location': name,
                        'value': f"{value}{unit}",
                        'color': '#FF9800'
                    })
        
        # Rainfall readings
        if rain_data and 'data' in rain_data:
            api_data = rain_data['data']
            if 'readings' in api_data and api_data['readings']:
                reading_item = api_data['readings'][0]
                readings = reading_item.get('data', [])
                stations = build_station_lookup(rain_data)
                unit = _normalize_unit(api_data.get('readingUnit', ''), 'mm')
                for reading in sorted(readings, key=lambda x: stations.get(x.get('stationId', ''), {}).get('name', '').lower()):
                    station_id = reading.get('stationId', '')
                    name = stations.get(station_id, {}).get('name', station_id)
                    value = reading.get('value', 'N/A')
                    all_readings.append({
                        'type': '🌧️ Rainfall',
                        'location': name,
                        'value': f"{value} {unit}",
                        'color': '#2196F3'
                    })
        
        # Humidity readings
        if humid_data and 'data' in humid_data:
            api_data = humid_data['data']
            if 'readings' in api_data and api_data['readings']:
                reading_item = api_data['readings'][0]
                readings = reading_item.get('data', [])
                stations = build_station_lookup(humid_data)
                unit = _normalize_unit(api_data.get('readingUnit', ''), '%')
                for reading in sorted(readings, key=lambda x: stations.get(x.get('stationId', ''), {}).get('name', '').lower()):
                    station_id = reading.get('stationId', '')
                    name = stations.get(station_id, {}).get('name', station_id)
                    value = reading.get('value', 'N/A')
                    all_readings.append({
                        'type': '💧 Humidity',
                        'location': name,
                        'value': f"{value} {unit}",
                        'color': '#00BCD4'
                    })
        
        # Wind readings
        if wind_data and 'data' in wind_data:
            api_data = wind_data['data']
            if 'readings' in api_data and api_data['readings']:
                reading_item = api_data['readings'][0]
                readings = reading_item.get('data', [])
                stations = build_station_lookup(wind_data)
                speed_unit = api_data.get('readingUnit', 'km/h')
                for reading in sorted(readings, key=lambda x: stations.get(x.get('stationId', ''), {}).get('name', '').lower()):
                    station_id = reading.get('stationId', '')
                    name = stations.get(station_id, {}).get('name', station_id)
                    speed_kmh = _convert_to_kmh(reading.get('value', 0), speed_unit)
                    icon = get_windspeed_icon(speed_kmh)
                    all_readings.append({
                        'type': '💨 Wind',
                        'location': name,
                        'value': f"{icon} {speed_kmh} km/h",
                        'color': '#4CAF50'
                    })
        
        if not all_readings:
            return html.P("No readings available", style={"color": "#999", "fontSize": "12px", "textAlign": "center"})
        
        # Format readings with location on one line and value on next line
        reading_divs = []
        for reading in all_readings:
            reading_divs.append(
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(reading['type'], style={
                                    "fontSize": "11px",
                                    "color": reading['color'],
                                    "fontWeight": "600",
                                    "marginRight": "8px",
                                }),
                                html.Span(reading['location'], style={
                                    "fontSize": "11px",
                                    "color": "#ccc",
                                }),
                            ],
                            style={"marginBottom": "2px"}
                        ),
                        html.Div(
                            html.Span(reading['value'], style={
                                "fontSize": "12px",
                                "fontWeight": "600",
                                "color": reading['color'],
                                "marginLeft": "20px",
                            }),
                        ),
                    ],
                    style={
                        "padding": "6px 8px",
                        "backgroundColor": "#2a3a4a",
                        "borderRadius": "4px",
                        "marginBottom": "6px",
                        "borderLeft": f"3px solid {reading['color']}",
                    }
                )
            )
        
        return html.Div(reading_divs)

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
        'wind': '#4CAF50',
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
