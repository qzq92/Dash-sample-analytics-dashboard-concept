"""
Callback functions for handling MRT/LRT Station Crowd information.
Uses LTA DataMall PCDRealTime API for real-time crowd density data.
"""
import os
import csv
import re
import threading
from typing import Optional, Dict, List, Any
from concurrent.futures import as_completed
from dash import Input, Output, html
from utils.async_fetcher import fetch_url_10min_cached, _executor, get_current_10min_bucket

# API URL
PCD_REALTIME_URL = "https://datamall2.mytransport.sg/ltaodataservice/PCDRealTime"

# Global cache for the combined crowd data to ensure 10-minute alignment
_COMBINED_CROWD_CACHE = {'data': None, 'bucket': None}
_COMBINED_CROWD_LOCK = threading.Lock()


# Official Line Colors and Names (ordered as per TrainLine parameter support)
LINE_INFO = {
    'CCL': {'name': 'Circle Line', 'color': '#FFA500'},
    'CEL': {'name': 'Circle Line Extension – BayFront, Marina Bay', 'color': '#FFA500'},
    'CGL': {'name': 'Changi Extension – Expo, Changi Airport', 'color': '#009645'},
    'DTL': {'name': 'Downtown Line', 'color': '#005EC4'},
    'EWL': {'name': 'East West Line', 'color': '#009645'},
    'NEL': {'name': 'North East Line', 'color': '#9900AA'},
    'NSL': {'name': 'North South Line', 'color': '#D42E12'},
    'BPL': {'name': 'Bukit Panjang LRT', 'color': '#748477'},
    'SLRT': {'name': 'Sengkang LRT', 'color': '#748477'},
    'PLRT': {'name': 'Punggol LRT', 'color': '#748477'},
    'TEL': {'name': 'Thomson-East Coast Line', 'color': '#9D5B25'},
}

# List of all train lines to fetch
ALL_TRAIN_LINES = ['CCL', 'CEL', 'CGL', 'DTL', 'EWL', 'NEL', 'NSL', 'BPL', 'SLRT', 'PLRT', 'TEL']

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


def _station_sort_key(station_obj):
    """
    Helper to sort station codes numerically (e.g., EW1, EW2, ..., EW10).
    """
    station_code = station_obj.get('Station', '')
    if not station_code:
        return ("", 0)

    # Extract prefix (e.g., EW) and number (e.g., 10)
    match = re.match(r"([a-zA-Z]+)(\d+)", station_code)
    if match:
        prefix, number = match.groups()
        return (prefix.upper(), int(number))

    # Fallback for codes that don't match the pattern
    return (station_code.upper(), 0)

# Station name mapping cache
_STATION_NAME_MAP = None


def _load_station_names() -> Dict[str, str]:
    """
    Load station codes to station names mapping from CSV file.
    Returns a dictionary mapping station codes to station names.
    """
    global _STATION_NAME_MAP
    if _STATION_NAME_MAP is not None:
        return _STATION_NAME_MAP

    _STATION_NAME_MAP = {}
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'MRTLRTStations.csv')

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                stn_no = row.get('STN_NO', '').strip()
                stn_name = row.get('STN_NAME', '').strip()
                if stn_no and stn_name:
                    # Handle multi-line stations (e.g., "EW8/CC9")
                    if '/' in stn_no:
                        for code in stn_no.split('/'):
                            _STATION_NAME_MAP[code.strip()] = stn_name
                    else:
                        _STATION_NAME_MAP[stn_no] = stn_name
    except Exception as e:
        print(f"Warning: Could not load station names from CSV: {e}")

    return _STATION_NAME_MAP


def fetch_station_crowd_data(train_line: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Fetch station crowd density data from LTA DataMall PCDRealTime API.

    Args:
        train_line: Optional train line code
                   (CCL, CEL, CGL, DTL, EWL, NEL, NSL, BPL, SLRT, PLRT, TEL)
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

    # Build URL with TrainLine parameter if specified
    url = PCD_REALTIME_URL
    if train_line:
        url = f"{PCD_REALTIME_URL}?TrainLine={train_line}"

    # Use cached fetch (10-minute cache based on system clock)
    return fetch_url_10min_cached(url, headers)


def fetch_all_station_crowd_data() -> Optional[Dict[str, Any]]:
    """
    Fetch crowd data for all train lines in parallel and combine results.
    Uses a 10-minute in-memory cache aligned to system clock.

    Returns:
        Dictionary containing combined crowd data from all lines or None if error
    """
    global _COMBINED_CROWD_CACHE
    
    current_bucket = get_current_10min_bucket()
    
    # Check high-level cache first
    with _COMBINED_CROWD_LOCK:
        if _COMBINED_CROWD_CACHE['bucket'] == current_bucket and _COMBINED_CROWD_CACHE['data'] is not None:
            # print(f"DEBUG: Serving combined crowd data from 10-minute cache (bucket: {current_bucket})")
            return _COMBINED_CROWD_CACHE['data']

    # If not in cache or bucket expired, fetch fresh data
    # Fetch all lines in parallel
    futures = {
        _executor.submit(fetch_station_crowd_data, line): line
        for line in ALL_TRAIN_LINES
    }

    all_stations = []
    for future in as_completed(futures):
        line = futures[future]
        try:
            data = future.result()
            if data and 'value' in data:
                stations = data['value']
                # Add TrainLine to each station if not present
                for station in stations:
                    if 'TrainLine' not in station or not station.get('TrainLine'):
                        station['TrainLine'] = line
                all_stations.extend(stations)
                # print(f"DEBUG: Fetched {len(stations)} stations for line {line}")
        except Exception as e:
            print(f"Error fetching crowd data for {line}: {e}")

    if not all_stations:
        return None

    combined_data = {'value': all_stations}
    
    # Update cache
    with _COMBINED_CROWD_LOCK:
        _COMBINED_CROWD_CACHE = {
            'data': combined_data,
            'bucket': current_bucket
        }

    print(f"DEBUG: Combined crowd data fetched and cached for bucket {current_bucket} ({len(all_stations)} stations)")
    return combined_data


def format_line_cards(crowd_data: Optional[Dict[str, Any]]) -> List[html.Div]:
    """
    Generate expandable cards for each train line.
    Returns a list with MRT lines in the first row and LRT lines in the second row.
    """
    if not crowd_data or 'value' not in crowd_data:
        msg = "No crowd data available"
        return [html.P(msg, style={"color": "#999", "textAlign": "center", "padding": "1.25rem"})]

    stations = crowd_data.get('value', [])
    station_names = _load_station_names()

    # Group stations by line
    line_groups = {}
    for station in stations:
        line = station.get('TrainLine', 'Other')
        if line not in line_groups:
            line_groups[line] = []
        line_groups[line].append(station)

    print(f"DEBUG: Line groups found: {list(line_groups.keys())}")
    print(f"DEBUG: Total stations: {len(stations)}")

    # MRT lines and LRT lines
    mrt_lines = ['CCL', 'CEL', 'CGL', 'DTL', 'EWL', 'NEL', 'NSL', 'TEL']
    lrt_lines = ['BPL', 'SLRT', 'PLRT']

    def create_line_card(line_code):
        """Helper function to create a single line card"""
        if line_code not in line_groups:
            return None

        line_stations = line_groups[line_code]
        line_stations.sort(key=_station_sort_key)

        info = LINE_INFO.get(line_code, {'name': f'{line_code} Line', 'color': '#888'})

        # Create station items for the expanded view
        station_items = []
        for stn in line_stations:
            lvl = stn.get('CrowdLevel', 'NA')
            color = CROWD_COLORS.get(lvl, '#888888')
            stn_code = stn.get('Station', '')
            stn_name = station_names.get(stn_code, stn_code)
            label = CROWD_LABELS.get(lvl, 'Unknown')

            station_items.append(
                html.Div([
                    html.Div([
                        html.Span(stn_code, style={"fontWeight": "700", "color": info['color'],
                                                   "fontSize": "0.85rem", "marginRight": "0.5rem"}),
                        html.Span(stn_name, style={"fontWeight": "400", "color": "#fff",
                                                   "fontSize": "0.85rem", "flex": "1"}),
                    ], style={"display": "flex", "alignItems": "center", "flex": "1"}),
                    html.Span(label, style={"color": color, "fontSize": "0.8rem",
                                          "fontWeight": "700"})
                ], style={
                    "padding": "0.375rem 0.625rem",
                    "borderBottom": "0.0625rem solid rgba(255,255,255,0.05)",
                    "display": "flex", "alignItems": "center"
                })
            )

        # Create the Card - expanded by default with fixed header
        return html.Div([
            # Card Header
            html.Div([
                html.Div(style={
                    "width": "0.25rem", "height": "1.5rem",
                    "backgroundColor": info['color'], "marginRight": "0.625rem"
                }),
                html.Span(
                    info['name'],
                    style={"fontWeight": "bold", "color": info['color']}
                ),
                html.Span(f" ({len(line_stations)} stns)",
                         style={"color": "#aaa", "marginLeft": "auto",
                               "fontSize": "0.75rem"})
            ], style={
                "display": "flex", "alignItems": "center",
                "width": "100%", "padding": "0.625rem 0.75rem",
                "borderBottom": f"0.0625rem solid {info['color']}22"
            }),
            # Card Content (Scrollable - standardised for ~5 stations)
            html.Div(
                station_items,
                style={
                    "height": "11.5625rem", "overflowY": "auto",
                    "backgroundColor": "rgba(0,0,0,0.15)", "padding": "0.3125rem"
                }
            )
        ],
            style={
                "backgroundColor": "rgba(58, 74, 90, 0.8)",
                "borderRadius": "0.375rem",
                "border": f"0.0625rem solid {info['color']}44",
                "overflow": "hidden",
                "minWidth": "17.5rem",
                "flex": "1 1 17.5rem",
                "maxWidth": "25rem",
                "display": "flex",
                "flexDirection": "column"
            }
        )

    # Create all line cards (MRT and LRT combined)
    all_cards = []
    for line in mrt_lines + lrt_lines:
        if line in line_groups:
            card = create_line_card(line)
            if card is not None:
                all_cards.append(card)

    print(f"DEBUG: Total cards created: {len(all_cards)}")

    # If no cards at all, return empty message
    if not all_cards:
        return [html.P("No station data available",
                      style={"color": "#999", "textAlign": "center", "padding": "1.25rem"})]

    # Build the layout as a 3 rows x 4 columns grid
    return [
        html.Div(
            all_cards,
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(4, 1fr)",
                "gridTemplateRows": "repeat(3, auto)",
                "gap": "0.9375rem",
                "width": "100%",
                "alignItems": "stretch",
            }
        )
    ]


def format_crowd_level_cards(crowd_data: Optional[Dict[str, Any]]) -> List[html.Div]:
    """
    Generate expandable cards for each crowd level (Low, Moderate, High).
    """
    if not crowd_data or 'value' not in crowd_data:
        msg = "No crowd data available"
        return [html.P(msg, style={"color": "#999", "textAlign": "center", "padding": "1.25rem"})]

    stations = crowd_data.get('value', [])
    station_names = _load_station_names()

    # Group stations by crowd level
    crowd_groups = {
        'l': [],
        'm': [],
        'h': [],
        'NA': []
    }

    for station in stations:
        crowd_level = station.get('CrowdLevel', 'NA').strip().lower()
        if crowd_level not in crowd_groups:
            crowd_level = 'NA'
        crowd_groups[crowd_level].append(station)

    # Sort stations within each group by station code numerically
    for level in crowd_groups:
        crowd_groups[level].sort(key=_station_sort_key)

    # Order: Low, Moderate, High, NA
    level_order = ['l', 'm', 'h', 'NA']
    cards = []

    for level in level_order:
        level_stations = crowd_groups[level]
        if not level_stations:
            continue

        color = CROWD_COLORS.get(level, '#888888')
        label = CROWD_LABELS.get(level, 'Unknown')

        # Create station items for the expanded view
        station_items = []
        for stn in level_stations:
            stn_code = stn.get('Station', '')
            stn_name = station_names.get(stn_code, stn_code)
            train_line = stn.get('TrainLine', '')
            line_info = LINE_INFO.get(train_line, {'color': '#888'})
            line_color = line_info['color']

            station_items.append(
                html.Div([
                    html.Div([
                        html.Span(stn_code, style={"fontWeight": "700", "color": line_color,
                                                   "fontSize": "0.85rem", "marginRight": "0.5rem"}),
                        html.Span(stn_name, style={"fontWeight": "400", "color": "#fff",
                                                   "fontSize": "0.85rem", "flex": "1"}),
                    ], style={"display": "flex", "alignItems": "center", "flex": "1"}),
                    html.Span(train_line, style={
                        "color": "#aaa", "fontSize": "0.75rem", "marginRight": "0.5rem"
                    }),
                ], style={
                    "padding": "0.375rem 0.625rem",
                    "borderBottom": "0.0625rem solid rgba(255,255,255,0.05)",
                    "display": "flex", "alignItems": "center"
                })
            )

        # Create the Card - expanded by default with fixed header
        cards.append(
            html.Div([
                # Card Header
                html.Div([
                    html.Div(style={
                        "width": "0.25rem", "height": "1.5rem",
                        "backgroundColor": color, "marginRight": "0.625rem"
                    }),
                    html.Span(
                        f"{label} Crowd",
                        style={"fontWeight": "bold", "color": "#fff"}
                    ),
                    html.Span(f" ({len(level_stations)} stns)",
                              style={"color": "#aaa", "marginLeft": "auto",
                                     "fontSize": "0.75rem"})
                ], style={
                    "display": "flex", "alignItems": "center",
                    "width": "100%", "padding": "0.625rem 0.75rem",
                    "borderBottom": f"0.0625rem solid {color}22"
                }),
                # Card Content (Scrollable - standardised for ~5 stations)
                html.Div(
                    station_items,
                    style={
                        "height": "11.5625rem", "overflowY": "auto",
                        "backgroundColor": "rgba(0,0,0,0.15)", "padding": "0.3125rem"
                    }
                )
            ],
                style={
                    "backgroundColor": "rgba(58, 74, 90, 0.8)",
                    "borderRadius": "0.375rem",
                    "marginBottom": "0.9375rem",
                    "border": f"0.0625rem solid {color}44",
                    "overflow": "hidden",
                    "minWidth": "17.5rem",
                    "flex": "1 1 17.5rem",
                    "maxWidth": "25rem",
                    "display": "flex",
                    "flexDirection": "column"
                }
            )
        )

    # Wrap all crowd level cards in a flex container for consistent layout
    return [
        html.Div(
            cards,
            style={
                "display": "flex",
                "flexDirection": "row",
                "gap": "0.9375rem",
                "flexWrap": "wrap",
                "width": "100%",
                "alignItems": "flex-start",
                "justifyContent": "flex-start",
            }
        )
    ]


def register_mrt_crowd_callbacks(app):
    """
    Register callbacks for MRT/LRT Station Crowd page.
    """
    @app.callback(
        Output('mrt-crowd-view-toggle', 'children'),
        Input('mrt-crowd-view-toggle', 'n_clicks'),
        prevent_initial_call=False
    )
    def update_toggle_button(n_clicks):
        """Update toggle button text based on click count."""
        # Button text shows what view is CURRENTLY displayed
        # Default to "By Line" view (n_clicks=0 or even)
        if n_clicks is None:
            n_clicks = 0
        # When viewing by line (even clicks), button shows current view
        # When viewing by crowd (odd clicks), button shows current view
        return "View: By Crowd Level" if n_clicks % 2 == 1 else "View: By Line"

    @app.callback(
        [Output('mrt-crowd-station-list', 'children'),
         Output('mrt-crowd-count-value', 'children'),
         Output('mrt-crowd-data-store', 'data')],
        [Input('mrt-crowd-interval', 'n_intervals'),
         Input('navigation-tabs', 'value'),
         Input('mrt-crowd-view-toggle', 'n_clicks')]
    )
    def update_mrt_crowd_display(_n, tab_value: str, toggle_clicks: int):
        """
        Update MRT/LRT Station Crowd display.
        """
        if tab_value != 'mrt-crowd':
            loading_msg = html.P("Select MRT/LRT Station Crowd tab",
                               style={"color": "#999", "textAlign": "center",
                                      "padding": "1.25rem", "gridColumn": "1 / -1"})
            return [loading_msg], None, None

        # Fetch data for all train lines in parallel
        crowd_data = fetch_all_station_crowd_data()
        if not crowd_data:
            error_msg = html.P("Data currently unavailable. Please try again later.",
                             style={"color": "#ff6b6b", "textAlign": "center",
                                    "padding": "1.25rem", "gridColumn": "1 / -1"})
            return [error_msg], None, None

        # Determine view mode: 0 or even = By Line, odd = By Crowd Level
        if toggle_clicks is None:
            toggle_clicks = 0
        view_by_crowd = toggle_clicks % 2 == 1

        # Generate cards based on view mode
        if view_by_crowd:
            cards = format_crowd_level_cards(crowd_data)
        else:
            cards = format_line_cards(crowd_data)

        # Summary count - removed text as requested
        summary = None

        return cards, summary, crowd_data
