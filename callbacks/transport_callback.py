"""
Callback functions for handling transport information.
Reference: https://api.data.gov.sg/v1/transport/taxi-availability
"""
from dash import Input, Output, State, html
import dash_leaflet as dl
from utils.async_fetcher import fetch_url

# API URL for taxi availability
TAXI_API_URL = "https://api.data.gov.sg/v1/transport/taxi-availability"


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
    def toggle_taxi_display(n_clicks, current_state):
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

