"""
Callback functions for handling transport information.
References:
- Taxi: https://api.data.gov.sg/v1/transport/taxi-availability
- Traffic Cameras: https://api.data.gov.sg/v1/transport/traffic-images
- ERP Gantries: https://data.gov.sg/datasets/d_753090823cc9920ac41efaa6530c5893/view
"""
import re
from dash import Input, Output, State, html
import dash_leaflet as dl
from utils.async_fetcher import fetch_url

# API URLs
TAXI_API_URL = "https://api.data.gov.sg/v1/transport/taxi-availability"
TRAFFIC_IMAGES_API_URL = "https://api.data.gov.sg/v1/transport/traffic-images"
ERP_GANTRY_DATASET_ID = "d_753090823cc9920ac41efaa6530c5893"
# ERP_GANTRY_API_URL uses initiate-download endpoint to get download URL
ERP_GANTRY_API_URL = (
    f"https://api-open.data.gov.sg/v1/public/api/datasets/"
    f"{ERP_GANTRY_DATASET_ID}/initiate-download"
)

# Cache for ERP gantry data (static dataset downloaded from S3, cache for 24 hours)
_erp_gantry_cache = {'data': None, 'timestamp': 0}
ERP_GANTRY_CACHE_TTL = 24 * 60 * 60  # 24 hours in seconds


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
            
            # Create small circle marker for each taxi
            markers.append(
                dl.CircleMarker(
                    center=[lat, lon],
                    radius=3,
                    color="#FFD700",
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
                        "fontSize": "12px",
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
                        "fontSize": "12px",
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
            from datetime import datetime
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
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
                        style={"fontSize": "32px", "marginRight": "10px"}
                    ),
                    html.Span(
                        f"{taxi_count:,}",
                        style={
                            "fontSize": "48px",
                            "fontWeight": "bold",
                            "color": "#FFD700",
                        }
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "marginBottom": "10px",
                }
            ),
            html.P(
                "Available Taxis",
                style={
                    "color": "#fff",
                    "textAlign": "center",
                    "fontSize": "14px",
                    "fontWeight": "600",
                    "margin": "0 0 10px 0",
                }
            ),
            html.P(
                f"Last updated: {formatted_time}",
                style={
                    "color": "#888",
                    "textAlign": "center",
                    "fontSize": "11px",
                    "fontStyle": "italic",
                    "margin": "0",
                }
            ),
        ],
        style={
            "padding": "15px",
            "backgroundColor": "#2c3e50",
            "borderRadius": "8px",
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
        
        if lat is None or lon is None:
            continue

        markers.append(
            dl.Marker(
                position=[lat, lon],
                children=[
                    dl.Tooltip(f"Camera {camera_id}"),
                    dl.Popup(
                        children=html.Div(
                            [
                                html.Strong(
                                    f"Camera {camera_id}",
                                    style={"fontSize": "14px"}
                                ),
                                html.Br(),
                                html.Img(
                                    src=image_url,
                                    style={
                                        "width": "280px",
                                        "height": "auto",
                                        "marginTop": "8px",
                                        "borderRadius": "4px",
                                    }
                                ),
                            ],
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
                        "fontSize": "12px",
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
            from datetime import datetime
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
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
                        style={"fontSize": "32px", "marginRight": "10px"}
                    ),
                    html.Span(
                        f"{camera_count}",
                        style={
                            "fontSize": "48px",
                            "fontWeight": "bold",
                            "color": "#4CAF50",
                        }
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "marginBottom": "10px",
                }
            ),
            html.P(
                "Traffic Cameras",
                style={
                    "color": "#fff",
                    "textAlign": "center",
                    "fontSize": "14px",
                    "fontWeight": "600",
                    "margin": "0 0 10px 0",
                }
            ),
            html.P(
                f"Last updated: {formatted_time}",
                style={
                    "color": "#888",
                    "textAlign": "center",
                    "fontSize": "11px",
                    "fontStyle": "italic",
                    "margin": "0",
                }
            ),
            html.P(
                "Click markers on map to view live feed",
                style={
                    "color": "#4CAF50",
                    "textAlign": "center",
                    "fontSize": "10px",
                    "margin": "10px 0 0 0",
                }
            ),
        ],
        style={
            "padding": "15px",
            "backgroundColor": "#2c3e50",
            "borderRadius": "8px",
        }
    )


def fetch_erp_gantry_data():
    """
    Fetch ERP gantry GeoJSON data using initiate-download API endpoint.
    
    The initiate-download endpoint returns a download URL which is then used to fetch
    the actual GeoJSON file. Since this is a static dataset, the data is cached for
    24 hours to avoid redundant downloads.
    
    Returns:
        Dictionary containing GeoJSON data or None if error
    """
    import time
    global _erp_gantry_cache

    current_time = time.time()

    # Check if cache is valid (24 hours)
    if (_erp_gantry_cache['data'] is not None and
            current_time - _erp_gantry_cache['timestamp'] < ERP_GANTRY_CACHE_TTL):
        print("Using cached ERP gantry data")
        return _erp_gantry_cache['data']

    # Step 1: Call initiate-download to get download URL
    print(f"Initiating ERP gantry download: {ERP_GANTRY_API_URL}")
    init_response = fetch_url(ERP_GANTRY_API_URL)
    
    
    if init_response.get('code') != 0:
        error_msg = init_response.get('errorMsg', 'Unknown error')
        print(f"Failed to initiate ERP gantry download: {error_msg}")
        return None

    # Extract URL from response structure: {"code": 0, "data": {"url": "..."}}
    data = init_response.get('data', {})
    download_url = data.get('url')
    
    if not download_url:
        print("No download URL in initiate-download response")
        print(f"Response data: {data}")
        return None

    print(f"Download URL extracted successfully: {download_url[:80]}...")
    print(f"Downloading ERP gantry GeoJSON from: {download_url[:80]}...")

    # Step 2: Fetch the actual GeoJSON file from the extracted download URL
    geojson_data = fetch_url(download_url)
    
    if not geojson_data:
        print("Failed to download ERP gantry GeoJSON data from URL")
        return None
    
    print("Successfully downloaded ERP gantry GeoJSON data")

    # Update cache if successful
    if geojson_data is not None:
        _erp_gantry_cache['data'] = geojson_data
        _erp_gantry_cache['timestamp'] = current_time
        print("ERP gantry data cached successfully")

    return geojson_data


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
                        "fontSize": "12px",
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
                        style={"fontSize": "32px", "marginRight": "10px"}
                    ),
                    html.Span(
                        f"{gantry_count}",
                        style={
                            "fontSize": "48px",
                            "fontWeight": "bold",
                            "color": "#FF6B6B",
                        }
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "marginBottom": "10px",
                }
            ),
            html.P(
                "ERP Gantries",
                style={
                    "color": "#fff",
                    "textAlign": "center",
                    "fontSize": "14px",
                    "fontWeight": "600",
                    "margin": "0 0 10px 0",
                }
            ),
            html.P(
                "Red lines show gantry locations",
                style={
                    "color": "#888",
                    "textAlign": "center",
                    "fontSize": "11px",
                    "fontStyle": "italic",
                    "margin": "0",
                }
            ),
        ],
        style={
            "padding": "15px",
            "backgroundColor": "#2c3e50",
            "borderRadius": "8px",
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
        """Update taxi markers and count display."""
        _ = n_intervals  # Used for periodic refresh
        
        if not show_taxis:
            # Return empty markers and default message
            return [], html.P(
                "Click 'Show on Map' to load taxi locations",
                style={
                    "color": "#999",
                    "textAlign": "center",
                    "padding": "20px",
                    "fontStyle": "italic",
                    "fontSize": "12px",
                }
            )
        
        # Fetch taxi data
        data = fetch_taxi_availability()
        
        # Create markers and count display
        markers = create_taxi_markers(data)
        count_display = format_taxi_count_display(data)
        
        return markers, count_display

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

