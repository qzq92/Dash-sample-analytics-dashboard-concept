"""
Callback functions for handling HDB Carpark Availability API integration.
Reference: https://data.gov.sg/datasets?query=carpark&resultId=d_ca933a644e55d34fe21f28b8052fac63
"""
import requests
import pandas as pd
import os
from dash.dependencies import Input, Output
from dash import html
from typing import List, Optional, Dict
from math import radians, sin, cos, asin, sqrt
from utils.coordinate_converter import convert_svy21_to_wgs84

# Cache for carpark location data
_carpark_locations_cache: Optional[pd.DataFrame] = None


def load_carpark_locations() -> pd.DataFrame:
    """
    Load carpark locations from CSV and convert SVY21 coordinates to WGS84 lat/lon.
    Caches the result for subsequent calls.
    
    Returns:
        DataFrame with carpark_number, latitude, longitude, and address columns
    """
    global _carpark_locations_cache
    
    if _carpark_locations_cache is not None:
        return _carpark_locations_cache
    
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'HDBCarparkInformation.csv')
    
    try:
        df = pd.read_csv(csv_path)
        
        # Convert SVY21 coordinates to WGS84
        coordinates = df.apply(
            lambda row: convert_svy21_to_wgs84(row['x_coord'], row['y_coord']),
            axis=1
        )
        
        # Extract lat and lon from tuples
        df['latitude'] = coordinates.apply(lambda x: x[0])
        df['longitude'] = coordinates.apply(lambda x: x[1])
        
        # Keep only necessary columns
        df = df[['car_park_no', 'latitude', 'longitude', 'address']].copy()
        df.columns = ['carpark_number', 'latitude', 'longitude', 'address']
        
        # Cache the result
        _carpark_locations_cache = df
        
        return df
    except Exception as e:
        print(f"Error loading carpark locations: {e}")
        return pd.DataFrame(columns=['carpark_number', 'latitude', 'longitude', 'address'])


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth in kilometers.
    
    Args:
        lat1, lon1: Latitude and longitude of first point in degrees
        lat2, lon2: Latitude and longitude of second point in degrees
    
    Returns:
        Distance in kilometers
    """
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Earth radius in kilometers
    r = 6371.0
    
    return c * r


def fetch_carpark_availability() -> Optional[dict]:
    """
    Fetch carpark availability data from HDB Carpark Availability API.
    
    Returns:
        Dictionary containing carpark data or None if request fails
    """
    api_url = "https://api.data.gov.sg/v1/transport/carpark-availability"
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching carpark availability: {e}")
        return None


def filter_carparks_by_distance(
    center_lat: float,
    center_lon: float,
    radius_m: float = 500.0
) -> List[Dict]:
    """
    Filter carparks within a specified radius (in meters) from the center point.
    
    Args:
        center_lat: Center latitude in degrees
        center_lon: Center longitude in degrees
        radius_m: Radius in meters (default: 500m)
    
    Returns:
        List of carpark dictionaries with distance information
    """
    # Load carpark locations
    carpark_locations = load_carpark_locations()
    
    if carpark_locations.empty:
        return []
    
    # Convert radius from meters to kilometers
    radius_km = radius_m / 1000.0
    
    # Calculate distances and filter
    results = []
    for _, row in carpark_locations.iterrows():
        try:
            carpark_lat = float(row['latitude'])
            carpark_lon = float(row['longitude'])
            
            # Calculate distance in kilometers
            distance_km = haversine_distance_km(center_lat, center_lon, carpark_lat, carpark_lon)
            
            # Filter by radius
            if distance_km <= radius_km:
                results.append({
                    'carpark_number': row['carpark_number'],
                    'latitude': carpark_lat,
                    'longitude': carpark_lon,
                    'address': row.get('address', ''),
                    'distance_km': distance_km
                })
        except (ValueError, TypeError) as e:
            print(f"Error processing carpark {row.get('carpark_number', 'unknown')}: {e}")
            continue
    
    # Sort by distance (closest first)
    results.sort(key=lambda x: x['distance_km'])
    
    return results


def format_lot_type_display(lot_type: str) -> str:
    """
    Format lot type code to readable format.
    
    Args:
        lot_type: Lot type code (e.g., 'C', 'Y', 'H', 'M')
    
    Returns:
        Formatted lot type name
    """
    lot_type_map = {
        'C': 'Car',
        'Y': 'Motorcycle',
        'H': 'Heavy Vehicle',
        'M': 'Motorcycle',
    }
    return lot_type_map.get(lot_type.upper(), lot_type.upper())


def register_carpark_callbacks(app):
    """
    Register carpark availability callbacks.
    
    This callback automatically finds and displays carparks within 500m of the map center,
    showing their availability and distance from the center.
    """
    
    @app.callback(
        Output('carpark-availability-panel', 'children'),
        Input('sg-map', 'center')
    )
    def update_carpark_availability(map_center):
        """
        Update carpark availability display based on map center location.
        Shows carparks within 500m of the map center.
        
        Args:
            map_center: List containing [latitude, longitude] of map center
        
        Returns:
            HTML Div containing carpark availability information
        """
        if not map_center or len(map_center) < 2:
            return html.Div(
                "Waiting for map to load...",
                style={
                    "padding": "10px",
                    "color": "#999",
                    "fontSize": "14px",
                    "fontStyle": "italic"
                }
            )
        
        try:
            center_lat = float(map_center[0])
            center_lon = float(map_center[1])
        except (ValueError, TypeError, IndexError):
            return html.Div(
                "Invalid map center coordinates",
                style={
                    "padding": "10px",
                    "color": "#ff6b6b",
                    "fontSize": "14px"
                }
            )
        
        # Find carparks within 500m
        nearby_carparks = filter_carparks_by_distance(center_lat, center_lon, radius_m=500.0)
        
        if not nearby_carparks:
            return html.Div(
                "No carparks found within 500m of map center",
                style={
                    "padding": "10px",
                    "color": "#999",
                    "fontSize": "14px",
                    "fontStyle": "italic"
                }
            )
        
        # Fetch availability data from API
        api_data = fetch_carpark_availability()
        
        if not api_data:
            return html.Div(
                "Error fetching carpark availability data. Please try again later.",
                style={
                    "padding": "10px",
                    "color": "#ff6b6b",
                    "fontSize": "14px"
                }
            )
        
        # Extract carpark data from API response
        items = api_data.get('items', [])
        if not items:
            return html.Div(
                "No carpark data available",
                style={
                    "padding": "10px",
                    "color": "#ff6b6b",
                    "fontSize": "14px"
                }
            )
        
        # Get carpark data from first item (latest timestamp)
        carpark_availability_data = items[0].get('carpark_data', [])
        
        # Create a lookup dictionary for availability data
        availability_lookup = {
            cp.get('carpark_number', '').upper(): cp
            for cp in carpark_availability_data
        }
        
        # Build display components for each nearby carpark
        carpark_cards = []
        
        for carpark in nearby_carparks:
            carpark_number = carpark['carpark_number']
            distance_km = carpark['distance_km']
            address = carpark.get('address', 'N/A')
            
            # Get availability data
            availability = availability_lookup.get(carpark_number.upper(), {})
            update_datetime = availability.get('update_datetime', 'N/A')
            carpark_info = availability.get('carpark_info', [])
            
            # Build lot type information
            lot_info_items = []
            for lot_info in carpark_info:
                lot_type = lot_info.get('lot_type', 'N/A')
                total_lots = lot_info.get('total_lots', '0')
                lots_available = lot_info.get('lots_available', '0')
                
                # Calculate percentage available
                try:
                    total = int(total_lots)
                    available = int(lots_available)
                    percentage = (available / total * 100) if total > 0 else 0
                    status_color = "#4ade80" if percentage > 20 else "#fbbf24" if percentage > 0 else "#ef4444"
                except (ValueError, TypeError):
                    percentage = 0
                    status_color = "#999"
                
                lot_info_items.append(
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        format_lot_type_display(lot_type),
                                        style={
                                            "fontWeight": "600",
                                            "fontSize": "13px",
                                            "color": "#fff"
                                        }
                                    ),
                                    html.Span(
                                        f"{lots_available}/{total_lots}",
                                        style={
                                            "marginLeft": "8px",
                                            "fontSize": "12px",
                                            "color": status_color,
                                            "fontWeight": "500"
                                        }
                                    ),
                                ],
                                style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}
                            ),
                            html.Div(
                                f"{percentage:.0f}% available" if percentage > 0 else "Full",
                                style={
                                    "fontSize": "11px",
                                    "color": "#999",
                                    "marginTop": "2px"
                                }
                            )
                        ],
                        style={
                            "padding": "6px 8px",
                            "borderBottom": "1px solid #333",
                            "marginBottom": "4px"
                        }
                    )
                )
            
            # Format distance display
            if distance_km < 0.1:
                distance_str = f"{distance_km * 1000:.0f}m"
            else:
                distance_str = f"{distance_km:.2f}km"
            
            # Create card for this carpark
            carpark_card = html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        f"Carpark {carpark_number}",
                                        style={
                                            "fontWeight": "700",
                                            "fontSize": "15px",
                                            "color": "#fff"
                                        }
                                    ),
                                    html.Span(
                                        f" • {distance_str}",
                                        style={
                                            "fontWeight": "600",
                                            "fontSize": "13px",
                                            "color": "#60a5fa",
                                            "marginLeft": "6px"
                                        }
                                    ),
                                ],
                                style={"display": "flex", "alignItems": "center"}
                            ),
                            html.Div(
                                address if address != 'N/A' else '',
                                style={
                                    "fontSize": "11px",
                                    "color": "#999",
                                    "marginTop": "2px",
                                    "maxWidth": "100%",
                                    "overflow": "hidden",
                                    "textOverflow": "ellipsis",
                                    "whiteSpace": "nowrap"
                                }
                            ),
                            html.Div(
                                f"Updated: {update_datetime}" if update_datetime != 'N/A' else "No availability data",
                                style={
                                    "fontSize": "10px",
                                    "color": "#666",
                                    "marginTop": "2px"
                                }
                            )
                        ],
                        style={
                            "padding": "8px 10px",
                            "backgroundColor": "#2c3e50",
                            "borderRadius": "4px 4px 0 0",
                            "borderBottom": "1px solid #444"
                        }
                    ),
                    html.Div(
                        lot_info_items if lot_info_items else [
                            html.Div(
                                "No lot information available",
                                style={
                                    "padding": "8px",
                                    "color": "#999",
                                    "fontSize": "12px"
                                }
                            )
                        ],
                        style={
                            "padding": "4px",
                            "backgroundColor": "#1a1a1a",
                            "borderRadius": "0 0 4px 4px"
                        }
                    )
                ],
                style={
                    "marginBottom": "12px",
                    "borderRadius": "4px",
                    "overflow": "hidden"
                }
            )
            
            carpark_cards.append(carpark_card)
        
        # Return header and all carpark cards
        header = html.Div(
            f"Carpark Availability (within 500m) - {len(nearby_carparks)} found",
            style={
                "marginTop": "12px",
                "marginBottom": "8px",
                "fontWeight": "700",
                "fontSize": "16px",
                "color": "#fff"
            }
        )
        
        return [header] + carpark_cards
