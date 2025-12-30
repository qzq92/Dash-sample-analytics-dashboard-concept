"""
Callback functions for handling MRT/LRT Station Crowd information.
Uses LTA DataMall PCDRealTime API for real-time crowd density data.
"""
import os
import pandas as pd
from typing import Optional, Dict, List, Any, Tuple
from dash import Input, Output, html
import dash_leaflet as dl
from utils.async_fetcher import fetch_url_2min_cached

# API URL
PCD_REALTIME_URL = "https://datamall2.mytransport.sg/ltaodataservice/PCDRealTime"

# Station coordinates cache loaded from MRTStations.csv
_STATION_COORDS_CACHE: Optional[Dict[str, Tuple[float, float]]] = None

# Crowd level colors
CROWD_COLORS = {
    'l': '#32CD32',  # Low - Green
    'm': '#FFD700',  # Moderate - Yellow/Gold
    'h': '#FF4500',  # High - Orange Red
    'NA': '#888888',  # Not Available - Grey
}

# Crowd level labels
CROWD_LABELS = {
    'l': 'Low',
    'm': 'Moderate',
    'h': 'High',
    'NA': 'Not Available',
}


def fetch_station_crowd_data(train_line: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Fetch station crowd density data from LTA DataMall PCDRealTime API.
    
    Args:
        train_line: Optional train line code to filter (e.g., 'NSL', 'EWL')
                   If None, fetches all lines
    
    Returns:
        Dictionary containing crowd data or None if error
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
    
    # Build URL with optional train line filter
    url = PCD_REALTIME_URL
    if train_line and train_line != "all":
        url = f"{PCD_REALTIME_URL}?TrainLine={train_line}"
    
    # Use cached fetch (2-minute cache)
    data = fetch_url_2min_cached(url, headers)
    
    return data


def _load_station_coordinates() -> Dict[str, Tuple[float, float]]:
    """
    Load station coordinates from MRTStations.csv file.
    Caches the result to avoid reloading on every call.
    
    Returns:
        Dictionary mapping station codes to (lat, lon) tuples
    """
    global _STATION_COORDS_CACHE
    
    if _STATION_COORDS_CACHE is not None:
        return _STATION_COORDS_CACHE
    
    _STATION_COORDS_CACHE = {}
    
    try:
        # Get project root (parent of callbacks folder)
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_file_dir)
        csv_path = os.path.join(project_root, 'data', 'MRTStations.csv')
        
        if not os.path.exists(csv_path):
            print(f"Warning: MRTStations.csv not found at {csv_path}")
            return _STATION_COORDS_CACHE
        
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Process each station
        for _, row in df.iterrows():
            try:
                stn_no = str(row.get('STN_NO', '')).strip()
                lat = float(row.get('Latitude', 0))
                lon = float(row.get('Longitude', 0))
                
                if stn_no and lat != 0 and lon != 0:
                    # Handle stations with multiple codes (e.g., "EW8/CC9")
                    codes = [code.strip() for code in stn_no.split('/')]
                    for code in codes:
                        if code:
                            _STATION_COORDS_CACHE[code] = (lat, lon)
            except (ValueError, TypeError, KeyError) as e:
                continue
        
        print(f"Loaded {len(_STATION_COORDS_CACHE)} station coordinates from MRTStations.csv")
        
    except Exception as e:
        print(f"Error loading MRTStations.csv: {e}")
    
    return _STATION_COORDS_CACHE


def get_station_coordinates(station_code: str) -> Optional[Tuple[float, float]]:
    """
    Get coordinates for a station code from MRTStations.csv.
    
    Args:
        station_code: Station code (e.g., 'NS1', 'EW13')
    
    Returns:
        Tuple of (lat, lon) or None if not found
    """
    coords_map = _load_station_coordinates()
    return coords_map.get(station_code)


def create_crowd_markers(crowd_data: Optional[Dict[str, Any]], line_filter: str = "all") -> List[dl.CircleMarker]:
    """
    Create map markers for stations with crowd levels.
    
    Args:
        crowd_data: Dictionary containing crowd data from API
        line_filter: Train line filter ('all' or specific line code)
    
    Returns:
        List of dl.CircleMarker components
    """
    markers = []
    
    if not crowd_data or 'value' not in crowd_data:
        return markers
    
    stations = crowd_data.get('value', [])
    
    for station in stations:
        try:
            station_code = station.get('Station', '')
            crowd_level = station.get('CrowdLevel', 'NA')
            train_line = station.get('TrainLine', '')
            
            # Filter by train line if specified
            if line_filter != "all" and train_line != line_filter:
                continue
            
            # Get station coordinates
            coords = get_station_coordinates(station_code)
            if not coords:
                # Skip if coordinates not available
                continue
            
            lat, lon = coords
            color = CROWD_COLORS.get(crowd_level, '#888888')
            
            # Create marker with popup
            popup_text = f"{station_code}<br>Crowd: {CROWD_LABELS.get(crowd_level, 'Unknown')}"
            if train_line:
                popup_text += f"<br>Line: {train_line}"
            
            markers.append(
                dl.CircleMarker(
                    center=[lat, lon],
                    radius=8,
                    color="#fff",
                    weight=2,
                    fillColor=color,
                    fillOpacity=0.8,
                    children=[
                        dl.Popup(popup_text)
                    ]
                )
            )
        except (ValueError, TypeError, KeyError) as e:
            print(f"Error creating marker for station: {e}")
            continue
    
    return markers


def format_station_list(crowd_data: Optional[Dict[str, Any]], line_filter: str = "all") -> List[html.Div]:
    """
    Format station list with crowd levels for display.
    
    Args:
        crowd_data: Dictionary containing crowd data from API
        line_filter: Train line filter ('all' or specific line code)
    
    Returns:
        List of HTML Div elements for each station
    """
    items = []
    
    if not crowd_data or 'value' not in crowd_data:
        return [html.P("No crowd data available", style={"color": "#999", "textAlign": "center", "padding": "20px"})]
    
    stations = crowd_data.get('value', [])
    
    # Filter by train line if specified
    if line_filter != "all":
        stations = [s for s in stations if s.get('TrainLine', '') == line_filter]
    
    if not stations:
        return [html.P(f"No stations found for selected line", style={"color": "#999", "textAlign": "center", "padding": "20px"})]
    
    # Sort by station code
    stations.sort(key=lambda x: x.get('Station', ''))
    
    for station in stations:
        try:
            station_code = station.get('Station', 'Unknown')
            crowd_level = station.get('CrowdLevel', 'NA')
            train_line = station.get('TrainLine', '')
            start_time = station.get('StartTime', '')
            end_time = station.get('EndTime', '')
            
            color = CROWD_COLORS.get(crowd_level, '#888888')
            label = CROWD_LABELS.get(crowd_level, 'Unknown')
            
            items.append(
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    style={
                                        "width": "12px",
                                        "height": "12px",
                                        "backgroundColor": color,
                                        "borderRadius": "50%",
                                        "marginRight": "8px",
                                    }
                                ),
                                html.Div(
                                    [
                                        html.Span(
                                            station_code,
                                            style={
                                                "fontWeight": "600",
                                                "fontSize": "0.875rem",
                                                "color": "#fff",
                                            }
                                        ),
                                        html.Span(
                                            f" ({train_line})" if train_line else "",
                                            style={
                                                "fontSize": "0.75rem",
                                                "color": "#aaa",
                                                "marginLeft": "4px",
                                            }
                                        ),
                                    ],
                                    style={"flex": "1"}
                                ),
                                html.Span(
                                    label,
                                    style={
                                        "fontSize": "0.75rem",
                                        "color": color,
                                        "fontWeight": "600",
                                    }
                                ),
                            ],
                            style={
                                "display": "flex",
                                "alignItems": "center",
                                "marginBottom": "4px",
                            }
                        ),
                        html.Div(
                            f"Time: {start_time} - {end_time}" if start_time and end_time else "",
                            style={
                                "fontSize": "0.6875rem",
                                "color": "#888",
                                "marginTop": "2px",
                            }
                        ),
                    ],
                    style={
                        "padding": "8px 12px",
                        "borderBottom": "1px solid rgba(255, 255, 255, 0.1)",
                        "marginBottom": "4px",
                        "backgroundColor": "rgba(42, 54, 66, 0.5)",
                        "borderRadius": "4px",
                    }
                )
            )
        except (ValueError, TypeError, KeyError) as e:
            print(f"Error formatting station: {e}")
            continue
    
    return items


def register_mrt_crowd_callbacks(app):
    """
    Register callbacks for MRT/LRT Station Crowd page.
    
    Args:
        app: Dash app instance
    """
    @app.callback(
        [Output('mrt-crowd-map-markers', 'children'),
         Output('mrt-crowd-station-list', 'children'),
         Output('mrt-crowd-count-value', 'children'),
         Output('mrt-crowd-data-store', 'data')],
        [Input('mrt-crowd-interval', 'n_intervals'),
         Input('mrt-crowd-line-filter', 'value'),
         Input('navigation-tabs', 'value')]
    )
    def update_mrt_crowd_display(n_intervals: int, line_filter: str, tab_value: str):
        """
        Update MRT/LRT Station Crowd display.
        Only fetches and displays data when the mrt-crowd tab is active.
        """
        # Only fetch and display data when mrt-crowd tab is active
        if tab_value != 'mrt-crowd':
            return [], html.P("Select MRT/LRT Station Crowd tab to view data", 
                            style={"color": "#999", "textAlign": "center", "padding": "20px"}), \
                   html.Div(html.Span("--", style={"color": "#999"}), 
                           style={"backgroundColor": "rgb(58, 74, 90)", "padding": "4px 8px", "borderRadius": "4px"}), None
        
        # Fetch crowd data
        crowd_data = fetch_station_crowd_data(line_filter if line_filter else None)
        
        if not crowd_data:
            return [], html.P("Error loading crowd data. Please try again later.", 
                            style={"color": "#ff6b6b", "textAlign": "center", "padding": "20px"}), \
                   html.Div(html.Span("Error", style={"color": "#ff6b6b"}), 
                           style={"backgroundColor": "rgb(58, 74, 90)", "padding": "4px 8px", "borderRadius": "4px"}), None
        
        # Create markers
        markers = create_crowd_markers(crowd_data, line_filter or "all")
        
        # Format station list
        station_list = format_station_list(crowd_data, line_filter or "all")
        
        # Count stations
        stations = crowd_data.get('value', [])
        if line_filter and line_filter != "all":
            stations = [s for s in stations if s.get('TrainLine', '') == line_filter]
        count = len(stations)
        
        count_display = html.Div(
            html.Span(f"{count} stations", style={"color": "#00BCD4"}),
            style={
                "backgroundColor": "rgb(58, 74, 90)",
                "padding": "4px 8px",
                "borderRadius": "4px",
            }
        )
        
        return markers, station_list, count_display, crowd_data

