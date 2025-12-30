"""
Callback functions for handling speed band information on the "Speed band on the roads" tab.
"""
import os
import math
import time
import threading
from typing import Optional, Dict, List, Any, Tuple
from concurrent.futures import Future
from dash import Input, Output, html
import dash_leaflet as dl
import requests

# API URL
SPEED_BAND_URL = "https://datamall2.mytransport.sg/ltaodataservice/v4/TrafficSpeedBands"

# In-memory cache for speed band data with timestamp
_speed_band_cache: Dict[str, Any] = {
    'data': None,
    'last_bucket': 0  # Unix timestamp of the 5-minute bucket
}
_cache_lock = threading.Lock()
_last_active_tab: Optional[str] = None  # Track last active tab to detect tab switches

# Zoom level thresholds (max zoom is 19, show at 17-18)
MIN_ZOOM_FOR_DISPLAY = 17
MAX_POINTS_TO_DISPLAY = 3000


def fetch_url_with_retry(url: str, headers: Dict[str, str], timeout: int = 10, max_retries: int = 3) -> Optional[dict]:
    """
    Fetch data from a URL with exponential backoff retry starting at 10 seconds.
    Specifically for speed band API calls which may need more robust retry handling.
    
    Args:
        url: The URL to fetch
        headers: Headers dict for the request
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts (default: 3)
    
    Returns:
        JSON response as dict, or None if error
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            
            # Accept any 2xx status code as success
            if 200 <= response.status_code < 300:
                return response.json()
            
            # Check for 5XX server errors (500-599)
            if 500 <= response.status_code < 600:
                if attempt < max_retries - 1:
                    # Exponential backoff starting at 10 seconds: 10s, 20s, 40s
                    wait_time = 10 * (2 ** attempt)
                    print(f"Speed band API request failed with {response.status_code}: {url} - retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                print(f"Speed band API request failed after {max_retries} attempts: {url} - status={response.status_code}")
                return None
            
            # For non-5XX errors (4XX client errors), don't retry
            print(f"Speed band API request failed: {url} - status={response.status_code}")
            return None
                
        except (requests.exceptions.RequestException, ValueError) as error:
            if attempt < max_retries - 1:
                # Exponential backoff starting at 10 seconds: 10s, 20s, 40s
                wait_time = 10 * (2 ** attempt)
                print(f"Error fetching speed band {url}: {error} - retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            print(f"Error fetching speed band {url} after {max_retries} attempts: {error}")
    
    return None


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.
    
    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point
    
    Returns:
        Distance in kilometers
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def fetch_speed_band_data() -> Optional[Dict[str, Any]]:
    """
    Fetch all Traffic Speed Band data from LTA DataMall API with optimized parallel pagination.
    Caches data for 5 minutes based on system time boundaries (0, 5, 10... mins).
    
    Returns:
        Dictionary containing all speed band data with combined 'value' list, or None if error
    """
    global _speed_band_cache
    
    # Calculate current 5-minute bucket start time (Unix timestamp)
    current_time = time.time()
    current_bucket = int(current_time // 300) * 300  # 300 seconds = 5 minutes
    
    # Return cached data if we're still in the same 5-minute bucket
    with _cache_lock:
        if (_speed_band_cache['data'] is not None and 
            _speed_band_cache['last_bucket'] == current_bucket):
            return _speed_band_cache['data']
    
    print(f"Refreshing speed band cache for bucket starting at {time.strftime('%H:%M:%S', time.localtime(current_bucket))}")
    
    api_key = os.getenv("LTA_API_KEY")
    
    if not api_key:
        print("Warning: LTA_API_KEY not found in environment variables")
        return None
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "AccountKey": api_key,
        "Content-Type": "application/json"
    }
    
    from utils.async_fetcher import _executor
    from concurrent.futures import as_completed
    
    all_speed_bands = []
    page_size = 500
    batch_size = 10000  # 20 pages per batch
    current_skip = 0
    
    while True:
        print(f"Fetching speed band batch starting at skip={current_skip}...")
        
        # Define skip values for this batch (e.g., [0, 500, ..., 4500])
        batch_skip_values = list(range(current_skip, current_skip + batch_size, page_size))
        
        # Create URLs for this batch
        batch_urls = []
        for skip in batch_skip_values:
            url = f"{SPEED_BAND_URL}?$skip={skip}" if skip > 0 else SPEED_BAND_URL
            batch_urls.append((url, skip))
        
        # Submit all batch requests to thread pool with custom retry logic
        batch_futures = {
            _executor.submit(fetch_url_with_retry, url, headers): skip
            for url, skip in batch_urls
        }
        
        # Collect results for this batch
        batch_results = {}
        for future in as_completed(batch_futures):
            skip = batch_futures[future]
            try:
                page_data = future.result()
                if page_data and 'value' in page_data:
                    batch_results[skip] = page_data.get('value', [])
                else:
                    batch_results[skip] = []
            except Exception as e:
                print(f"Error fetching speed bands (skip={skip}): {e}")
                batch_results[skip] = []
        
        # Combine results in order and determine if we should continue
        last_page_full = False
        batch_completed_normally = True
        
        for skip in sorted(batch_results.keys()):
            page_items = batch_results[skip]
            if not page_items:
                # Empty page means we've reached the end
                batch_completed_normally = False
                break
            
            # Pre-parse coordinates as floats to save time during map interactions
            for item in page_items:
                try:
                    item['_start_lat'] = float(item.get('StartLat', 0))
                    item['_start_lon'] = float(item.get('StartLon', 0))
                    item['_end_lat'] = float(item.get('EndLat', 0))
                    item['_end_lon'] = float(item.get('EndLon', 0))
                except (ValueError, TypeError):
                    item['_start_lat'] = 0.0
                    item['_start_lon'] = 0.0
                    item['_end_lat'] = 0.0
                    item['_end_lon'] = 0.0
                
            all_speed_bands.extend(page_items)
            print(f"Fetched {len(page_items)} speed bands (skip={skip}), total so far: {len(all_speed_bands)}")
            
            # Check if this was the last page of the batch and if it was full
            if skip == batch_skip_values[-1]:
                if len(page_items) == page_size:
                    last_page_full = True
            elif len(page_items) < page_size:
                # Reached end before batch finished
                batch_completed_normally = False
                break
        
        # If we reached the end of the data, stop
        if not batch_completed_normally or not last_page_full:
            break
            
        # Move to next batch
        current_skip += batch_size
    
    print(f"Total speed bands fetched: {len(all_speed_bands)}")
    
    # Prepare result
    result = {'value': all_speed_bands}
    
    # Update cache
    if all_speed_bands:
        with _cache_lock:
            _speed_band_cache['data'] = result
            _speed_band_cache['last_bucket'] = current_bucket
        print(f"Speed band cache updated for 5-minute bucket: {time.strftime('%H:%M:%S', time.localtime(current_bucket))}")
    
    return result


def fetch_speed_band_data_async() -> Optional[Future]:
    """
    Fetch all Traffic Speed Band data asynchronously with pagination (returns Future).
    The API returns 500 records per page. This function fetches all pages
    until less than 500 records are returned.
    Call .result() to get the data when needed.
    
    Returns:
        Future object that will contain all speed band data, or None if error
    """
    # Import executor from async_fetcher module
    from utils.async_fetcher import _executor
    
    # Submit the synchronous paginated function to thread pool
    return _executor.submit(fetch_speed_band_data)




def create_speed_band_markers(speed_data: Optional[Dict[str, Any]]) -> List[dl.Polyline]:
    """
    Create map polylines for Traffic Speed Band locations.
    
    Args:
        speed_data: Dictionary or list of speed band data
    
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
    items = speed_data.get('value', []) if isinstance(speed_data, dict) else (speed_data if isinstance(speed_data, list) else [])
    
    for item in items:
        try:
            # Use pre-parsed floats if available, otherwise fallback
            start_lat = item.get('_start_lat')
            start_lon = item.get('_start_lon')
            end_lat = item.get('_end_lat')
            end_lon = item.get('_end_lon')
            
            if start_lat is None:
                start_lat = float(item.get('StartLat', 0))
                start_lon = float(item.get('StartLon', 0))
                end_lat = float(item.get('EndLat', 0))
                end_lon = float(item.get('EndLon', 0))
            
            band = str(item.get('SpeedBand', '0'))
            
            if start_lat == 0 or end_lat == 0:
                continue
                
            color = band_colors.get(band, "#888888")
            
            markers.append(
                dl.Polyline(
                    positions=[[start_lat, start_lon], [end_lat, end_lon]],
                    color=color,
                    weight=5,
                    opacity=0.8,
                )
            )
        except (ValueError, TypeError):
            continue
            
    return markers


def format_speed_band_display() -> html.Div:
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


def calculate_viewport_bounds(center_lat: float, center_lon: float, zoom: int) -> Dict[str, float]:
    """
    Calculate viewport bounds based on center and zoom level.
    Approximation based on Web Mercator projection.
    
    Args:
        center_lat: Latitude of viewport center
        center_lon: Longitude of viewport center
        zoom: Current zoom level
    
    Returns:
        Dictionary with 'north', 'south', 'east', 'west' bounds
    """
    # Approximate viewport size in degrees
    # At zoom level z, the world is 256 * 2^z pixels wide
    # Assuming viewport is ~800 pixels wide and ~600 pixels tall
    viewport_width_pixels = 800
    viewport_height_pixels = 600
    
    # Degrees per pixel at this zoom level (at equator)
    degrees_per_pixel = 360 / (256 * (2 ** zoom))
    
    # Calculate lat/lon offsets (rough approximation)
    # Adjust for latitude (mercator distortion)
    lat_offset = (viewport_height_pixels / 2) * degrees_per_pixel
    lon_offset = (viewport_width_pixels / 2) * degrees_per_pixel / math.cos(math.radians(center_lat))
    
    bounds = {
        'north': center_lat + lat_offset,
        'south': center_lat - lat_offset,
        'east': center_lon + lon_offset,
        'west': center_lon - lon_offset
    }
    
    return bounds


def is_in_viewport(start_lat: float, start_lon: float, end_lat: float, end_lon: float, bounds: Dict[str, float]) -> bool:
    """
    Check if a speed band segment is within viewport bounds.
    Returns True if either start or end point is within bounds.
    
    Args:
        start_lat: Start latitude
        start_lon: Start longitude
        end_lat: End latitude
        end_lon: End longitude
        bounds: Dictionary with 'north', 'south', 'east', 'west'
    
    Returns:
        True if segment is within viewport
    """
    # Check if start point is in viewport
    start_in = (bounds['south'] <= start_lat <= bounds['north'] and 
                bounds['west'] <= start_lon <= bounds['east'])
    
    # Check if end point is in viewport
    end_in = (bounds['south'] <= end_lat <= bounds['north'] and 
              bounds['west'] <= end_lon <= bounds['east'])
    
    # Return True if either point is in viewport
    return start_in or end_in


def filter_speed_bands_by_viewport(speed_data: Optional[Dict[str, Any]], center_lat: float, center_lon: float, zoom: int) -> List[Dict[str, Any]]:
    """
    Filter speed band data by viewport bounds.
    Only returns segments within viewport, up to MAX_POINTS_TO_DISPLAY.
    
    Args:
        speed_data: Dictionary containing speed band data
        center_lat: Latitude of viewport center
        center_lon: Longitude of viewport center
        zoom: Current zoom level
    
    Returns:
        List of filtered speed band items within viewport
    """
    if not speed_data:
        return []
    
    items = speed_data.get('value', []) if isinstance(speed_data, dict) else []
    if not items:
        return []
    
    # Calculate viewport bounds
    bounds = calculate_viewport_bounds(center_lat, center_lon, zoom)
    
    # Print viewport endpoints
    print(f"Viewport bounds at zoom {zoom}:")
    print(f"  North: {bounds['north']:.6f}, South: {bounds['south']:.6f}")
    print(f"  East: {bounds['east']:.6f}, West: {bounds['west']:.6f}")
    
    # Filter items that are within viewport
    filtered_items = []
    for item in items:
        try:
            # Use pre-parsed floats if available, otherwise fallback
            start_lat = item.get('_start_lat')
            start_lon = item.get('_start_lon')
            end_lat = item.get('_end_lat')
            end_lon = item.get('_end_lon')
            
            if start_lat is None:
                start_lat = float(item.get('StartLat', 0))
                start_lon = float(item.get('StartLon', 0))
                end_lat = float(item.get('EndLat', 0))
                end_lon = float(item.get('EndLon', 0))
            
            if start_lat == 0 or end_lat == 0:
                continue
            
            # Check if segment is within viewport
            if is_in_viewport(start_lat, start_lon, end_lat, end_lon, bounds):
                filtered_items.append(item)
                
                # Stop if we've reached max points
                if len(filtered_items) >= MAX_POINTS_TO_DISPLAY:
                    break
                    
        except (ValueError, TypeError):
            continue
    
    print(f"Filtered to {len(filtered_items)} speed bands within viewport (max: {MAX_POINTS_TO_DISPLAY})")
    return filtered_items


def parse_coordinates(coords: Any) -> Tuple[Optional[float], Optional[float]]:
    """
    Parse coordinates from various formats (list, tuple, dict).
    
    Returns:
        Tuple of (lat, lon) or (None, None)
    """
    if coords is None:
        return None, None
    
    # Handle dict format {'lat': 1.23, 'lng': 103.45} or {'lat': 1.23, 'lon': 103.45}
    if isinstance(coords, dict):
        lat = coords.get('lat')
        lon = coords.get('lng') or coords.get('lon')
        try:
            return float(lat) if lat is not None else None, float(lon) if lon is not None else None
        except (ValueError, TypeError):
            return None, None
            
    # Handle list/tuple format [1.23, 103.45]
    if isinstance(coords, (list, tuple)) and len(coords) >= 2:
        try:
            return float(coords[0]), float(coords[1])
        except (ValueError, TypeError):
            return None, None
            
    return None, None


def register_speedband_callbacks(app):
    """
    Register callbacks for speed band information on the "Speed band on the roads" tab.
    
    Args:
        app: Dash app instance
    """
    @app.callback(
        [Output('speed-band-map-markers', 'children'),
         Output('speed-band-count-value', 'children'),
         Output('speed-band-center-coords', 'children')],
        [Input('speed-band-page-toggle-state', 'data'),
         Input('speed-band-interval', 'n_intervals'),
         Input('navigation-tabs', 'value'),
         Input('speed-band-map', 'zoom'),
         Input('speed-band-map', 'center'),
         Input('speed-band-map', 'click_lat_lng')]
    )
    def update_speed_band_page_display(_show_speed_band: bool, n_intervals: int, tab_value: str, 
                                     zoom: Optional[int], center: Any, click_lat_lng: Any) -> Tuple[List[dl.Polyline], html.Div, html.Div]:
        """
        Update Speed Band page markers, count, and information display.
        Only runs when the speed-band tab is active.
        Shows markers only when zoomed in close (zoom >= 17).
        """
        print(f"Callback triggered: tab={tab_value}, zoom={zoom}, center={center}")
        
        # Initialize center coordinates display
        center_coords_display = html.Div(
            [
                html.Span("Viewport Center: ", style={"color": "#ccc", "fontSize": "0.75rem"}),
                html.Span("--", style={"color": "#999", "fontSize": "0.75rem"}),
            ],
            style={
                "backgroundColor": "rgb(58, 74, 90)",
                "padding": "4px 8px",
                "borderRadius": "4px",
            }
        )
        
        global _last_active_tab
        _ = _show_speed_band  # Always show on speed band page

        # Only fetch and display data when speed-band tab is active
        if tab_value != 'speed-band':
            _last_active_tab = tab_value
            return [], html.Div(
                html.Span("Zoom in to trigger traffic band display", style={"color": "#999"}),
                style={
                    "backgroundColor": "rgb(58, 74, 90)",
                    "padding": "4px 8px",
                    "borderRadius": "4px",
                }
            ), center_coords_display

        # Trigger data fetch/refresh when speed-band tab is active
        # Fetch when: tab is first selected (tab switch) OR when interval triggers
        tab_just_selected = (_last_active_tab != 'speed-band')
        if tab_just_selected or n_intervals is not None:
            # Check if cache needs refresh (when tab is selected or interval triggers)
            # fetch_speed_band_data() will check cache and only fetch if needed
            from utils.async_fetcher import _executor
            # Trigger async fetch in background (non-blocking)
            _executor.submit(fetch_speed_band_data)
        
        _last_active_tab = tab_value

        # Initialize default message (zoom required)
        count_value = html.Div(
            html.Span("Zoom in to trigger traffic band display", style={"color": "#999"}),
            style={
                "backgroundColor": "rgb(58, 74, 90)",
                "padding": "4px 8px",
                "borderRadius": "4px",
            }
        )
        
        # Update center coordinates display - prioritize click location, then map center
        # Use click coordinates if available, otherwise use map center
        click_lat, click_lon = parse_coordinates(click_lat_lng)
        center_lat, center_lon = parse_coordinates(center)
        
        display_lat, display_lon = (click_lat, click_lon) if click_lat is not None else (center_lat, center_lon)
        
        if display_lat is not None and display_lon is not None:
            center_coords_display = html.Div(
                [
                    html.Span("Viewport Center: ", style={"color": "#ccc", "fontSize": "0.75rem"}),
                    html.Span(f"{display_lat:.6f}, {display_lon:.6f}", style={"color": "#00BCD4", "fontSize": "0.75rem", "fontWeight": "600"}),
                ],
                style={
                    "backgroundColor": "rgb(58, 74, 90)",
                    "padding": "4px 8px",
                    "borderRadius": "4px",
                }
            )
            # Print center update for debugging
            source = "click" if click_lat is not None else "center"
            print(f"Viewport display updated ({source}): {display_lat:.6f}, {display_lon:.6f} (zoom: {zoom})")
        
        markers = []
        displayed_count = 0
        
        # Only fetch and show markers when zoomed in close (zoom >= MIN_ZOOM_FOR_DISPLAY)
        if zoom is not None and zoom >= MIN_ZOOM_FOR_DISPLAY and center_lat is not None and center_lon is not None:
            # Check cache directly - fetch_speed_band_data() returns cached data if available and fresh
            # If cache is empty or stale, it will fetch in the background (triggered above)
            data = fetch_speed_band_data()
            
            if data:
                # Filter data by viewport bounds
                filtered_items = filter_speed_bands_by_viewport(data, center_lat, center_lon, zoom)
                
                # Create markers for filtered data
                if filtered_items:
                    filtered_data = {'value': filtered_items}
                    markers = create_speed_band_markers(filtered_data)
                    displayed_count = len(markers)
                    print(f"Displaying {displayed_count} speed band markers at zoom {zoom}")
                
                # Update count value to show number of speed bands displayed
                count_value = html.Div(
                    html.Span(f"{displayed_count}", style={"color": "#00BCD4"}),
                    style={
                        "backgroundColor": "rgb(58, 74, 90)",
                        "padding": "4px 8px",
                        "borderRadius": "4px",
                    }
                )

        return markers, count_value, center_coords_display

