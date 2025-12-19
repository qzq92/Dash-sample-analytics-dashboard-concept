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
import base64
from datetime import datetime
from dash import Input, Output, State, html
import dash_leaflet as dl
from utils.async_fetcher import fetch_url
from utils.data_download_helper import fetch_erp_gantry_data
from utils.map_utils import SG_MAP_CENTER
from conf.speed_band_config import get_speed_midpoint
from callbacks.map_callback import _haversine_distance_m

# API URLs
TAXI_API_URL = "https://api.data.gov.sg/v1/transport/taxi-availability"
TRAFFIC_IMAGES_API_URL = "https://api.data.gov.sg/v1/transport/traffic-images"
TRAFFIC_INCIDENTS_URL = "https://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents"
FAULTY_TRAFFIC_LIGHTS_URL = "https://datamall2.mytransport.sg/ltaodataservice/FaultyTrafficLights"
BICYCLE_PARKING_URL = "https://datamall2.mytransport.sg/ltaodataservice/BicycleParkingv2"


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
                f"• Name: {taxi_code}({name})"
                f"• Barrier Free: {bfa}"
                f"• Owner: {ownership}"
                f"• Type: {stand_type}"
            )
            
            # Create triangle marker for taxi stands using DivIcon with SVG
            triangle_svg = (
                '<svg width="16" height="16" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">'
                '<path d="M 8 0 L 16 16 L 0 16 Z" fill="#FFA500" stroke="#FFA500" stroke-width="1"/>'
                '</svg>'
            )
            triangle_svg_base64 = base64.b64encode(triangle_svg.encode()).decode()
            
            triangle_icon = {
                "iconUrl": f"data:image/svg+xml;base64,{triangle_svg_base64}",
                "iconSize": [16, 16],
                "iconAnchor": [8, 16],
                "popupAnchor": [0, -16],
            }
            
            markers.append(
                dl.Marker(
                    position=[latitude, longitude],
                    icon=triangle_icon,
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


def fetch_traffic_incidents_data():
    """
    Fetch traffic incidents from LTA DataMall API.
    
    Returns:
        Dictionary containing traffic incidents data or None if error
    """
    api_key = os.getenv("LTA_API_KEY")
    
    if not api_key:
        print("Warning: LTA_API_KEY not found in environment variables")
        return None
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "AccountKey": api_key,
        "Content-Type": "application/json"
    }
    
    return fetch_url(TRAFFIC_INCIDENTS_URL, headers)


def fetch_faulty_traffic_lights_data():
    """
    Fetch faulty traffic lights from LTA DataMall API.
    
    Returns:
        Dictionary containing faulty traffic lights data or None if error
    """
    api_key = os.getenv("LTA_API_KEY")
    
    if not api_key:
        print("Warning: LTA_API_KEY not found in environment variables")
        return None
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "AccountKey": api_key,
        "Content-Type": "application/json"
    }
    
    return fetch_url(FAULTY_TRAFFIC_LIGHTS_URL, headers)


def create_traffic_incidents_markers(incidents_data, faulty_lights_data=None):
    """
    Create map markers for traffic incidents and faulty traffic lights.
    
    Args:
        incidents_data: Dictionary containing traffic incidents response from LTA API
        faulty_lights_data: Optional dictionary containing faulty traffic lights response
    
    Returns:
        List of dl.CircleMarker components
    """
    markers = []
    
    # Extract incidents
    incidents = []
    if incidents_data:
        if isinstance(incidents_data, dict):
            if 'value' in incidents_data:
                incidents = incidents_data.get('value', [])
            elif isinstance(incidents_data, list):
                incidents = incidents_data
        elif isinstance(incidents_data, list):
            incidents = incidents_data
    
    # Create markers for traffic incidents
    for incident in incidents:
        if not isinstance(incident, dict):
            continue
        
        try:
            # Try different possible keys for coordinates
            latitude = (
                float(incident.get('Latitude', 0)) or
                float(incident.get('latitude', 0)) or
                float(incident.get('Lat', 0)) or
                float(incident.get('lat', 0)) or
                0
            )
            longitude = (
                float(incident.get('Longitude', 0)) or
                float(incident.get('longitude', 0)) or
                float(incident.get('Lon', 0)) or
                float(incident.get('lon', 0)) or
                0
            )
            
            if latitude == 0 or longitude == 0:
                continue
            
            # Get incident type/message
            incident_type = (
                incident.get('Type') or
                incident.get('type') or
                incident.get('Message') or
                incident.get('message') or
                incident.get('IncidentType') or
                incident.get('incidentType') or
                'Unknown Incident'
            )
            
            # Create tooltip with incident information
            tooltip_html = f"🚦 {incident_type}"
            
            # Use red color for incidents
            markers.append(
                dl.CircleMarker(
                    center=[latitude, longitude],
                    radius=8,
                    color="#FF0000",  # Red for incidents
                    fill=True,
                    fillColor="#FF0000",
                    fillOpacity=0.7,
                    weight=2,
                    children=[
                        dl.Tooltip(tooltip_html),
                    ]
                )
            )
        except (ValueError, TypeError, KeyError):
            continue
    
    # Add faulty traffic lights if provided
    if faulty_lights_data:
        faulty_lights = []
        if isinstance(faulty_lights_data, dict):
            if 'value' in faulty_lights_data:
                faulty_lights = faulty_lights_data.get('value', [])
            elif isinstance(faulty_lights_data, list):
                faulty_lights = faulty_lights_data
        elif isinstance(faulty_lights_data, list):
            faulty_lights = faulty_lights_data
        
        for light in faulty_lights:
            if not isinstance(light, dict):
                continue
            
            try:
                latitude = (
                    float(light.get('Latitude', 0)) or
                    float(light.get('latitude', 0)) or
                    float(light.get('Lat', 0)) or
                    float(light.get('lat', 0)) or
                    0
                )
                longitude = (
                    float(light.get('Longitude', 0)) or
                    float(light.get('longitude', 0)) or
                    float(light.get('Lon', 0)) or
                    float(light.get('lon', 0)) or
                    0
                )
                
                if latitude == 0 or longitude == 0:
                    continue
                
                node_id = (
                    light.get('NodeID') or
                    light.get('nodeID') or
                    light.get('node_id') or
                    'N/A'
                )
                
                tooltip_html = f"🚦 Faulty Traffic Light<br>Node ID: {node_id}"
                
                # Use orange color for faulty traffic lights
                markers.append(
                    dl.CircleMarker(
                        center=[latitude, longitude],
                        radius=6,
                        color="#FF8C00",  # Dark orange for faulty lights
                        fill=True,
                        fillColor="#FF8C00",
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


def format_traffic_incidents_count_display(incidents_data, faulty_lights_data=None):
    """
    Format the traffic incidents count display.
    
    Args:
        incidents_data: Dictionary containing traffic incidents response from LTA API
        faulty_lights_data: Optional dictionary containing faulty traffic lights response
    
    Returns:
        HTML Div with traffic incidents count information
    """
    # Extract incidents
    incidents = []
    if incidents_data:
        if isinstance(incidents_data, dict):
            if 'value' in incidents_data:
                incidents = incidents_data.get('value', [])
            elif isinstance(incidents_data, list):
                incidents = incidents_data
        elif isinstance(incidents_data, list):
            incidents = incidents_data
    
    # Count incidents by type
    incident_counts = {}
    for incident in incidents:
        if isinstance(incident, dict):
            incident_type = (
                incident.get('Type') or
                incident.get('type') or
                incident.get('Message') or
                incident.get('message') or
                incident.get('IncidentType') or
                incident.get('incidentType') or
                'Unknown'
            )
            incident_counts[incident_type] = incident_counts.get(incident_type, 0) + 1
    
    # Count faulty traffic lights
    faulty_lights_count = 0
    if faulty_lights_data:
        faulty_lights = []
        if isinstance(faulty_lights_data, dict):
            if 'value' in faulty_lights_data:
                faulty_lights = faulty_lights_data.get('value', [])
            elif isinstance(faulty_lights_data, list):
                faulty_lights = faulty_lights_data
        elif isinstance(faulty_lights_data, list):
            faulty_lights = faulty_lights_data
        
        # Count unique NodeID instances
        node_ids = set()
        for light in faulty_lights:
            if isinstance(light, dict):
                node_id = (
                    light.get('NodeID') or
                    light.get('nodeID') or
                    light.get('node_id') or
                    None
                )
                if node_id:
                    node_ids.add(str(node_id))
        faulty_lights_count = len(node_ids)
        if faulty_lights_count > 0:
            incident_counts['Faulty Traffic Lights'] = faulty_lights_count
    
    total_count = len(incidents) + faulty_lights_count
    
    if not incident_counts:
        return html.Div(
            [
                html.P(
                    "No traffic incidents reported",
                    style={
                        "color": "#999",
                        "textAlign": "center",
                        "padding": "0.625rem",
                        "fontSize": "0.875rem",
                        "fontWeight": "600",
                        "margin": "0",
                    }
                )
            ]
        )
    
    # Create display with incident types
    incident_items = []
    for incident_type, count in sorted(incident_counts.items()):
        incident_items.append(
            html.Div(
                [
                    html.Span(
                        incident_type,
                        style={
                            "color": "#fff",
                            "fontSize": "0.75rem",
                            "fontWeight": "600",
                        }
                    ),
                    html.Span(
                        f"{count}",
                        style={
                            "color": "#FF6B6B",
                            "fontSize": "0.875rem",
                            "fontWeight": "bold",
                            "marginLeft": "0.5rem",
                        }
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "padding": "0.25rem 0",
                    "borderBottom": "0.0625rem solid #5a6a7a",
                }
            )
        )
    
    return html.Div(
        [
            html.Div(
                [
                    html.Span(
                        "🚦",
                        style={"fontSize": "2rem", "marginRight": "0.625rem", "lineHeight": "1"}
                    ),
                    html.Span(
                        f"{total_count}",
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
                "Total Incidents",
                style={
                    "color": "#fff",
                    "textAlign": "center",
                    "fontSize": "0.875rem",
                    "fontWeight": "600",
                    "margin": "0 0 0.625rem 0",
                }
            ),
            html.Div(
                incident_items,
                style={
                    "overflowY": "auto",
                    "maxHeight": "200px",
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


def fetch_bicycle_parking_data():
    """
    Fetch bicycle parking data from LTA DataMall API.
    Uses default map center coordinates and dist=50 to get all bicycle parking lots.
    
    Returns:
        Dictionary containing bicycle parking data or None if error
    """
    import requests
    
    api_key = os.getenv("LTA_API_KEY")
    
    if not api_key:
        print("Warning: LTA_API_KEY not found in environment variables")
        return None
    
    # Use default map center coordinates
    lat, lon = SG_MAP_CENTER
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "AccountKey": api_key,
        "Content-Type": "application/json"
    }
    
    # Set dist=50 to get all bicycle parking lots
    params = {
        "Lat": lat,
        "Long": lon,
        "Dist": 50
    }
    
    try:
        response = requests.get(BICYCLE_PARKING_URL, headers=headers, params=params, timeout=10)
        if 200 <= response.status_code < 300:
            return response.json()
        print(f"Bicycle parking API request failed: status={response.status_code}")
    except (requests.exceptions.RequestException, ValueError) as error:
        print(f"Error fetching bicycle parking data: {error}")
    return None


def fetch_nearby_bicycle_parking(lat: float, lon: float, radius_m: int = 500) -> list:
    """
    Fetch nearby bicycle parking data from LTA DataMall API within specified radius.
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        radius_m: Search radius in meters (default: 500)
    
    Returns:
        List of bicycle parking dictionaries with distance information, sorted by distance
    """
    import requests
    
    api_key = os.getenv("LTA_API_KEY")
    
    if not api_key:
        print("Warning: LTA_API_KEY not found in environment variables")
        return []
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "AccountKey": api_key,
        "Content-Type": "application/json"
    }
    
    # Use dist parameter - API accepts distance in km, so 0.5 for 500m
    # But we'll also filter by haversine distance to ensure accuracy
    dist_km = max(0.5, radius_m / 1000.0)  # At least 0.5km, or convert radius_m to km
    
    params = {
        "Lat": lat,
        "Long": lon,
        "Dist": dist_km
    }
    
    try:
        response = requests.get(BICYCLE_PARKING_URL, headers=headers, params=params, timeout=10)
        if 200 <= response.status_code < 300:
            data = response.json()
            
            if not data or 'value' not in data:
                return []
            
            parking_locations = data.get('value', [])
            processed_results = []
            
            for loc in parking_locations:
                try:
                    parking_lat = float(loc.get('Latitude', 0))
                    parking_lon = float(loc.get('Longitude', 0))
                    
                    if parking_lat == 0 or parking_lon == 0:
                        continue
                    
                    # Calculate distance using haversine formula
                    distance_m = _haversine_distance_m(lat, lon, parking_lat, parking_lon)
                    
                    # Only include parking within the specified radius
                    if distance_m <= radius_m:
                        processed_results.append({
                            'description': loc.get('Description', 'N/A'),
                            'rack_type': loc.get('RackType', 'N/A'),
                            'rack_count': loc.get('RackCount', 'N/A'),
                            'shelter_indicator': loc.get('ShelterIndicator', 'N'),
                            'latitude': parking_lat,
                            'longitude': parking_lon,
                            'distance_m': distance_m,
                            'raw_data': loc
                        })
                except (ValueError, TypeError, KeyError) as e:
                    print(f"Error processing bicycle parking data: {e}")
                    continue
            
            # Sort by distance (closest first)
            processed_results.sort(key=lambda x: x['distance_m'])
            
            return processed_results
        
        print(f"Bicycle parking API request failed: status={response.status_code}")
    except (requests.exceptions.RequestException, ValueError) as error:
        print(f"Error fetching nearby bicycle parking data: {error}")
    
    return []


def create_bicycle_parking_markers(bicycle_data):
    """
    Create map markers for bicycle parking locations.
    
    Args:
        bicycle_data: Dictionary containing bicycle parking response from LTA API
    
    Returns:
        List of dl.CircleMarker components
    """
    markers = []
    
    if not bicycle_data or 'value' not in bicycle_data:
        return markers
    
    parking_locations = bicycle_data.get('value', [])
    
    for loc in parking_locations:
        try:
            latitude = float(loc.get('Latitude', 0))
            longitude = float(loc.get('Longitude', 0))
            description = loc.get('Description', 'N/A')
            rack_type = loc.get('RackType', 'N/A')
            rack_count = loc.get('RackCount', 'N/A')
            shelter_indicator = loc.get('ShelterIndicator', 'N')
            
            if latitude == 0 or longitude == 0:
                continue
            
            # Determine sheltered/unsheltered status
            shelter_status = 'sheltered' if shelter_indicator == 'Y' else 'unsheltered'
            
            # Create tooltip with formatted information
            tooltip_html = (
                f"{description} ({shelter_status})<br>"
                f"RackType: {rack_type}<br>"
                f"RackCount: {rack_count}"
            )
            
            # Create circle marker for bicycle parking
            markers.append(
                dl.CircleMarker(
                    center=[latitude, longitude],
                    radius=5,
                    color="#4CAF50",  # Green color for bicycle parking
                    fill=True,
                    fillColor="#4CAF50",
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


def create_nearby_bicycle_parking_markers(bicycle_parking_list):
    """
    Create map markers for nearby bicycle parking locations from processed list.
    
    Args:
        bicycle_parking_list: List of processed bicycle parking dictionaries
    
    Returns:
        List of dl.CircleMarker components
    """
    markers = []
    
    if not bicycle_parking_list:
        return markers
    
    for parking in bicycle_parking_list:
        try:
            latitude = parking.get('latitude', 0)
            longitude = parking.get('longitude', 0)
            description = parking.get('description', 'N/A')
            rack_type = parking.get('rack_type', 'N/A')
            rack_count = parking.get('rack_count', 'N/A')
            shelter_indicator = parking.get('shelter_indicator', 'N')
            
            if latitude == 0 or longitude == 0:
                continue
            
            # Determine sheltered/unsheltered status
            shelter_status = 'sheltered' if shelter_indicator == 'Y' else 'unsheltered'
            
            # Create tooltip with formatted information
            tooltip_html = (
                f"{description} ({shelter_status})<br>"
                f"RackType: {rack_type}<br>"
                f"RackCount: {rack_count}"
            )
            
            # Create circle marker for bicycle parking
            markers.append(
                dl.CircleMarker(
                    center=[latitude, longitude],
                    radius=5,
                    color="#4CAF50",  # Green color for bicycle parking
                    fill=True,
                    fillColor="#4CAF50",
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


def format_bicycle_parking_display(bicycle_data):
    """
    Format the bicycle parking count display.
    
    Args:
        bicycle_data: Dictionary containing bicycle parking response from LTA API
    
    Returns:
        HTML Div with bicycle parking information
    """
    if not bicycle_data or 'value' not in bicycle_data:
        return html.Div(
            [
                html.P(
                    "Error loading bicycle parking data",
                    style={
                        "color": "#ff6b6b",
                        "textAlign": "center",
                        "fontSize": "0.75rem",
                    }
                )
            ]
        )

    parking_locations = bicycle_data.get('value', [])
    total_locations = len(parking_locations)
    
    # Calculate total rack count
    total_racks = sum(int(loc.get('RackCount', 0)) for loc in parking_locations if loc.get('RackCount'))
    
    # Count sheltered vs unsheltered
    sheltered_count = sum(1 for loc in parking_locations if loc.get('ShelterIndicator') == 'Y')
    unsheltered_count = total_locations - sheltered_count
    
    # Count by rack type
    rack_types = {}
    for loc in parking_locations:
        rack_type = loc.get('RackType', 'Unknown')
        rack_types[rack_type] = rack_types.get(rack_type, 0) + 1

    return html.Div(
        [
            html.Div(
                [
                    html.Span(
                        "🚴",
                        style={"fontSize": "2rem", "marginRight": "0.625rem", "lineHeight": "1"}
                    ),
                    html.Span(
                        f"{total_locations}",
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
                "Bicycle Parking Locations",
                style={
                    "color": "#fff",
                    "textAlign": "center",
                    "fontSize": "0.875rem",
                    "fontWeight": "600",
                    "margin": "0 0 0.625rem 0",
                }
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                f"Total Racks: {total_racks:,}",
                                style={
                                    "color": "#4CAF50",
                                    "fontSize": "0.8125rem",
                                    "fontWeight": "600",
                                }
                            ),
                        ],
                        style={
                            "marginBottom": "0.5rem",
                            "textAlign": "center",
                        }
                    ),
                    html.Div(
                        [
                            html.Span(
                                f"Sheltered: {sheltered_count}",
                                style={
                                    "color": "#fff",
                                    "fontSize": "0.75rem",
                                    "marginRight": "0.75rem",
                                }
                            ),
                            html.Span(
                                f"Unsheltered: {unsheltered_count}",
                                style={
                                    "color": "#fff",
                                    "fontSize": "0.75rem",
                                }
                            ),
                        ],
                        style={
                            "textAlign": "center",
                            "marginBottom": "0.5rem",
                        }
                    ),
                ],
                style={
                    "padding": "0.5rem",
                    "backgroundColor": "#3a4a5a",
                    "borderRadius": "0.25rem",
                    "marginBottom": "0.625rem",
                }
            ),
            html.P(
                f"Data within 50km radius of Singapore center",
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
            text = "Hide Taxi Location & Stands"
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
            text = "Show Taxi Location & Stands"
        
        return new_state, style, text
    
    @app.callback(
        [Output('taxi-markers', 'children'),
         Output('taxi-count-value', 'children'),
         Output('taxi-legend', 'style')],
        [Input('taxi-toggle-state', 'data'),
         Input('transport-interval', 'n_intervals')]
    )
    def update_taxi_display(show_taxis, n_intervals):
        """Update taxi locations and stands markers and count display."""
        _ = n_intervals  # Used for periodic refresh
        
        # Always fetch data to display counts
        taxi_data = fetch_taxi_availability()
        taxi_stands_data = fetch_taxi_stands_data()
        
        # Extract count values (always calculate)
        taxi_count = 0
        if taxi_data and 'features' in taxi_data:
            features = taxi_data.get('features', [])
            if features:
                first_feature = features[0]
                properties = first_feature.get('properties', {})
                taxi_count = properties.get('taxi_count', 0)
        
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
        
        # Format as "taxi/taxi stands"
        count_value = html.Div(
            html.Span(f"{taxi_count:,}/{stands_count}", style={"color": "#fff"}),
            style={
                "backgroundColor": "rgb(58, 74, 90)",
                "padding": "4px 8px",
                "borderRadius": "4px",
            }
        )
        
        # Legend style - show when toggle is on
        legend_style = {
            "position": "absolute",
            "top": "10px",
            "right": "10px",
            "backgroundColor": "rgba(26, 42, 58, 0.9)",
            "borderRadius": "8px",
            "padding": "10px",
            "zIndex": "1000",
            "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.3)",
            "display": "block" if show_taxis else "none",
        }
        
        # Only show markers if toggle is on
        if not show_taxis:
            return [], count_value, legend_style
        
        # Create markers for both
        taxi_markers = create_taxi_markers(taxi_data)
        taxi_stands_markers = create_taxi_stands_markers(taxi_stands_data)
        
        # Combine all markers
        all_markers = taxi_markers + taxi_stands_markers
        
        return all_markers, count_value, legend_style

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
            text = "Hide Traffic Cameras Location"
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
            text = "Show Traffic Cameras Location"
        
        return new_state, style, text

    @app.callback(
        [Output('cctv-markers', 'children'),
         Output('cctv-count-value', 'children')],
        [Input('cctv-toggle-state', 'data'),
         Input('transport-interval', 'n_intervals')]
    )
    def update_cctv_display(show_cctv, n_intervals):
        """Update CCTV markers and count display."""
        _ = n_intervals  # Used for periodic refresh
        
        # Always fetch data to display counts
        data = fetch_traffic_cameras()
        camera_data = parse_traffic_camera_data(data)
        
        # Extract count (always calculate)
        camera_count = len(camera_data) if camera_data else 0
        count_value = html.Div(
            html.Span(f"{camera_count}", style={"color": "#fff"}),
            style={
                "backgroundColor": "rgb(58, 74, 90)",
                "padding": "4px 8px",
                "borderRadius": "4px",
            }
        )
        
        # Only show markers if toggle is on
        if not show_cctv:
            return [], count_value
        
        # Create markers
        markers = create_cctv_markers(camera_data)
        
        return markers, count_value

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
            text = "Hide ERP Gantries Location"
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
            text = "Show ERP Gantries Location"

        return new_state, style, text

    @app.callback(
        [Output('erp-markers', 'children'),
         Output('erp-count-value', 'children')],
        [Input('erp-toggle-state', 'data'),
         Input('transport-interval', 'n_intervals')]
    )
    def update_erp_display(show_erp, n_intervals):
        """Update ERP gantry markers and count display."""
        _ = n_intervals  # Used for periodic refresh

        # Always fetch data to display counts
        geojson_data = fetch_erp_gantry_data()
        gantry_data = parse_erp_gantry_data(geojson_data)
        
        # Extract count (always calculate)
        gantry_count = len(gantry_data) if gantry_data else 0
        count_value = html.Div(
            html.Span(f"{gantry_count}", style={"color": "#fff"}),
            style={
                "backgroundColor": "rgb(58, 74, 90)",
                "padding": "4px 8px",
                "borderRadius": "4px",
            }
        )

        # Only show markers if toggle is on
        if not show_erp:
            return [], count_value

        # Create markers
        markers = create_erp_gantry_markers(gantry_data)

        return markers, count_value

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
            text = "Hide Traffic Speed Bands"
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
            text = "Show Traffic Speed Bands"

        return new_state, style, text

    @app.callback(
        [Output('speed-band-markers', 'children'),
         Output('speed-band-count-value', 'children')],
        [Input('speed-band-toggle-state', 'data'),
         Input('transport-interval', 'n_intervals')]
    )
    def update_speed_band_display(show_speed_band, n_intervals):
        """Update Speed Band markers and information display."""
        _ = n_intervals  # Used for periodic refresh

        # Always fetch data to display counts
        data = fetch_speed_band_data()
        
        # Calculate average speed band value (always calculate)
        items = data.get('value', []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        if items:
            band_values = []
            for item in items:
                try:
                    band = item.get('SpeedBand', '0')
                    if band and str(band).isdigit():
                        band_int = int(band)
                        if 1 <= band_int <= 8:
                            band_values.append(band_int)
                except (ValueError, TypeError):
                    continue
            
            if band_values:
                # Calculate average speed using midpoint of each range
                speed_midpoints = []
                for band in band_values:
                    midpoint = get_speed_midpoint(band)
                    if midpoint > 0:  # Only add valid midpoints
                        speed_midpoints.append(midpoint)
                
                if speed_midpoints:
                    avg_speed = sum(speed_midpoints) / len(speed_midpoints)
                else:
                    avg_speed = 0
                
                # Display average speed rounded to nearest integer
                count_value = html.Div(
                    html.Span(f"{int(round(avg_speed))} km/h", style={"color": "#fff"}),
                    style={
                        "backgroundColor": "rgb(58, 74, 90)",
                        "padding": "4px 8px",
                        "borderRadius": "4px",
                    }
                )
            else:
                count_value = html.Div(
                    html.Span("--", style={"color": "#999"}),
                    style={
                        "backgroundColor": "rgb(58, 74, 90)",
                        "padding": "4px 8px",
                        "borderRadius": "4px",
                    }
                )
        else:
            count_value = html.Div(
                html.Span("--", style={"color": "#999"}),
                style={
                    "backgroundColor": "rgb(58, 74, 90)",
                    "padding": "4px 8px",
                    "borderRadius": "4px",
                }
            )

        # Only show markers if toggle is on
        if not show_speed_band:
            return [], count_value

        # Create markers
        markers = create_speed_band_markers(data)

        return markers, count_value

    @app.callback(
        [Output('traffic-incidents-toggle-state', 'data'),
         Output('traffic-incidents-toggle-btn', 'style'),
         Output('traffic-incidents-toggle-btn', 'children')],
        Input('traffic-incidents-toggle-btn', 'n_clicks'),
        State('traffic-incidents-toggle-state', 'data'),
        prevent_initial_call=True
    )
    def toggle_traffic_incidents_display(_n_clicks, current_state):
        """Toggle Traffic Incidents markers display on/off."""
        new_state = not current_state

        if new_state:
            # Active state - orange background
            style = {
                "backgroundColor": "#FF9800",
                "border": "none",
                "borderRadius": "4px",
                "color": "#fff",
                "cursor": "pointer",
                "padding": "6px 12px",
                "fontSize": "12px",
                "fontWeight": "600",
            }
            text = "Hide Traffic Incidents"
        else:
            # Inactive state - outline
            style = {
                "backgroundColor": "transparent",
                "border": "2px solid #FF9800",
                "borderRadius": "4px",
                "color": "#FF9800",
                "cursor": "pointer",
                "padding": "4px 10px",
                "fontSize": "12px",
                "fontWeight": "600",
            }
            text = "Show Traffic Incidents"

        return new_state, style, text

    @app.callback(
        [Output('traffic-incidents-markers', 'children'),
         Output('traffic-incidents-count-value', 'children')],
        [Input('traffic-incidents-toggle-state', 'data'),
         Input('transport-interval', 'n_intervals')]
    )
    def update_traffic_incidents_display(show_incidents, n_intervals):
        """Update Traffic Incidents markers and count display."""
        _ = n_intervals  # Used for periodic refresh

        # Always fetch data to display counts
        incidents_data = fetch_traffic_incidents_data()
        faulty_lights_data = fetch_faulty_traffic_lights_data()
        
        # Extract count (always calculate)
        incidents = []
        if isinstance(incidents_data, dict):
            if "value" in incidents_data:
                incidents = incidents_data.get("value", [])
            elif isinstance(incidents_data, list):
                incidents = incidents_data
        elif isinstance(incidents_data, list):
            incidents = incidents_data
        
        faulty_lights = []
        if faulty_lights_data:
            if isinstance(faulty_lights_data, dict):
                if "value" in faulty_lights_data:
                    faulty_lights = faulty_lights_data.get("value", [])
                elif isinstance(faulty_lights_data, list):
                    faulty_lights = faulty_lights_data
            elif isinstance(faulty_lights_data, list):
                faulty_lights = faulty_lights_data
        
        total_count = len(incidents) + len(faulty_lights)
        count_value = html.Div(
            html.Span(f"{total_count}", style={"color": "#fff"}),
            style={
                "backgroundColor": "rgb(58, 74, 90)",
                "padding": "4px 8px",
                "borderRadius": "4px",
            }
        )

        # Only show markers if toggle is on
        if not show_incidents:
            return [], count_value

        # Create markers
        markers = create_traffic_incidents_markers(incidents_data, faulty_lights_data)

        return markers, count_value

    @app.callback(
        [Output('bicycle-parking-toggle-state', 'data'),
         Output('bicycle-parking-toggle-btn', 'style'),
         Output('bicycle-parking-toggle-btn', 'children')],
        Input('bicycle-parking-toggle-btn', 'n_clicks'),
        State('bicycle-parking-toggle-state', 'data'),
        prevent_initial_call=True
    )
    def toggle_bicycle_parking_display(_n_clicks, current_state):
        """Toggle bicycle parking markers display on/off."""
        new_state = not current_state
        
        if new_state:
            # Active state - purple background
            style = {
                "backgroundColor": "#9C27B0",
                "border": "none",
                "borderRadius": "4px",
                "color": "#fff",
                "cursor": "pointer",
                "padding": "6px 12px",
                "fontSize": "12px",
                "fontWeight": "600",
            }
            text = "Hide Bicycle Parking Locations"
        else:
            # Inactive state - outline
            style = {
                "backgroundColor": "transparent",
                "border": "2px solid #9C27B0",
                "borderRadius": "4px",
                "color": "#9C27B0",
                "cursor": "pointer",
                "padding": "4px 10px",
                "fontSize": "12px",
                "fontWeight": "600",
            }
            text = "Show Bicycle Parking Locations"
        
        return new_state, style, text

    @app.callback(
        [Output('bicycle-parking-markers', 'children'),
         Output('bicycle-parking-count-value', 'children')],
        [Input('bicycle-parking-toggle-state', 'data'),
         Input('transport-interval', 'n_intervals')]
    )
    def update_bicycle_parking_display(show_bicycle_parking, n_intervals):
        """Update bicycle parking markers and count display."""
        _ = n_intervals  # Used for periodic refresh
        
        # Always fetch data to display counts
        data = fetch_bicycle_parking_data()
        
        if not data or 'value' not in data:
            count_value = html.Div(
                html.Span("--/--", style={"color": "#999"}),
                style={
                    "backgroundColor": "rgb(58, 74, 90)",
                    "padding": "4px 8px",
                    "borderRadius": "4px",
                }
            )
            return [], count_value
        
        parking_locations = data.get('value', [])
        
        # Count sheltered vs unsheltered
        sheltered_count = sum(1 for loc in parking_locations if loc.get('ShelterIndicator') == 'Y')
        unsheltered_count = len(parking_locations) - sheltered_count
        
        # Format as "sheltered/unsheltered"
        count_value = html.Div(
            html.Span(f"{sheltered_count}/{unsheltered_count}", style={"color": "#fff"}),
            style={
                "backgroundColor": "rgb(58, 74, 90)",
                "padding": "4px 8px",
                "borderRadius": "4px",
            }
        )
        
        # Only show markers if toggle is on
        if not show_bicycle_parking:
            return [], count_value
        
        # Create markers
        markers = create_bicycle_parking_markers(data)
        
        return markers, count_value

    # Callback for nearby transport page - bicycle parking
    @app.callback(
        [Output('nearby-transport-bicycle-content', 'children'),
         Output('nearby-bicycle-markers', 'children')],
        Input('nearby-transport-location-store', 'data')
    )
    def update_nearby_transport_bicycle_parking(location_data):
        """
        Update bicycle parking display for nearby transport page based on selected location.
        Shows bicycle parking within 500m of the selected location.
        
        Args:
            location_data: Dictionary containing {'lat': float, 'lon': float} of selected location
        
        Returns:
            HTML Div containing bicycle parking information and markers
        """
        if not location_data:
            return html.P(
                "Select a location to view nearest bicycle parking",
                style={
                    "textAlign": "center",
                    "padding": "15px",
                    "color": "#999",
                    "fontSize": "12px",
                    "fontStyle": "italic"
                }
            ), []

        try:
            center_lat = float(location_data.get('lat'))
            center_lon = float(location_data.get('lon'))
        except (ValueError, TypeError, KeyError):
            return html.Div(
                "Invalid coordinates",
                style={
                    "padding": "10px",
                    "color": "#ff6b6b",
                    "fontSize": "12px",
                    "textAlign": "center"
                }
            ), []

        # Fetch nearby bicycle parking within 500m
        print(f"Searching for bicycle parking near ({center_lat}, {center_lon}) for nearby transport page")
        nearby_parking = fetch_nearby_bicycle_parking(center_lat, center_lon, radius_m=500)
        print(f"Found {len(nearby_parking)} bicycle parking locations within 500m")

        if not nearby_parking:
            return html.P(
                "No bicycle parking found within 500m",
                style={
                    "textAlign": "center",
                    "padding": "15px",
                    "color": "#999",
                    "fontSize": "12px",
                    "fontStyle": "italic"
                }
            ), []

        # Create markers for map
        markers = create_nearby_bicycle_parking_markers(nearby_parking)

        # Build display components for each nearby bicycle parking
        parking_items = []

        for parking in nearby_parking:
            description = parking.get('description', 'N/A')
            rack_type = parking.get('rack_type', 'N/A')
            rack_count = parking.get('rack_count', 'N/A')
            distance_m = parking.get('distance_m', 0)

            # Format distance display
            if distance_m < 1000:
                distance_str = f"{int(distance_m)}m"
            else:
                distance_str = f"{distance_m/1000:.2f}km"

            # Create card for each bicycle parking location
            parking_items.append(
                html.Div(
                    [
                        html.Div(
                            description,
                            style={
                                "fontSize": "13px",
                                "color": "#fff",
                                "fontWeight": "600",
                                "marginBottom": "4px"
                            }
                        ),
                        html.Div(
                            f"RackType: {rack_type}",
                            style={
                                "fontSize": "12px",
                                "color": "#ccc",
                                "marginBottom": "2px"
                            }
                        ),
                        html.Div(
                            f"RackCount: {rack_count}",
                            style={
                                "fontSize": "12px",
                                "color": "#ccc",
                                "marginBottom": "4px"
                            }
                        ),
                        html.Div(
                            f"Distance: {distance_str}",
                            style={
                                "fontSize": "12px",
                                "color": "#60a5fa",
                                "fontWeight": "500"
                            }
                        )
                    ],
                    style={
                        "padding": "10px 12px",
                        "borderBottom": "1px solid #444",
                        "marginBottom": "6px",
                        "backgroundColor": "#1a1a1a",
                        "borderRadius": "4px"
                    }
                )
            )

        # Return all parking items and markers
        return parking_items, markers


