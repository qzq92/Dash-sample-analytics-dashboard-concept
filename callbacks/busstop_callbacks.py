"""
Callback functions for handling nearest bus stop display using OneMap Nearby Transport API.
Reference: https://www.onemap.gov.sg/apidocs/nearbytransport
"""
import requests
from dash.dependencies import Input, Output
from dash import html
from callbacks.map_callback import _haversine_distance_m
#from auth.onemap_api import get_onemap_token
import os

def fetch_nearby_bus_stops(lat: float, lon: float, radius_m: int = 500) -> list:
    """
    Fetch nearest bus stops using OneMap Nearby Transport API.
    Reference: https://www.onemap.gov.sg/apidocs/nearbytransport
    
    Uses the getNearestBusStops endpoint which returns bus stops within radius.
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        radius_m: Search radius in meters (default: 500)
    
    Returns:
        List of bus stop dictionaries with distance information
    """
    try:
        # OneMap Nearby Transport API endpoint for bus stops
        url = f"https://www.onemap.gov.sg/api/public/nearbysvc/getNearestBusStops?latitude={lat}&longitude={lon}&radius_in_meters={radius_m}"

        print(url)

        # Get API token from auth module - uses cached token if valid, no re-authentication needed
        # Token is already cached from app startup, this just retrieves it
        api_token = os.getenv("ONEMAP_API_KEY")
        
        headers = {}
        if api_token:
            # OneMap API expects Authorization header with Bearer token format
            headers["Authorization"] = f"{api_token}"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            if not data:
                print(f"No bus stops found within {radius_m}m")
                return []
            
            print(f"Found {len(data)} bus stops within {radius_m}m")
            # Process and add distance information
            processed_results = []
            for bus_stop in data:
                try:
                    # Try different possible field names from API response
                    stop_lat = float(
                        bus_stop.get('lat') or 0
                    )
                    stop_lon = float(
                        bus_stop.get('lon') or 0
                    )
                    
                    # Skip if data is invalid
                    if stop_lat == 0 or stop_lon == 0:
                        continue
                    
                    # Calculate distance using haversine formula
                    distance_m = _haversine_distance_m(lat, lon, stop_lat, stop_lon)
                    
                    # Only include bus stops within the specified radius
                    if distance_m <= radius_m:
                        # Get bus stop name/description from various possible fields
                        name = (
                            bus_stop.get('name') or
                            'Unknown Bus Stop'
                        )
                        
                        # Get bus stop code if available
                        bus_stop_id = (
                            bus_stop.get('id') or
                            ''
                        )
                        
                        processed_results.append({
                            'name': name,
                            'code': bus_stop_id,
                            'distance_m': distance_m,
                            'latitude': stop_lat,
                            'longitude': stop_lon,
                            'raw_data': bus_stop
                        })
                except (ValueError, TypeError, KeyError) as e:
                    print(f"Error processing bus stop data: {e}")
                    continue
            
            # Sort by distance (closest first)
            processed_results.sort(key=lambda x: x['distance_m'])
            
            return processed_results
        
        print(f"OneMap Nearby Transport API failed for bus stops: status={response.status_code}, body={response.text[:200]}")
        return []
            
    except requests.exceptions.RequestException as e:
        print(f"Error calling OneMap Nearby Transport API: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error in fetch_nearby_bus_stops: {e}")
        return []


def register_busstop_callbacks(app):
    """
    Register callbacks for displaying nearest bus stops.
    """
    
    @app.callback(
        Output('nearest-bus-stop-content', 'children'),
        Input('input_search', 'value')
    )
    def update_nearest_bus_stop_content(search_value):
        """
        Update the nearest bus stop content based on selected location.
        
        Args:
            search_value: Selected value from search dropdown (format: 'lat,lon,address')
        
        Returns:
            HTML Div containing nearest bus stops within 500m
        """
        if not search_value:
            return html.P(
                "Select a location to view nearest bus stops",
                style={
                    "textAlign": "center",
                    "color": "#999",
                    "fontSize": "14px",
                    "fontStyle": "italic",
                    "padding": "20px"
                }
            )
        
        try:
            # Parse the search value to get coordinates
            parts = search_value.split(',', 2)
            lat = float(parts[0])
            lon = float(parts[1])
        except (ValueError, IndexError, TypeError):
            return html.P(
                "Invalid location coordinates",
                style={
                    "textAlign": "center",
                    "color": "#ff6b6b",
                    "fontSize": "14px",
                    "padding": "20px"
                }
            )
        
        # Fetch nearby bus stops within 500m
        bus_stops = fetch_nearby_bus_stops(lat, lon, radius_m=500)
        
        if not bus_stops:
            return html.P(
                "No bus stops found within 500m",
                style={
                    "textAlign": "center",
                    "color": "#999",
                    "fontSize": "14px",
                    "fontStyle": "italic",
                    "padding": "20px"
                }
            )
        
        # Build display items for each bus stop
        bus_stop_items = []
        for bus_stop in bus_stops:
            name = bus_stop['name']
            code = bus_stop['code']
            distance_m = bus_stop['distance_m']
            
            # Format distance display
            if distance_m < 1000:
                distance_str = f"{int(distance_m)}m"
            else:
                distance_str = f"{distance_m/1000:.2f}km"
            
            # Build display text with name and code if available
            display_name = name
            if code:
                display_name = f"{name} ({code})"
            
            bus_stop_items.append(
                html.Div(
                    [
                        html.Div(
                            display_name,
                            style={
                                "fontWeight": "600",
                                "fontSize": "14px",
                                "color": "#fff",
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
        
        # Return all bus stop items
        return bus_stop_items

