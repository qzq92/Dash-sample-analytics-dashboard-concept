"""
Callback functions for handling speed band information on the "Speed band on the roads" tab.
"""
import os
from typing import Optional, Dict, List, Any, Tuple
from dash import Input, Output, html
import dash_leaflet as dl
from utils.async_fetcher import fetch_url
from concurrent.futures import Future
from conf.speed_band_config import get_speed_range

# API URL
SPEED_BAND_URL = "https://datamall2.mytransport.sg/ltaodataservice/v4/TrafficSpeedBands"


def fetch_speed_band_data() -> Optional[Dict[str, Any]]:
    """
    Fetch all Traffic Speed Band data from LTA DataMall API with optimized parallel pagination.
    Strategy:
    1. Fetch records in batches of 5000 (10 pages of 500) in parallel.
    2. After each batch, check if the last page returned full 500 records.
    3. If yes, continue fetching the next batch of 5000.
    
    Returns:
        Dictionary containing all speed band data with combined 'value' list, or None if error
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
    
    from utils.async_fetcher import _executor
    from concurrent.futures import as_completed
    
    all_speed_bands = []
    page_size = 500
    batch_size = 5000  # 10 pages per batch
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
        
        # Submit all batch requests to thread pool
        batch_futures = {
            _executor.submit(fetch_url, url, headers): skip
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
    
    # Return in the same format as the API response
    return {'value': all_speed_bands}


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
            start_lat = float(item.get('StartLat', 0))
            start_lon = float(item.get('StartLon', 0))
            end_lat = float(item.get('EndLat', 0))
            end_lon = float(item.get('EndLon', 0))
            road_name = item.get('RoadName', 'Unknown Road')
            band = str(item.get('SpeedBand', '0'))
            
            if start_lat == 0 or end_lat == 0:
                continue
                
            color = band_colors.get(band, "#888888")
            
            # Convert speed band to speed range in km/h
            try:
                band_int = int(band)
                min_speed, max_speed = get_speed_range(band_int)
                if min_speed == 0 and max_speed == 0:
                    speed_range_text = f"Speed Band: {band}"
                elif band_int == 8:
                    # Speed band 8 is 70+ km/h
                    speed_range_text = f"Speed Band {band}: {min_speed}+ km/h"
                else:
                    speed_range_text = f"Speed Band {band}: {min_speed} km/h to {max_speed} km/h"
            except (ValueError, TypeError):
                speed_range_text = f"Speed Band: {band}"
            
            tooltip_text = f"Road: {road_name}\n{speed_range_text}"
            
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


def register_speedband_callbacks(app):
    """
    Register callbacks for speed band information on the "Speed band on the roads" tab.
    
    Args:
        app: Dash app instance
    """
    @app.callback(
        [Output('speed-band-map-markers', 'children'),
         Output('speed-band-count-value', 'children'),
         Output('speed-band-info-display', 'children')],
        [Input('speed-band-page-toggle-state', 'data'),
         Input('speed-band-interval', 'n_intervals'),
         Input('navigation-tabs', 'value')]
    )
    def update_speed_band_page_display(_show_speed_band: bool, n_intervals: int, tab_value: str) -> Tuple[List[dl.Polyline], html.Div, html.Div]:
        """
        Update Speed Band page markers, count, and information display.
        Only runs when the speed-band tab is active.
        """
        # Only fetch and display data when speed-band tab is active
        if tab_value != 'speed-band':
            return [], html.Div(
                html.Span("--", style={"color": "#999"}),
                style={
                    "backgroundColor": "rgb(58, 74, 90)",
                    "padding": "4px 8px",
                    "borderRadius": "4px",
                }
            ), html.Div()
        
        _ = n_intervals  # Used for periodic refresh
        _ = _show_speed_band  # Always show on speed band page

        # Fetch data asynchronously
        future = fetch_speed_band_data_async()
        data: Optional[Dict[str, Any]] = future.result() if future else None
        
        # Count number of road segments measured (always calculate)
        items = data.get('value', []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        road_segment_count = len(items) if items else 0
        
        if road_segment_count > 0:
            # Display number of road segments measured
            count_value = html.Div(
                html.Span(f"{road_segment_count}", style={"color": "#00BCD4"}),
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

        # Always show markers on speed band page
        markers = create_speed_band_markers(data)
        
        # Format speed band information display
        info_display = format_speed_band_display()

        return markers, count_value, info_display

