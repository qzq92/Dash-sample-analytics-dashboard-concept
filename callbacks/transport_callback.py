"""
Callback functions for handling transport information.
References:
- Taxi: https://api.data.gov.sg/v1/transport/taxi-availability
- Traffic Cameras: https://api.data.gov.sg/v1/transport/traffic-images
- ERP Gantries: https://data.gov.sg/datasets/d_753090823cc9920ac41efaa6530c5893/view
- PUB CCTV: https://data.gov.sg/datasets/d_1de1c45043183bec57e762d01c636eee/view
"""
import re
import os
from datetime import datetime
from dash import Input, Output, State, html
import dash_leaflet as dl
from utils.async_fetcher import fetch_url
from utils.data_download_helper import fetch_erp_gantry_data

# API URLs
TAXI_API_URL = "https://api.data.gov.sg/v1/transport/taxi-availability"
TRAFFIC_IMAGES_API_URL = "https://api.data.gov.sg/v1/transport/traffic-images"


def fetch_taxi_availability():
    """
    Fetch taxi availability data from Data.gov.sg API.
    
    Returns:
        Dictionary containing taxi location data or None if error
    """
    return fetch_url(TAXI_API_URL)


def create_taxi_markers(data):
    """
    Create map markers for taxi locations.
    
    Args:
        data: API response with taxi coordinates
    
    Returns:
        List of dl.CircleMarker components
    """
    markers = []
    
    if not data or 'features' not in data:
        return markers
    
    features = data.get('features', [])
    if not features:
        return markers
    
    # Get coordinates from first feature
    first_feature = features[0]
    geometry = first_feature.get('geometry', {})
    coordinates = geometry.get('coordinates', [])
    
    # Create markers for each taxi location
    # Coordinates are [lon, lat] format, need to swap for Leaflet [lat, lon]
    for coord in coordinates:
        if len(coord) >= 2:
            lon, lat = coord[0], coord[1]
            
            # Create small circle marker for each taxi (lighter yellow for taxi locations)
            markers.append(
                dl.CircleMarker(
                    center=[lat, lon],
                    radius=3,
                    color="#FFD700",  # Lighter yellow (gold)
                    fill=True,
                    fillColor="#FFD700",
                    fillOpacity=0.7,
                    weight=1,
                )
            )
    
    return markers


def format_taxi_count_display(data):
    """
    Format the taxi count display.
    
    Args:
        data: API response with taxi data
    
    Returns:
        HTML Div with taxi count information
    """
    if not data or 'features' not in data:
        return html.Div(
            [
                html.P(
                    "Error loading taxi data",
                    style={
                        "color": "#ff6b6b",
                        "textAlign": "center",
                        "fontSize": "0.75rem",
                    }
                )
            ]
        )
    
    features = data.get('features', [])
    if not features:
        return html.Div(
            [
                html.P(
                    "No taxi data available",
                    style={
                        "color": "#999",
                        "textAlign": "center",
                        "fontSize": "0.75rem",
                    }
                )
            ]
        )
    
    # Get taxi count and timestamp from properties
    first_feature = features[0]
    properties = first_feature.get('properties', {})
    taxi_count = properties.get('taxi_count', 0)
    timestamp = properties.get('timestamp', '')
    
    # Format timestamp
    if timestamp:
        # Parse and format timestamp (e.g., "2025-12-10T20:58:46+08:00")
        try:
            parsed_datetime = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = parsed_datetime.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            formatted_time = timestamp
    else:
        formatted_time = "Unknown"
    
    return html.Div(
        [
            # Large taxi count display
            html.Div(
                [
                    html.Span(
                        "🚕",
                        style={"fontSize": "2rem", "marginRight": "0.625rem", "lineHeight": "1"}
                    ),
                    html.Span(
                        f"{taxi_count:,}",
                        style={
                            "fontSize": "2.5rem",
                            "fontWeight": "bold",
                            "color": "#FFD700",
                            "lineHeight": "1",
                        }
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "marginBottom": "0.625rem",
                    "flexWrap": "wrap",
                }
            ),
            html.P(
                "Available Taxis",
                style={
                    "color": "#fff",
                    "textAlign": "center",
                    "fontSize": "0.875rem",
                    "fontWeight": "600",
                    "margin": "0 0 0.625rem 0",
                }
            ),
            html.P(
                f"Last updated: {formatted_time}",
                style={
                    "color": "#888",
                    "textAlign": "center",
                    "fontSize": "0.6875rem",
                    "fontStyle": "italic",
                    "margin": "0",
                }
            ),
        ],
        style={
            "padding": "0.9375rem",
            "backgroundColor": "#2c3e50",
            "borderRadius": "0.5rem",
            "width": "100%",
            "boxSizing": "border-box",
            "overflow": "hidden",
        }
    )


def fetch_traffic_cameras():
    """
    Fetch traffic camera data from Data.gov.sg API.
    
    Returns:
        Dictionary containing camera data or None if error
    """
    return fetch_url(TRAFFIC_IMAGES_API_URL)


def parse_traffic_camera_data(data):
    """
    Parse traffic camera API response to extract camera metadata.
    
    Args:
        data: API response
    
    Returns:
        Dictionary mapping camera_id to metadata
    """
    camera_dict = {}
    
    if not data or 'items' not in data:
        return camera_dict
    
    items = data.get('items', [])
    if not items:
        return camera_dict
    
    cameras = items[0].get('cameras', [])
    
    for camera in cameras:
        camera_id = camera.get('camera_id', '')
        if camera_id:
            location = camera.get('location', {})
            camera_dict[camera_id] = {
                'timestamp': camera.get('timestamp', ''),
                'image_url': camera.get('image', ''),
                'lat': location.get('latitude'),
                'lon': location.get('longitude'),
            }
    
    return camera_dict


def create_cctv_markers(camera_data):
    """
    Create map markers for CCTV camera locations with image popups.
    
    Args:
        camera_data: Dictionary of camera metadata
    
    Returns:
        List of dl.Marker components with popups
    """
    markers = []
    
    for camera_id, info in camera_data.items():
        lat = info.get('lat')
        lon = info.get('lon')
        image_url = info.get('image_url', '')
        timestamp = info.get('timestamp', '')
        
        if lat is None or lon is None:
            continue

        # Format timestamp if available
        datetime_text = ""
        if timestamp:
            try:
                if isinstance(timestamp, str):
                    # Try to parse and format the timestamp
                    parsed_datetime = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    datetime_text = parsed_datetime.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    datetime_text = str(timestamp)
            except (ValueError, AttributeError):
                datetime_text = str(timestamp) if timestamp else ""

        # Create popup content
        popup_children = [
            html.Strong(
                f"Camera {camera_id}",
                style={"fontSize": "14px"}
            ),
            html.Br(),
        ]
        
        # Add lat/lon on next line
        if lat is not None and lon is not None:
            popup_children.append(
                html.Div(
                    f"(lat: {lat:.6f}, lon: {lon:.6f})",
                    style={"fontSize": "12px", "color": "#888", "marginTop": "4px"}
                )
            )
        
        # Add datetime if available
        if datetime_text:
            popup_children.append(
                html.Div(
                    f"Time: {datetime_text}",
                    style={"fontSize": "12px", "color": "#888", "marginTop": "4px"}
                )
            )
        
        popup_children.append(
            html.Img(
                src=image_url,
                style={
                    "width": "280px",
                    "height": "auto",
                    "marginTop": "8px",
                    "borderRadius": "4px",
                }
            )
        )

        markers.append(
            dl.Marker(
                position=[lat, lon],
                children=[
                    dl.Tooltip(f"Camera {camera_id}"),
                    dl.Popup(
                        children=html.Div(
                            popup_children,
                            style={"textAlign": "center"}
                        ),
                        maxWidth=320,
                    ),
                ],
                icon={
                    "iconUrl": "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
                    "shadowUrl": "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
                    "iconSize": [25, 41],
                    "iconAnchor": [12, 41],
                    "popupAnchor": [1, -34],
                    "shadowSize": [41, 41],
                },
            )
        )
    
    return markers


def format_cctv_count_display(camera_data):
    """
    Format the CCTV camera count display.
    
    Args:
        camera_data: Dictionary of camera metadata
    
    Returns:
        HTML Div with camera count information
    """
    if not camera_data:
        return html.Div(
            [
                html.P(
                    "Error loading camera data",
                    style={
                        "color": "#ff6b6b",
                        "textAlign": "center",
                        "fontSize": "0.75rem",
                    }
                )
            ]
        )
    
    camera_count = len(camera_data)
    
    # Get timestamp from first camera
    first_camera = next(iter(camera_data.values()), {})
    timestamp = first_camera.get('timestamp', '')
    
    if timestamp:
        try:
            parsed_datetime = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = parsed_datetime.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            formatted_time = timestamp
    else:
        formatted_time = "Unknown"
    
    return html.Div(
        [
            html.Div(
                [
                    html.Span(
                        "📹",
                        style={"fontSize": "2rem", "marginRight": "0.625rem", "lineHeight": "1"}
                    ),
                    html.Span(
                        f"{camera_count}",
                        style={
                            "fontSize": "2.5rem",
                            "fontWeight": "bold",
                            "color": "#4CAF50",
                            "lineHeight": "1",
                        }
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "marginBottom": "0.625rem",
                    "flexWrap": "wrap",
                }
            ),
            html.P(
                "Traffic Cameras",
                style={
                    "color": "#fff",
                    "textAlign": "center",
                    "fontSize": "0.875rem",
                    "fontWeight": "600",
                    "margin": "0 0 0.625rem 0",
                }
            ),
            html.P(
                f"Last updated: {formatted_time}",
                style={
                    "color": "#888",
                    "textAlign": "center",
                    "fontSize": "0.6875rem",
                    "fontStyle": "italic",
                    "margin": "0",
                }
            ),
            html.P(
                "Click markers on map to view live feed",
                style={
                    "color": "#4CAF50",
                    "textAlign": "center",
                    "fontSize": "0.625rem",
                    "margin": "0.625rem 0 0 0",
                }
            ),
        ],
        style={
            "padding": "0.9375rem",
            "backgroundColor": "#2c3e50",
            "borderRadius": "0.5rem",
            "width": "100%",
            "boxSizing": "border-box",
            "overflow": "hidden",
        }
    )


# fetch_erp_gantry_data is now imported from utils.data_download_helper


def extract_gantry_number(description_html):
    """
    Extract gantry number from HTML description field.
    
    Args:
        description_html: HTML string containing gantry attributes
    
    Returns:
        Gantry number string or "Unknown"
    """
    if not description_html:
        return "Unknown"

    # Look for GNTRY_NUM in the HTML table
    match = re.search(r'<th>GNTRY_NUM</th>\s*<td>([^<]*)</td>', description_html)
    if match:
        gantry_num = match.group(1).strip()
        return gantry_num if gantry_num else "Unknown"

    return "Unknown"


def parse_erp_gantry_data(geojson_data):
    """
    Parse ERP gantry GeoJSON data.
    
    Args:
        geojson_data: GeoJSON FeatureCollection
    
    Returns:
        List of dictionaries with gantry information
    """
    gantries = []

    if not geojson_data or 'features' not in geojson_data:
        return gantries

    features = geojson_data.get('features', [])

    for feature in features:
        properties = feature.get('properties', {})
        geometry = feature.get('geometry', {})

        if geometry.get('type') != 'LineString':
            continue

        coordinates = geometry.get('coordinates', [])
        if len(coordinates) < 2:
            continue

        # Extract gantry number from description
        description = properties.get('Description', '')
        gantry_num = extract_gantry_number(description)
        unique_id = properties.get('Name', '')

        # LineString has two points - convert to [lat, lon] for Leaflet
        # GeoJSON coordinates are [lon, lat, z]
        line_coords = [[coord[1], coord[0]] for coord in coordinates]

        gantries.append({
            'gantry_num': gantry_num,
            'unique_id': unique_id,
            'coordinates': line_coords,
            'description': description,
        })

    return gantries


def create_erp_gantry_markers(gantry_data):
    """
    Create map polylines for ERP gantry locations.
    
    Args:
        gantry_data: List of gantry dictionaries
    
    Returns:
        List of dl.Polyline components
    """
    markers = []

    for gantry in gantry_data:
        coords = gantry.get('coordinates', [])
        gantry_num = gantry.get('gantry_num', 'Unknown')
        unique_id = gantry.get('unique_id', '')

        if not coords or len(coords) < 2:
            continue

        # Create tooltip text
        tooltip_text = f"ERP Gantry {gantry_num}"
        if unique_id and unique_id != f"kml_{gantry_num}":
            tooltip_text += f" (ID: {unique_id})"

        # Create polyline for the gantry (line between two points)
        markers.append(
            dl.Polyline(
                positions=coords,
                color="#FF6B6B",
                weight=4,
                opacity=0.8,
                children=[
                    dl.Tooltip(tooltip_text),
                ]
            )
        )

    return markers


# fetch_pub_cctv_data is now imported from utils.data_download_helper


def fetch_taxi_stands_data():
    """
    Fetch Taxi Stands data from LTA DataMall API asynchronously.
    
    Returns:
        Dictionary containing taxi stands data or None if error
    """
    taxi_stands_url = "https://datamall2.mytransport.sg/ltaodataservice/TaxiStands"
    api_key = os.getenv("LTA_API_KEY")
    
    if not api_key:
        print("Warning: LTA_API_KEY not found in environment variables")
        return None
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "AccountKey": api_key,
        "Content-Type": "application/json"
    }
    
    return fetch_url(taxi_stands_url, headers)


def create_taxi_stands_markers(taxi_stands_data):
    """
    Create map markers for Taxi Stand locations.
    
    Args:
        taxi_stands_data: Dictionary containing taxi stands response from LTA API
    
    Returns:
        List of dl.CircleMarker components
    """
    if not taxi_stands_data:
        return []

    markers = []
    
    # Extract taxi stands from response
    stands = []
    if isinstance(taxi_stands_data, dict):
        if "value" in taxi_stands_data:
            stands = taxi_stands_data.get("value", [])
        elif isinstance(taxi_stands_data, list):
            stands = taxi_stands_data
    elif isinstance(taxi_stands_data, list):
        stands = taxi_stands_data
    
    for stand in stands:
        try:
            latitude = float(stand.get('Latitude', 0))
            longitude = float(stand.get('Longitude', 0))
            taxi_code = stand.get('TaxiCode', 'N/A')
            name = stand.get('Name', 'N/A')
            bfa = stand.get('Bfa', 'N/A')
            ownership = stand.get('Ownership', 'N/A')
            stand_type = stand.get('Type', 'N/A')
            
            if latitude == 0 or longitude == 0:
                continue
            
            # Create tooltip with bulleted points (using HTML for line breaks)
            tooltip_html = (
                f"• Name: {taxi_code}({name})<br>"
                f"• Barrier Free: {bfa}<br>"
                f"• Owner: {ownership}<br>"
                f"• Type: {stand_type}"
            )
            
            markers.append(
                dl.CircleMarker(
                    center=[latitude, longitude],
                    radius=6,
                    color="#FFA500",  # Darker yellow/orange for taxi stands
                    fill=True,
                    fillColor="#FFA500",
                    fillOpacity=0.7,
                    weight=2,
                    children=[
                        dl.Tooltip(tooltip_html),
                    ]
                )
            )
        except (ValueError, TypeError, KeyError):
            continue
            
    return markers


def format_taxi_stands_count_display(taxi_stands_data):
    """
    Format the Taxi Stands count display.
    
    Args:
        taxi_stands_data: Dictionary containing taxi stands response from LTA API
    
    Returns:
        HTML Div with taxi stands count information
    """
    if not taxi_stands_data:
        return html.Div(
            [
                html.P(
                    "Error loading taxi stands data",
                    style={
                        "color": "#ff6b6b",
                        "textAlign": "center",
                        "padding": "1.25rem",
                        "fontSize": "0.75rem",
                    }
                )
            ]
        )
    
    # Extract count from response
    stands = []
    if isinstance(taxi_stands_data, dict):
        if "value" in taxi_stands_data:
            stands = taxi_stands_data.get("value", [])
        elif isinstance(taxi_stands_data, list):
            stands = taxi_stands_data
    elif isinstance(taxi_stands_data, list):
        stands = taxi_stands_data
    
    count = len(stands)
    return html.Div(
        [
            html.P(
                f"Total taxi stands: {count}",
                style={
                    "color": "#fff",
                    "textAlign": "center",
                    "padding": "0.625rem",
                    "fontSize": "0.875rem",
                    "fontWeight": "600",
                    "margin": "0",
                }
            )
        ]
    )


def format_combined_taxi_display(taxi_data, taxi_stands_data):
    """
    Format the combined taxi locations and stands count display.
    
    Args:
        taxi_data: API response with taxi location data
        taxi_stands_data: Dictionary containing taxi stands response from LTA API
    
    Returns:
        HTML Div with combined taxi locations and stands count information
    """
    # Get taxi count
    taxi_count = 0
    timestamp = "Unknown"
    if taxi_data and 'features' in taxi_data:
        features = taxi_data.get('features', [])
        if features:
            first_feature = features[0]
            properties = first_feature.get('properties', {})
            taxi_count = properties.get('taxi_count', 0)
            timestamp = properties.get('timestamp', '')
    
    # Get taxi stands count
    stands_count = 0
    if taxi_stands_data:
        stands = []
        if isinstance(taxi_stands_data, dict):
            if "value" in taxi_stands_data:
                stands = taxi_stands_data.get("value", [])
            elif isinstance(taxi_stands_data, list):
                stands = taxi_stands_data
        elif isinstance(taxi_stands_data, list):
            stands = taxi_stands_data
        stands_count = len(stands)
    
    # Format timestamp
    if timestamp and timestamp != "Unknown":
        try:
            parsed_datetime = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = parsed_datetime.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            formatted_time = timestamp
    else:
        formatted_time = "Unknown"
    
    return html.Div(
        [
            # Side by side layout for taxi locations and stands
            html.Div(
                [
                    # Left side: Taxi locations
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        "🚕",
                                        style={"fontSize": "1.5rem", "marginRight": "0.5rem", "lineHeight": "1"}
                                    ),
                                    html.Span(
                                        f"{taxi_count:,}",
                                        style={
                                            "fontSize": "2rem",
                                            "fontWeight": "bold",
                                            "color": "#FFD700",  # Lighter yellow
                                            "lineHeight": "1",
                                        }
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "marginBottom": "0.25rem",
                                }
                            ),
                            html.P(
                                "Available Taxis",
                                style={
                                    "color": "#fff",
                                    "textAlign": "center",
                                    "fontSize": "0.75rem",
                                    "fontWeight": "600",
                                    "margin": "0",
                                }
                            ),
                        ],
                        style={
                            "flex": "1",
                            "display": "flex",
                            "flexDirection": "column",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "padding": "0.5rem",
                        }
                    ),
                    # Right side: Taxi stands
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        "🚕",
                                        style={"fontSize": "1.5rem", "marginRight": "0.5rem", "lineHeight": "1"}
                                    ),
                                    html.Span(
                                        f"{stands_count}",
                                        style={
                                            "fontSize": "2rem",
                                            "fontWeight": "bold",
                                            "color": "#FFA500",  # Darker yellow/orange
                                            "lineHeight": "1",
                                        }
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "marginBottom": "0.25rem",
                                }
                            ),
                            html.P(
                                "Taxi Stands",
                                style={
                                    "color": "#fff",
                                    "textAlign": "center",
                                    "fontSize": "0.75rem",
                                    "fontWeight": "600",
                                    "margin": "0",
                                }
                            ),
                        ],
                        style={
                            "flex": "1",
                            "display": "flex",
                            "flexDirection": "column",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "padding": "0.5rem",
                            "borderLeft": "0.0625rem solid #5a6a7a",
                        }
                    ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "row",
                    "width": "100%",
                    "marginBottom": "0.5rem",
                }
            ),
            html.P(
                f"Last updated: {formatted_time}",
                style={
                    "color": "#888",
                    "textAlign": "center",
                    "fontSize": "0.6875rem",
                    "fontStyle": "italic",
                    "margin": "0",
                }
            ),
        ],
        style={
            "padding": "0.9375rem",
            "backgroundColor": "#2c3e50",
            "borderRadius": "0.5rem",
            "width": "100%",
            "boxSizing": "border-box",
            "overflow": "hidden",
            "display": "flex",
            "flexDirection": "column",
            "height": "100%",
        }
    )


def fetch_speed_band_data():
    """
    Fetch Traffic Speed Band data from LTA DataMall API.
    
    Returns:
        Dictionary containing speed band data or None if error
    """
    speed_band_url = "https://datamall2.mytransport.sg/ltaodataservice/v4/TrafficSpeedBands"
    api_key = os.getenv("LTA_API_KEY")
    
    if not api_key:
        print("Warning: LTA_API_KEY not found in environment variables")
        return None
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "AccountKey": api_key,
        "Content-Type": "application/json"
    }
    
    return fetch_url(speed_band_url, headers)


def create_speed_band_markers(speed_data):
    """
    Create map polylines for Traffic Speed Band locations.
    
    Args:
        speed_data: List of speed band dictionaries
    
    Returns:
        List of dl.Polyline components
    """
    if not speed_data:
        return []

    markers = []
    
    # Speed band colors based on range
    band_colors = {
        '1': "#FF0000", # 0-9 km/h (Red)
        '2': "#FF4500", # 10-19 km/h (Orange Red)
        '3': "#FFA500", # 20-29 km/h (Orange)
        '4': "#FFD700", # 30-39 km/h (Gold)
        '5': "#FFFF00", # 40-49 km/h (Yellow)
        '6': "#ADFF2F", # 50-59 km/h (Green Yellow)
        '7': "#32CD32", # 60-69 km/h (Lime Green)
        '8': "#008000", # 70+ km/h (Green)
    }

    # Handle both list and dict with 'value' key
    items = speed_data.get('value', []) if isinstance(speed_data, dict) else speed_data
    
    for item in items:
        try:
            start_lat = float(item.get('StartLat', 0))
            start_lon = float(item.get('StartLon', 0))
            end_lat = float(item.get('EndLat', 0))
            end_lon = float(item.get('EndLon', 0))
            road_name = item.get('RoadName', 'Unknown Road')
            band = str(item.get('SpeedBand', '0'))
            
            if start_lat == 0 or end_lat == 0:
                continue
                
            color = band_colors.get(band, "#888888")
            
            tooltip_text = f"Road: {road_name}\nSpeed Band: {band}"
            
            markers.append(
                dl.Polyline(
                    positions=[[start_lat, start_lon], [end_lat, end_lon]],
                    color=color,
                    weight=5,
                    opacity=0.8,
                    children=[
                        dl.Tooltip(tooltip_text),
                    ]
                )
            )
        except (ValueError, TypeError):
            continue
            
    return markers


def format_speed_band_display():
    """
    Format the Traffic Speed Band information display.
    
    Returns:
        HTML elements with speed band definitions
    """
    definitions = [
        ("1", "0 < 9 km/h"),
        ("2", "10 < 19 km/h"),
        ("3", "20 < 29 km/h"),
        ("4", "30 < 39 km/h"),
        ("5", "40 < 49 km/h"),
        ("6", "50 < 59 km/h"),
        ("7", "60 < 69 km/h"),
        ("8", "70+ km/h"),
    ]
    
    # Create colored dots for the legend
    band_colors = {
        '1': "#FF0000", '2': "#FF4500", '3': "#FFA500", '4': "#FFD700",
        '5': "#FFFF00", '6': "#ADFF2F", '7': "#32CD32", '8': "#008000"
    }
    
    return html.Div([
        html.Div([
            html.P("Speed Band Definitions:", style={
                "color": "#fff",
                "fontSize": "0.8125rem",
                "fontWeight": "600",
                "marginBottom": "0.5rem"
            }),
            html.Div([
                html.Div([
                    html.Div(style={
                        "width": "10px",
                        "height": "10px",
                        "borderRadius": "50%",
                        "backgroundColor": band_colors[code],
                        "marginRight": "8px"
                    }),
                    html.Span(f"{code} – {desc}", style={
                        "color": "#ccc",
                        "fontSize": "0.75rem"
                    })
                ], style={
                    "display": "flex",
                    "alignItems": "center",
                    "marginBottom": "4px"
                }) for code, desc in definitions
            ])
        ], style={"padding": "0.625rem"})
    ])


def format_erp_count_display(gantry_data):
    """
    Format the ERP gantry count display.
    
    Args:
        gantry_data: List of gantry dictionaries
    
    Returns:
        HTML Div with gantry count information
    """
    if not gantry_data:
        return html.Div(
            [
                html.P(
                    "Error loading ERP gantry data",
                    style={
                        "color": "#ff6b6b",
                        "textAlign": "center",
                        "fontSize": "0.75rem",
                    }
                )
            ]
        )

    gantry_count = len(gantry_data)

    return html.Div(
        [
            html.Div(
                [
                    html.Span(
                        "🚧",
                        style={"fontSize": "2rem", "marginRight": "0.625rem", "lineHeight": "1"}
                    ),
                    html.Span(
                        f"{gantry_count}",
                        style={
                            "fontSize": "2.5rem",
                            "fontWeight": "bold",
                            "color": "#FF6B6B",
                            "lineHeight": "1",
                        }
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "marginBottom": "0.625rem",
                    "flexWrap": "wrap",
                }
            ),
            html.P(
                "ERP Gantries",
                style={
                    "color": "#fff",
                    "textAlign": "center",
                    "fontSize": "0.875rem",
                    "fontWeight": "600",
                    "margin": "0 0 0.625rem 0",
                }
            ),
            html.P(
                "Red lines show gantry locations",
                style={
                    "color": "#888",
                    "textAlign": "center",
                    "fontSize": "0.6875rem",
                    "fontStyle": "italic",
                    "margin": "0",
                }
            ),
        ],
        style={
            "padding": "0.9375rem",
            "backgroundColor": "#2c3e50",
            "borderRadius": "0.5rem",
            "width": "100%",
            "boxSizing": "border-box",
            "overflow": "hidden",
        }
    )


def register_transport_callbacks(app):
    """
    Register callbacks for transport information.
    
    Args:
        app: Dash app instance
    """
    
    @app.callback(
        [Output('taxi-toggle-state', 'data'),
         Output('taxi-toggle-btn', 'style'),
         Output('taxi-toggle-btn', 'children')],
        Input('taxi-toggle-btn', 'n_clicks'),
        State('taxi-toggle-state', 'data'),
        prevent_initial_call=True
    )
    def toggle_taxi_display(_n_clicks, current_state):
        """Toggle taxi markers display on/off."""
        new_state = not current_state
        
        if new_state:
            # Active state - yellow background
            style = {
                "backgroundColor": "#FFD700",
                "border": "none",
                "borderRadius": "4px",
                "color": "#000",
                "cursor": "pointer",
                "padding": "6px 12px",
                "fontSize": "12px",
                "fontWeight": "600",
            }
            text = "Hide from Map"
        else:
            # Inactive state - outline
            style = {
                "backgroundColor": "transparent",
                "border": "2px solid #FFD700",
                "borderRadius": "4px",
                "color": "#FFD700",
                "cursor": "pointer",
                "padding": "4px 10px",
                "fontSize": "12px",
                "fontWeight": "600",
            }
            text = "Show on Map"
        
        return new_state, style, text
    
    @app.callback(
        [Output('taxi-markers', 'children'),
         Output('taxi-count-display', 'children')],
        [Input('taxi-toggle-state', 'data'),
         Input('transport-interval', 'n_intervals')]
    )
    def update_taxi_display(show_taxis, n_intervals):
        """Update taxi locations and stands markers and count display."""
        _ = n_intervals  # Used for periodic refresh
        
        if not show_taxis:
            # Return empty markers and default message
            return [], html.P(
                "Click 'Show on Map' to load taxi locations and stands",
                style={
                    "color": "#999",
                    "textAlign": "center",
                    "padding": "20px",
                    "fontStyle": "italic",
                    "fontSize": "12px",
                }
            )
        
        # Fetch both taxi locations and taxi stands data
        taxi_data = fetch_taxi_availability()
        taxi_stands_data = fetch_taxi_stands_data()
        
        # Create markers for both
        taxi_markers = create_taxi_markers(taxi_data)
        taxi_stands_markers = create_taxi_stands_markers(taxi_stands_data)
        
        # Combine all markers
        all_markers = taxi_markers + taxi_stands_markers
        
        # Create combined count display
        count_display = format_combined_taxi_display(taxi_data, taxi_stands_data)
        
        return all_markers, count_display

    @app.callback(
        [Output('cctv-toggle-state', 'data'),
         Output('cctv-toggle-btn', 'style'),
         Output('cctv-toggle-btn', 'children')],
        Input('cctv-toggle-btn', 'n_clicks'),
        State('cctv-toggle-state', 'data'),
        prevent_initial_call=True
    )
    def toggle_cctv_display(_n_clicks, current_state):
        """Toggle CCTV markers display on/off."""
        new_state = not current_state
        
        if new_state:
            # Active state - green background
            style = {
                "backgroundColor": "#4CAF50",
                "border": "none",
                "borderRadius": "4px",
                "color": "#fff",
                "cursor": "pointer",
                "padding": "6px 12px",
                "fontSize": "12px",
                "fontWeight": "600",
            }
            text = "Hide from Map"
        else:
            # Inactive state - outline
            style = {
                "backgroundColor": "transparent",
                "border": "2px solid #4CAF50",
                "borderRadius": "4px",
                "color": "#4CAF50",
                "cursor": "pointer",
                "padding": "4px 10px",
                "fontSize": "12px",
                "fontWeight": "600",
            }
            text = "Show on Map"
        
        return new_state, style, text

    @app.callback(
        [Output('cctv-markers', 'children'),
         Output('cctv-count-display', 'children')],
        [Input('cctv-toggle-state', 'data'),
         Input('transport-interval', 'n_intervals')]
    )
    def update_cctv_display(show_cctv, n_intervals):
        """Update CCTV markers and count display."""
        _ = n_intervals  # Used for periodic refresh
        
        if not show_cctv:
            # Return empty markers and default message
            return [], html.P(
                "Click 'Show on Map' to load camera locations",
                style={
                    "color": "#999",
                    "textAlign": "center",
                    "padding": "20px",
                    "fontStyle": "italic",
                    "fontSize": "12px",
                }
            )
        
        # Fetch camera data
        data = fetch_traffic_cameras()
        camera_data = parse_traffic_camera_data(data)
        
        # Create markers and count display
        markers = create_cctv_markers(camera_data)
        count_display = format_cctv_count_display(camera_data)
        
        return markers, count_display

    @app.callback(
        [Output('erp-toggle-state', 'data'),
         Output('erp-toggle-btn', 'style'),
         Output('erp-toggle-btn', 'children')],
        Input('erp-toggle-btn', 'n_clicks'),
        State('erp-toggle-state', 'data'),
        prevent_initial_call=True
    )
    def toggle_erp_display(_n_clicks, current_state):
        """Toggle ERP gantry markers display on/off."""
        new_state = not current_state

        if new_state:
            # Active state - red background
            style = {
                "backgroundColor": "#FF6B6B",
                "border": "none",
                "borderRadius": "4px",
                "color": "#fff",
                "cursor": "pointer",
                "padding": "6px 12px",
                "fontSize": "12px",
                "fontWeight": "600",
            }
            text = "Hide from Map"
        else:
            # Inactive state - outline
            style = {
                "backgroundColor": "transparent",
                "border": "2px solid #FF6B6B",
                "borderRadius": "4px",
                "color": "#FF6B6B",
                "cursor": "pointer",
                "padding": "4px 10px",
                "fontSize": "12px",
                "fontWeight": "600",
            }
            text = "Show on Map"

        return new_state, style, text

    @app.callback(
        [Output('erp-markers', 'children'),
         Output('erp-count-display', 'children')],
        [Input('erp-toggle-state', 'data'),
         Input('transport-interval', 'n_intervals')]
    )
    def update_erp_display(show_erp, n_intervals):
        """Update ERP gantry markers and count display."""
        _ = n_intervals  # Used for periodic refresh

        if not show_erp:
            # Return empty markers and default message
            return [], html.P(
                "Click 'Show on Map' to load gantry locations",
                style={
                    "color": "#999",
                    "textAlign": "center",
                    "padding": "20px",
                    "fontStyle": "italic",
                    "fontSize": "12px",
                }
            )

        # Fetch gantry data
        geojson_data = fetch_erp_gantry_data()
        gantry_data = parse_erp_gantry_data(geojson_data)

        # Create markers and count display
        markers = create_erp_gantry_markers(gantry_data)
        count_display = format_erp_count_display(gantry_data)

        return markers, count_display

    @app.callback(
        [Output('speed-band-toggle-state', 'data'),
         Output('speed-band-toggle-btn', 'style'),
         Output('speed-band-toggle-btn', 'children')],
        Input('speed-band-toggle-btn', 'n_clicks'),
        State('speed-band-toggle-state', 'data'),
        prevent_initial_call=True
    )
    def toggle_speed_band_display(_n_clicks, current_state):
        """Toggle Speed Band display on/off."""
        new_state = not current_state

        if new_state:
            # Active state - cyan background
            style = {
                "backgroundColor": "#00BCD4",
                "border": "none",
                "borderRadius": "4px",
                "color": "#fff",
                "cursor": "pointer",
                "padding": "6px 12px",
                "fontSize": "12px",
                "fontWeight": "600",
            }
            text = "Hide from Map"
        else:
            # Inactive state - outline
            style = {
                "backgroundColor": "transparent",
                "border": "2px solid #00BCD4",
                "borderRadius": "4px",
                "color": "#00BCD4",
                "cursor": "pointer",
                "padding": "4px 10px",
                "fontSize": "12px",
                "fontWeight": "600",
            }
            text = "Show on Map"

        return new_state, style, text

    @app.callback(
        [Output('speed-band-markers', 'children'),
         Output('speed-band-display', 'children')],
        [Input('speed-band-toggle-state', 'data'),
         Input('transport-interval', 'n_intervals')]
    )
    def update_speed_band_display(show_speed_band, n_intervals):
        """Update Speed Band markers and information display."""
        _ = n_intervals  # Used for periodic refresh

        if not show_speed_band:
            # Return empty markers and default message
            return [], html.P(
                "Click 'Show on Map' to load speed band information",
                style={
                    "color": "#999",
                    "textAlign": "center",
                    "padding": "20px",
                    "fontStyle": "italic",
                    "fontSize": "12px",
                }
            )

        # Fetch speed band data
        data = fetch_speed_band_data()

        # Create markers and information display
        markers = create_speed_band_markers(data)
        info_display = format_speed_band_display()

        return markers, info_display


