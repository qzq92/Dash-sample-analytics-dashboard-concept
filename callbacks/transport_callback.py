"""
Callback functions for handling transport information.
References:
- Taxi: https://api.data.gov.sg/v1/transport/taxi-availability
- Traffic Cameras: https://api.data.gov.sg/v1/transport/traffic-images
- ERP Gantries: https://data.gov.sg/datasets/d_753090823cc9920ac41efaa6530c5893/view
- PUB CCTV: https://data.gov.sg/datasets/d_1de1c45043183bec57e762d01c636eee/view
"""
import re
from dash import Input, Output, State, html
import dash_leaflet as dl
from utils.async_fetcher import fetch_url
from utils.data_download_helper import fetch_erp_gantry_data, fetch_pub_cctv_data

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


def extract_cctv_info(description_html):
    """
    Extract CCTV information from HTML description field.
    
    Args:
        description_html: HTML string containing CCTV attributes
    
    Returns:
        Dictionary with CCTV information (cctv_id, catchment, ref_name, hyperlink)
    """
    if not description_html:
        return {
            'cctv_id': 'Unknown',
            'catchment': 'Unknown',
            'ref_name': 'Unknown',
            'hyperlink': None
        }

    info = {
        'cctv_id': 'Unknown',
        'catchment': 'Unknown',
        'ref_name': 'Unknown',
        'hyperlink': None
    }

    # Extract CCTVID
    match = re.search(r'<th>CCTVID</th>\s*<td>([^<]*)</td>', description_html)
    if match:
        info['cctv_id'] = match.group(1).strip()

    # Extract CATCHMENT
    match = re.search(r'<th>CATCHMENT</th>\s*<td>([^<]*)</td>', description_html)
    if match:
        info['catchment'] = match.group(1).strip()

    # Extract REF_NAME
    match = re.search(r'<th>REF_NAME</th>\s*<td>([^<]*)</td>', description_html)
    if match:
        info['ref_name'] = match.group(1).strip()

    # Extract HYPERLINK
    match = re.search(r'<th>HYPERLINK</th>\s*<td>([^<]*)</td>', description_html)
    if match:
        info['hyperlink'] = match.group(1).strip()

    return info


def parse_pub_cctv_data(geojson_data):
    """
    Parse PUB CCTV GeoJSON data.
    
    Args:
        geojson_data: GeoJSON FeatureCollection
    
    Returns:
        List of dictionaries with CCTV information
    """
    cctvs = []

    if not geojson_data or 'features' not in geojson_data:
        return cctvs

    features = geojson_data.get('features', [])

    for feature in features:
        properties = feature.get('properties', {})
        geometry = feature.get('geometry', {})

        if geometry.get('type') != 'Point':
            continue

        coordinates = geometry.get('coordinates', [])
        if len(coordinates) < 2:
            continue

        # Extract CCTV info from description
        description = properties.get('Description', '')
        cctv_info = extract_cctv_info(description)
        unique_id = properties.get('Name', '')

        # Point coordinates are [lon, lat, z] in GeoJSON, convert to [lat, lon] for Leaflet
        lon, lat = coordinates[0], coordinates[1]

        cctvs.append({
            'cctv_id': cctv_info['cctv_id'],
            'catchment': cctv_info['catchment'],
            'ref_name': cctv_info['ref_name'],
            'hyperlink': cctv_info['hyperlink'],
            'unique_id': unique_id,
            'coordinates': [lat, lon],
            'description': description,
        })

    return cctvs


def create_pub_cctv_markers(cctv_data):
    """
    Create map markers for PUB CCTV locations.
    
    Args:
        cctv_data: List of CCTV dictionaries
    
    Returns:
        List of dl.CircleMarker components
    """
    markers = []

    for cctv in cctv_data:
        coords = cctv.get('coordinates', [])
        cctv_id = cctv.get('cctv_id', 'Unknown')
        ref_name = cctv.get('ref_name', 'Unknown')
        catchment = cctv.get('catchment', 'Unknown')

        if not coords or len(coords) < 2:
            continue

        # Create tooltip text
        tooltip_text = f"PUB CCTV {cctv_id}"
        if ref_name and ref_name != 'Unknown':
            tooltip_text += f"\n{ref_name}"
        if catchment and catchment != 'Unknown':
            tooltip_text += f"\nCatchment: {catchment}"

        # Create circle marker for CCTV location
        markers.append(
            dl.CircleMarker(
                center=coords,
                radius=6,
                color="#00BCD4",
                fill=True,
                fillColor="#00BCD4",
                fillOpacity=0.7,
                weight=2,
                children=[
                    dl.Tooltip(tooltip_text),
                ]
            )
        )

    return markers


def format_pub_cctv_count_display(cctv_data):
    """
    Format the PUB CCTV count display.
    
    Args:
        cctv_data: List of CCTV dictionaries
    
    Returns:
        HTML Div with CCTV count information
    """
    if not cctv_data:
        return html.Div(
            [
                html.P(
                    "Error loading PUB CCTV data",
                    style={
                        "color": "#ff6b6b",
                        "textAlign": "center",
                        "padding": "1.25rem",
                        "fontSize": "0.75rem",
                    }
                )
            ]
        )

    count = len(cctv_data)
    return html.Div(
        [
            html.P(
                f"Total CCTV locations: {count}",
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

    @app.callback(
        [Output('pub-cctv-toggle-state', 'data'),
         Output('pub-cctv-toggle-btn', 'style'),
         Output('pub-cctv-toggle-btn', 'children')],
        Input('pub-cctv-toggle-btn', 'n_clicks'),
        State('pub-cctv-toggle-state', 'data'),
        prevent_initial_call=True
    )
    def toggle_pub_cctv_display(_n_clicks, current_state):
        """Toggle PUB CCTV markers display on/off."""
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
        [Output('pub-cctv-markers', 'children'),
         Output('pub-cctv-count-display', 'children')],
        [Input('pub-cctv-toggle-state', 'data'),
         Input('transport-interval', 'n_intervals')]
    )
    def update_pub_cctv_display(show_pub_cctv, n_intervals):
        """Update PUB CCTV markers and count display."""
        _ = n_intervals  # Used for periodic refresh

        if not show_pub_cctv:
            # Return empty markers and default message
            return [], html.P(
                "Click 'Show on Map' to load CCTV locations",
                style={
                    "color": "#999",
                    "textAlign": "center",
                    "padding": "20px",
                    "fontStyle": "italic",
                    "fontSize": "12px",
                }
            )

        # Fetch CCTV data
        geojson_data = fetch_pub_cctv_data()
        cctv_data = parse_pub_cctv_data(geojson_data)

        # Create markers and count display
        markers = create_pub_cctv_markers(cctv_data)
        count_display = format_pub_cctv_count_display(cctv_data)

        return markers, count_display

