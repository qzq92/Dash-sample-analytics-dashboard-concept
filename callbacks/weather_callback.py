"""
Callback functions for handling weather forecast API integration.
References:
- 2-hour forecast: https://data.gov.sg/datasets?query=weather&resultId=d_3f9e064e25005b0e42969944ccaf2e7a
- 24-hour forecast: https://data.gov.sg/datasets?query=weather&resultId=d_ce2eb1e307bda31993c533285834ef2b
"""
import os
import requests
from dash import Input, Output, html
from dotenv import load_dotenv

load_dotenv(override=True)


def fetch_weather_forecast_2h():
    """
    Fetch 2-hour weather forecast from data.gov.sg API.
    Reference: https://data.gov.sg/datasets?query=weather&resultId=d_3f9e064e25005b0e42969944ccaf2e7a

    Returns:
        Dictionary containing forecast data or None if error
    """
    api_key = os.getenv('DATA_GOV_API')
    if not api_key:
        print("DATA_GOV_API environment variable not set")
        return None

    url = "https://api.data.gov.sg/v1/environment/2-hour-weather-forecast"
    headers = {
        "X-API-Key": api_key,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        print(f"2-hour weather forecast API failed: status={res.status_code}")
    except (requests.exceptions.RequestException, ValueError) as error:
        print(f"Error calling 2-hour weather forecast API: {error}")
    return None


def fetch_weather_forecast_24h():
    """
    Fetch 24-hour weather forecast from data.gov.sg API.
    Reference: https://data.gov.sg/datasets?query=weather&resultId=d_ce2eb1e307bda31993c533285834ef2b

    Returns:
        Dictionary containing forecast data or None if error
    """
    api_key = os.getenv('DATA_GOV_API')
    if not api_key:
        print("DATA_GOV_API environment variable not set")
        return None

    url = "https://api.data.gov.sg/v1/environment/24-hour-weather-forecast"
    headers = {
        "X-API-Key": api_key,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        print(f"24-hour weather forecast API failed: status={res.status_code}")
    except (requests.exceptions.RequestException, ValueError) as error:
        print(f"Error calling 24-hour weather forecast API: {error}")
    return None


def format_weather_2h(data):
    """
    Format 2-hour weather forecast data for display.
    Arranges towns in a grid layout with multiple columns per row.
    Example: 48 towns arranged in 4 rows of 12 columns each.

    Args:
        data: JSON response from 2-hour weather forecast API

    Returns:
        HTML Div containing grid of town forecast divs arranged in rows and columns
    """
    if not data or 'items' not in data or not data['items']:
        return html.P("No data available", style={"padding": "10px", "color": "#999"})

    forecast_item = data['items'][0]

    # Get forecasts
    forecasts = forecast_item.get('forecasts', [])

    if not forecasts:
        return html.P("No forecast data available", style={"padding": "10px", "color": "#999"})

    # Calculate grid layout: determine columns per row based on total items
    total_items = len(forecasts)
    
    # Calculate optimal columns per row (aim for 4 rows if 48 items = 12 columns)
    # For other counts, calculate to get approximately 4 rows
    if total_items <= 12:
        cols_per_row = total_items
    elif total_items <= 24:
        cols_per_row = 12
    elif total_items <= 48:
        cols_per_row = 12  # 4 rows of 12
    else:
        # For more than 48, calculate to get approximately 4-6 rows
        cols_per_row = max(12, total_items // 4)
    
    # Create town divs
    town_divs = []
    for forecast in forecasts:
        area_name = forecast.get('area', 'Unknown')
        forecast_text = forecast.get('forecast', 'N/A')

        town_divs.append(
            html.Div(
                [
                    html.Div(
                        area_name,
                        style={
                            "fontWeight": "700",
                            "fontSize": "14px",
                            "color": "#4CAF50",
                            "marginBottom": "4px"
                        }
                    ),
                    html.Div(
                        forecast_text,
                        style={
                            "color": "#ddd",
                            "fontSize": "12px",
                            "lineHeight": "1.3"
                        }
                    )
                ],
                style={
                    "padding": "10px 12px",
                    "borderRadius": "4px",
                    "backgroundColor": "#3a4a5a",
                    "border": "1px solid #555",
                }
            )
        )

    # Return grid container with all town divs
    return html.Div(
        town_divs,
        style={
            "display": "grid",
            "gridTemplateColumns": f"repeat({cols_per_row}, 1fr)",
            "gap": "8px",
            "width": "100%",
        }
    )


def format_weather_24h(data):
    """
    Format 24-hour weather forecast data for display.

    Args:
        data: JSON response from 24-hour weather forecast API

    Returns:
        List of HTML elements for display
    """
    if not data or 'items' not in data or not data['items']:
        return [html.P("No data available", style={"padding": "10px", "color": "#999"})]

    items = []
    forecast_item = data['items'][0]

    # Get general forecast
    general_forecast = forecast_item.get('general', {})
    relative_humidity = forecast_item.get('relative_humidity', {})
    temperature = forecast_item.get('temperature', {})
    wind = forecast_item.get('wind', {})

    # Display general forecast
    if general_forecast:
        forecast_text = general_forecast.get('forecast', 'N/A')
        items.append(
            html.Div(
                [
                    html.Strong("General Forecast", style={"color": "#4CAF50", "fontSize": "16px"}),
                    html.Br(),
                    html.Span(forecast_text, style={"color": "#ddd", "fontSize": "14px"})
                ],
                style={
                    "padding": "10px",
                    "margin": "5px 0",
                    "borderBottom": "2px solid #444",
                    "borderRadius": "3px",
                }
            )
        )

    # Display temperature
    if temperature:
        temp_high = temperature.get('high', 'N/A')
        temp_low = temperature.get('low', 'N/A')
        items.append(
            html.Div(
                [
                    html.Strong("Temperature", style={"color": "#FF9800"}),
                    html.Br(),
                    html.Span(f"High: {temp_high}°C | Low: {temp_low}°C", style={"color": "#ddd", "fontSize": "14px"})
                ],
                style={
                    "padding": "8px",
                    "margin": "5px 0",
                    "borderBottom": "1px solid #444",
                    "borderRadius": "3px",
                }
            )
        )

    # Display relative humidity
    if relative_humidity:
        rh_high = relative_humidity.get('high', 'N/A')
        rh_low = relative_humidity.get('low', 'N/A')
        items.append(
            html.Div(
                [
                    html.Strong("Relative Humidity", style={"color": "#2196F3"}),
                    html.Br(),
                    html.Span(f"High: {rh_high}% | Low: {rh_low}%", style={"color": "#ddd", "fontSize": "14px"})
                ],
                style={
                    "padding": "8px",
                    "margin": "5px 0",
                    "borderBottom": "1px solid #444",
                    "borderRadius": "3px",
                }
            )
        )

    # Display wind
    if wind:
        wind_speed = wind.get('speed', {})
        wind_direction = wind.get('direction', 'N/A')
        speed_low = wind_speed.get('low', 'N/A')
        speed_high = wind_speed.get('high', 'N/A')
        items.append(
            html.Div(
                [
                    html.Strong("Wind", style={"color": "#9C27B0"}),
                    html.Br(),
                    html.Span(f"Speed: {speed_low}-{speed_high} km/h | Direction: {wind_direction}",
                             style={"color": "#ddd", "fontSize": "14px"})
                ],
                style={
                    "padding": "8px",
                    "margin": "5px 0",
                    "borderBottom": "1px solid #444",
                    "borderRadius": "3px",
                }
            )
        )

    return items if items else [html.P("No forecast data available", style={"padding": "10px", "color": "#999"})]


def register_weather_callbacks(app):
    """
    Register weather forecast callbacks for the dashboard.

    Args:
        app: Dash app instance
    """
    @app.callback(
        Output('weather-2h-content', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_weather_forecast_2h(n_intervals):
        """
        Update 2-hour weather forecast display periodically.

        Args:
            n_intervals: Number of intervals (from dcc.Interval component)

        Returns:
            HTML content for 2-hour forecast (towns arranged in column)
        """
        # n_intervals is required by the callback but not used directly
        _ = n_intervals

        # Fetch 2-hour forecast
        weather_2h_data = fetch_weather_forecast_2h()
        weather_2h_content = format_weather_2h(weather_2h_data)

        return weather_2h_content

