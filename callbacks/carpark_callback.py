"""
Callback functions for handling HDB Carpark Availability API integration.
Reference: https://data.gov.sg/datasets?query=carpark&resultId=d_ca933a644e55d34fe21f28b8052fac63
"""
import requests
import pandas as pd
import numpy as np
import os
from dash.dependencies import Input, Output
from dash import html
import dash_leaflet as dl
from typing import List, Optional, Dict, Tuple
from pyproj import Transformer

# Cache for carpark location data
_carpark_locations_cache: Optional[pd.DataFrame] = None


def load_carpark_locations() -> pd.DataFrame:
    """
    Load carpark locations from CSV with SVY21 coordinates.
    Caches the result for subsequent calls.
    
    Returns:
        DataFrame with carpark_number, x_coord, y_coord, and address columns (in SVY21)
    """
    global _carpark_locations_cache
    
    if _carpark_locations_cache is not None:
        return _carpark_locations_cache
    
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'HDBCarparkInformation.csv')
    
    try:
        print(f"Loading carpark data from: {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} carpark records")
        
        # Keep only necessary columns with SVY21 coordinates
        df = df[['car_park_no', 'x_coord', 'y_coord', 'address']].copy()
        df.columns = ['carpark_number', 'x_coord', 'y_coord', 'address']

        # Cache the result
        _carpark_locations_cache = df
        print(f"Carpark location data cached successfully")
        
        return df
    except Exception as e:
        print(f"Error loading carpark locations: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame(columns=['carpark_number', 'x_coord', 'y_coord', 'address'])




def fetch_carpark_availability() -> Optional[dict]:
    """
    Fetch carpark availability data from HDB Carpark Availability API.
    
    Returns:
        Dictionary containing carpark data or None if request fails
    """
    api_url = "https://api.data.gov.sg/v1/transport/carpark-availability"
    headers = {"Authorisation": os.getenv("ONEMAP_API_KEY")}
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching carpark availability: {e}")
        return None


def convert_wgs84_to_svy21(latitude: float, longitude: float) -> Tuple[float, float]:
    """
    Convert WGS84 (EPSG:4326) coordinates to SVY21 (EPSG:3414) using pyproj.
    
    Args:
        latitude: Latitude in WGS84 degrees
        longitude: Longitude in WGS84 degrees
    
    Returns:
        Tuple of (X, Y) coordinates in SVY21 (meters)
    """
    try:
        # Create transformer from WGS84 to SVY21
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:3414")
        
        # Transform coordinates
        # Note: pyproj returns (Y, X) for this transformation due to axis order
        # EPSG:4326 (WGS84) is (lat, lon) and EPSG:3414 (SVY21) is (Northing, Easting)
        y, x = transformer.transform(latitude, longitude)
        
        return x, y
    except Exception as e:
        print(f"Error converting coordinates via pyproj: {e}")
        return None, None


def convert_svy21_to_wgs84_vectorized(x_array: np.ndarray, y_array: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert SVY21 (EPSG:3414) coordinates to WGS84 (EPSG:4326) using pyproj (vectorized).
    
    Args:
        x_array: Array of X coordinates in SVY21 (meters)
        y_array: Array of Y coordinates in SVY21 (meters)
    
    Returns:
        Tuple of (latitude_array, longitude_array) in WGS84 degrees
    """
    try:
        # Create transformer from SVY21 to WGS84
        transformer = Transformer.from_crs("EPSG:3414", "EPSG:4326")
        
        # Transform coordinates (vectorized)
        # EPSG:3414 uses (Northing, Easting) = (Y, X) axis order
        # EPSG:4326 uses (Lat, Lon) axis order
        # So we must pass (y_array, x_array) to get (lat_array, lon_array)
        lat_array, lon_array = transformer.transform(y_array, x_array)
        
        return lat_array, lon_array
    except Exception as e:
        print(f"Error converting coordinates via pyproj: {e}")
        return None, None


def euclidean_distance_vectorized_svy21(x1: float, y1: float, x2_array: np.ndarray, y2_array: np.ndarray) -> np.ndarray:
    """
    Calculate Euclidean distance between one point and multiple points in SVY21 coordinate system.
    Since SVY21 is a projected coordinate system with units in meters, Euclidean distance is accurate.
    
    Args:
        x1: X coordinate of center point in SVY21 (meters)
        y1: Y coordinate of center point in SVY21 (meters)
        x2_array: Array of X coordinates in SVY21 (meters)
        y2_array: Array of Y coordinates in SVY21 (meters)
    
    Returns:
        Array of distances in meters
    """
    # Calculate Euclidean distance in meters
    dx = x2_array - x1
    dy = y2_array - y1
    distances_m = np.sqrt(dx * dx + dy * dy)
    
    return distances_m


def filter_carparks_by_distance(
    center_lat: float,
    center_lon: float,
    radius_m: float = 500.0
) -> List[Dict]:
    """
    Filter carparks within a specified radius (in meters) from the center point.
    Converts WGS84 coordinates to SVY21 and uses Euclidean distance calculation.
    
    Args:
        center_lat: Center latitude in WGS84 degrees
        center_lon: Center longitude in WGS84 degrees
        radius_m: Radius in meters (default: 500m)
    
    Returns:
        List of carpark dictionaries with distance information, sorted by distance
    """
    # Load carpark locations (in SVY21 coordinates)
    carpark_locations = load_carpark_locations()
    
    if carpark_locations.empty:
        return []
    
    # Convert center point from WGS84 (EPSG:4326) to SVY21 (EPSG:3414) using OneMap API
    center_x, center_y = convert_wgs84_to_svy21(center_lat, center_lon)
    
    # Check if conversion was successful
    if center_x is None or center_y is None:
        print(f"Failed to convert coordinates for ({center_lat}, {center_lon})")
        return []
    
    print(f"Center in WGS84: ({center_lat}, {center_lon})")
    print(f"Center in SVY21: ({center_x}, {center_y})")
    
    # Vectorized Euclidean distance calculation in SVY21 (meters)
    distances_m = euclidean_distance_vectorized_svy21(
        center_x, 
        center_y,
        carpark_locations['x_coord'].values,
        carpark_locations['y_coord'].values
    )
    
    # Convert distances to kilometers for display
    distances_km = distances_m / 1000.0
    
    # Add distance columns to dataframe
    carpark_locations['distance_m'] = distances_m
    carpark_locations['distance_km'] = distances_km

    #print(carpark_locations)
    
    # Filter carparks within radius
    nearby_carparks = carpark_locations[carpark_locations['distance_m'] <= radius_m].copy()
    
    # Sort by distance
    nearby_carparks = nearby_carparks.sort_values('distance_m')
    
    # If no carparks found, return empty list
    if nearby_carparks.empty:
        print(f"Found no carparks within radius of {radius_m}m")
        return []
    
    # Convert SVY21 coordinates back to WGS84 for display purposes (vectorized)
    lat_array, lon_array = convert_svy21_to_wgs84_vectorized(
        nearby_carparks['x_coord'].values,
        nearby_carparks['y_coord'].values
    )
    
    if lat_array is not None and lon_array is not None:
        nearby_carparks['latitude'] = lat_array
        nearby_carparks['longitude'] = lon_array
    else:
        print("Error converting SVY21 to WGS84")
        return []
    
    # Convert to list of dictionaries
    results = nearby_carparks[['carpark_number', 'latitude', 'longitude', 'address', 'distance_km']].to_dict('records')
    
    print(f"Found {len(results)} carparks within radius of {radius_m}m")
    return results


def _get_label_letter(index):
    """Get label letter (A, B, C, D, E) for index."""
    labels = ['A', 'B', 'C', 'D', 'E']
    return labels[index] if index < len(labels) else str(index + 1)


def create_carpark_markers(nearby_carparks, availability_lookup=None):
    """Create map markers for carparks with carpark ID labels.
    
    Note: lat/lon coordinates are derived from CSV file (SVY21 converted to WGS84),
    not from the carpark availability API which only provides lot availability data.
    
    Args:
        nearby_carparks: List of carpark dictionaries with location data
        availability_lookup: Optional dict mapping carpark numbers to availability data
    """
    markers = []
    for idx, carpark in enumerate(nearby_carparks):
        lat = carpark.get('latitude')
        lon = carpark.get('longitude')
        carpark_number = carpark.get('carpark_number', '')
        address = carpark.get('address', 'N/A')
        distance_km = carpark.get('distance_km', 0)

        if lat is None or lon is None:
            print(f"Skipping carpark {carpark_number}: missing lat/lon coordinates")
            continue
        
        print(f"Creating marker for {carpark_number} at ({lat}, {lon})")

        # Format distance
        if distance_km < 0.1:
            distance_str = f"{distance_km * 1000:.0f}m"
        else:
            distance_str = f"{distance_km:.2f}km"

        # Build tooltip text with availability
        tooltip_parts = []
        tooltip_parts.append(carpark_number)
        if address and address != 'N/A':
            tooltip_parts.append(address)
        tooltip_parts.append(distance_str)
        
        # Add availability info to tooltip if available
        if availability_lookup:
            availability = availability_lookup.get(carpark_number.upper(), {})
            carpark_info = availability.get('carpark_info', [])
            if carpark_info:
                tooltip_parts.append("")  # Empty line for spacing
                tooltip_parts.append("Availability:")
                for lot_info in carpark_info:
                    lot_type = lot_info.get('lot_type', '')
                    total_lots = lot_info.get('total_lots', '0')
                    lots_available = lot_info.get('lots_available', '0')
                    lot_type_name = format_lot_type_display(lot_type)
                    tooltip_parts.append(f"  {lot_type_name}: {lots_available}/{total_lots}")
        
        # Join all parts with line breaks
        tooltip_text = "\n".join(tooltip_parts)

        # Create marker HTML with carpark ID as label
        marker_html = (
            f'<div style="position:relative;display:flex;flex-direction:column;'
            f'align-items:center;">'
            f'<div style="background:#2196F3;color:#fff;padding:4px 8px;'
            f'border-radius:4px;border:2px solid #fff;'
            f'box-shadow:0 2px 8px rgba(33,150,243,0.6);'
            f'font-size:11px;font-weight:bold;white-space:nowrap;">'
            f'{carpark_number}</div>'
            f'<div style="width:0;height:0;border-left:8px solid transparent;'
            f'border-right:8px solid transparent;border-top:8px solid #2196F3;'
            f'margin-top:-2px;"></div>'
            f'</div>'
        )

        marker_id = f"carpark-{carpark_number}-{lat}-{lon}-{idx}"

        markers.append(dl.DivMarker(
            id=marker_id,
            position=[lat, lon],
            iconOptions={
                'className': 'carpark-pin',
                'html': marker_html,
                'iconSize': [60, 40],
                'iconAnchor': [30, 40],
            },
            children=[dl.Tooltip(tooltip_text)]
        ))

    return markers


def format_lot_type_display(lot_type: str) -> str:
    """
    Format lot type code to readable format.
    
    Args:
        lot_type: Lot type code (e.g., 'C', 'H', 'S', 'Y')
    
    Returns:
        Formatted lot type name (defaults to "Unknown" for empty strings)
    """
    if not lot_type:
        return "Unknown"
    
    lot_type_map = {
        'C': 'Cars',
        'H': 'Heavy vehicles',
        'S': 'Motorcycles with side car',
        'Y': 'Motorcycles',
    }
    return lot_type_map.get(lot_type.upper(), lot_type.upper())


def register_carpark_callbacks(app):
    """
    Register carpark availability callbacks.
    
    This callback automatically finds and displays carparks within 500m of the map center,
    showing their availability and distance from the center.
    """
    
    @app.callback(
        [Output('nearest-carpark-content', 'children'),
         Output('carpark-markers', 'children')],
        Input('map-coordinates-store', 'data')
    )
    def update_carpark_availability(map_coords):
        """
        Update carpark availability display based on map center location.
        Shows carparks within 500m of the map center.
        
        Args:
            map_coords: Dictionary containing {'lat': float, 'lon': float} of map center
        
        Returns:
            HTML Div containing carpark availability information
        """
        if not map_coords:
            return html.P(
                "Select a location to view nearest carparks",
                style={
                    "textAlign": "center",
                    "padding": "15px",
                    "color": "#999",
                    "fontSize": "12px",
                    "fontStyle": "italic"
                }
            ), []
        
        try:
            center_lat = float(map_coords.get('lat'))
            center_lon = float(map_coords.get('lon'))
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
        
        # Find carparks within 500m and limit to top 5
        print(f"Searching for carparks near ({center_lat}, {center_lon})")
        nearby_carparks = filter_carparks_by_distance(center_lat, center_lon, radius_m=500.0)
        print(f"Found {len(nearby_carparks)} carparks within 500m")
        
        # Limit to top 5 nearest
        nearby_carparks = nearby_carparks[:5]
        
        if not nearby_carparks:
            return html.P(
                "No carparks found within 500m",
                style={
                    "textAlign": "center",
                    "padding": "15px",
                    "color": "#999",
                    "fontSize": "12px",
                    "fontStyle": "italic"
                }
            ), []
        
        # Fetch availability data from API
        api_data = fetch_carpark_availability()
        
        if not api_data:
            return html.Div(
                "Error fetching carpark data",
                style={
                    "textAlign": "center",
                    "padding": "15px",
                    "color": "#ff6b6b",
                    "fontSize": "12px"
                }
            ), []
        
        # Extract carpark data from API response
        items = api_data.get('items', [])
        if not items:
            return html.Div(
                "No carpark data available",
                style={
                    "textAlign": "center",
                    "padding": "15px",
                    "color": "#ff6b6b",
                    "fontSize": "12px"
                }
            ), []
        
        # Get carpark data from first item (latest timestamp)
        carpark_availability_data = items[0].get('carpark_data', [])
        
        # Create a lookup dictionary for availability data
        availability_lookup = {
            cp.get('carpark_number', '').upper(): cp
            for cp in carpark_availability_data
        }
        
        # Create markers for map with availability data
        markers = create_carpark_markers(nearby_carparks, availability_lookup)

        # Build display components for each nearby carpark
        carpark_cards = []
        
        for carpark in nearby_carparks:
            carpark_number = carpark['carpark_number']
            distance_km = carpark['distance_km']
            address = carpark.get('address', 'N/A')
            
            # Get availability data
            availability = availability_lookup.get(carpark_number.upper(), {})
            #update_datetime = availability.get('update_datetime', 'N/A')
            carpark_info = availability.get('carpark_info', [])
            
            # Format distance display
            if distance_km < 0.1:
                distance_str = f"{distance_km * 1000:.0f}m"
            else:
                distance_str = f"{distance_km:.2f}km"
            
            # Store carpark availability data
            carpark_data = {
                'carpark_number': carpark_number,
                'address': address,
                'distance': distance_str,
                'availability': []
            }
            
            # Build availability data for side panel
            for lot_info in carpark_info:
                lot_type = lot_info.get('lot_type', 'N/A')
                print(f"Processing lot type: {lot_type} for {carpark_number}")
                total_lots = lot_info.get('total_lots', '0')
                lots_available = lot_info.get('lots_available', '0')
                
                # Calculate percentage and color
                try:
                    total = int(total_lots)
                    available = int(lots_available)
                    percentage = (available / total * 100) if total > 0 else 0
                    status_color = "#4ade80" if percentage > 20 else "#fbbf24" if percentage > 0 else "#ef4444"
                except (ValueError, TypeError):
                    percentage = 0
                    status_color = "#999"
                    available = 0
                
                carpark_data['availability'].append({
                    'type': lot_type.upper(),
                    'type_name': format_lot_type_display(lot_type),
                    'available': available,
                    'total': total,
                    'percentage': percentage,
                    'color': status_color
                })
            
            # Build availability display for card
            availability_elements = []
            for avail_info in carpark_data['availability']:
                # Get first character safely (default to '?' if empty string)
                type_initial = (avail_info['type_name'][0]
                                if avail_info['type_name'] else '?')
                availability_elements.append(
                    html.Div(
                        [
                            html.Span(
                                f"{type_initial}: ",
                                style={
                                    "fontSize": "9px",
                                    "color": "#999",
                                }
                            ),
                            html.Span(
                                f"{avail_info['available']}/{avail_info['total']}",
                                style={
                                    "fontSize": "9px",
                                    "color": avail_info['color'],
                                    "fontWeight": "bold",
                                }
                            ),
                        ],
                        style={"marginBottom": "2px"}
                    )
                )

            # Create card with availability info on the right
            carpark_card = html.Div(
                [
                    # Left side: Carpark info
                    html.Div(
                        [
                            # Carpark ID label and distance
                            html.Div(
                                [
                                    html.Span(
                                        carpark_number,
                                        style={
                                            "display": "inline-block",
                                            "padding": "2px 8px",
                                            "backgroundColor": "#2196F3",
                                            "color": "#fff",
                                            "borderRadius": "4px",
                                            "fontSize": "11px",
                                            "fontWeight": "bold",
                                            "marginRight": "8px",
                                        }
                                    ),
                                    html.Span(
                                        f"{distance_str}",
                                        style={
                                            "fontSize": "10px",
                                            "color": "#999",
                                        }
                                    ),
                                ],
                                style={
                                    "marginBottom": "3px",
                                    "display": "flex",
                                    "alignItems": "center"
                                }
                            ),
                            # Address
                            html.Div(
                                address if address != 'N/A' else 'No address',
                                style={
                                    "fontSize": "9px",
                                    "color": "#ccc",
                                    "overflow": "hidden",
                                    "textOverflow": "ellipsis",
                                    "whiteSpace": "nowrap"
                                }
                            ),
                        ],
                        style={"flex": "1", "minWidth": "0"}
                    ),
                    # Right side: Availability info
                    html.Div(
                        availability_elements if availability_elements else html.Span("No data", style={"fontSize": "9px", "color": "#666"}),
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "alignItems": "flex-end",
                            "justifyContent": "center",
                            "marginLeft": "8px"
                        }
                    )
                ],
                style={
                    "padding": "6px 8px",
                    "marginBottom": "4px",
                    "backgroundColor": "#000000",
                    "borderRadius": "4px",
                    "borderLeft": "3px solid #60a5fa",
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "8px"
                }
            )
            
            carpark_cards.append(carpark_card)
        
        # Return cards and markers
        cards_output = carpark_cards if carpark_cards else html.P(
            "No carpark data available",
            style={
                "textAlign": "center",
                "padding": "15px",
                "color": "#999",
                "fontSize": "12px"
            }
        )
        
        return cards_output, markers