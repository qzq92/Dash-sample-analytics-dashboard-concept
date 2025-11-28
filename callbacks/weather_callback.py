"""
Callback functions for handling weather forecast API integration.
References:
- 2-hour forecast:
  https://data.gov.sg/datasets?query=weather&resultId=d_3f9e064e25005b0e42969944ccaf2e7a
- 24-hour forecast:
  https://data.gov.sg/datasets?query=weather&resultId=d_ce2eb1e307bda31993c533285834ef2b
"""
import os
import requests
from dash import Input, Output, html
from dotenv import load_dotenv
from conf.weather_icons import get_weather_icon

load_dotenv(override=True)


def fetch_weather_forecast_2h():
    """
    Fetch 2-hour weather forecast from data.gov.sg API.
    Reference:
    https://data.gov.sg/datasets?query=weather&resultId=d_3f9e064e25005b0e42969944ccaf2e7a

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

    # Create town divs
    town_divs = []
    for forecast in forecasts:
        area_name = forecast.get('area', 'Unknown')
        forecast_text = forecast.get('forecast', 'N/A')
        weather_icon = get_weather_icon(forecast_text)

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
                        [
                            html.Span(
                                weather_icon,
                                style={"marginRight": "6px", "fontSize": "14px"}
                            ),
                            html.Span(forecast_text)
                        ],
                        style={
                            "color": "#ddd",
                            "fontSize": "12px",
                            "lineHeight": "1.3",
                            "display": "flex",
                            "alignItems": "center"
                        }
                    )
                ],
                style={
                    "padding": "10px 12px",
                    "borderRadius": "4px",
                    "backgroundColor": "#3a4a5a",
                    "border": "1px solid #555",
                    "width": "100%",
                }
            )
        )

    # Return scrollable column container with all town divs
    return html.Div(
        town_divs,
        style={
            "display": "flex",
            "flexDirection": "column",
            "gap": "8px",
            "width": "100%",
            "overflowX": "hidden",
            "overflowY": "auto",
            "padding": "5px",
        }
    )


def _create_weather_card(title, emoji, color, value):
    """
    Helper to create a weather info card with large value display.

    Args:
        title: Card title
        emoji: Icon/emoji for the card
        color: Theme color for the card
        value: Main value to display (e.g., "23 °C - 33 °C")
    """
    return html.Div(
        [
            html.Div(
                f"{emoji} {title}",
                style={
                    "fontSize": "14px",
                    "fontWeight": "700",
                    "color": color,
                    "marginBottom": "12px",
                    "textAlign": "center"
                }
            ),
            html.Div(
                value,
                style={
                    "fontSize": "24px",
                    "fontWeight": "700",
                    "color": color,
                    "textAlign": "center",
                    "whiteSpace": "nowrap"
                }
            )
        ],
        style={
            "flex": "1",
            "padding": "15px",
            "backgroundColor": "#3a4a5a",
            "borderRadius": "8px",
            "border": "1px solid #555",
            "minWidth": "120px"
        }
    )


def _build_weather_grid(general):
    """
    Build weather info cards from general forecast data.
    Returns 4 cards: Temperature, Humidity, Wind, and General Forecast.
    Values shown as ranges with units beside each value (e.g., "23 °C - 33 °C").
    """
    grid_items = []

    # Temperature card: "23 °C - 33 °C"
    temp = general.get('temperature', {})
    if temp:
        grid_items.append(_create_weather_card(
            "Temperature", "🌡️", "#FF9800",
            f"{temp.get('low', 'N/A')} °C - {temp.get('high', 'N/A')} °C"
        ))

    # Humidity card: "65 % - 95 %"
    hum = general.get('relativeHumidity', {})
    if hum:
        grid_items.append(_create_weather_card(
            "Humidity", "💧", "#2196F3",
            f"{hum.get('low', 'N/A')} % - {hum.get('high', 'N/A')} %"
        ))

    # Wind card: "15 km/h - 35 km/h SW"
    wind = general.get('wind', {})
    if wind:
        spd = wind.get('speed', {})
        direction = wind.get('direction', '')
        dir_text = f" {direction}" if direction else ""
        grid_items.append(_create_weather_card(
            "Wind", "🌬️", "#9C27B0",
            f"{spd.get('low', 'N/A')} - {spd.get('high', 'N/A')} km/h{dir_text}"
        ))

    # General Forecast card
    forecast = general.get('forecast', {})
    if forecast:
        text = forecast.get('text', 'N/A')
        grid_items.append(_create_weather_card(
            "Forecast", get_weather_icon(text), "#4CAF50", text
        ))

    return grid_items


def fetch_and_format_weather_24h():
    """
    Fetch and format 24-hour weather forecast data for main dashboard display.
    Shows temperature, relative humidity, general forecast and wind information.
    Reference:
    https://data.gov.sg/datasets?query=weather&resultId=d_ce2eb1e307bda31993c533285834ef2b

    API structure: data.records[0].general contains all forecast info:
    - temperature: {low, high, unit}
    - relativeHumidity: {low, high, unit}
    - forecast: {code, text}
    - validPeriod: {start, end, text}
    - wind: {speed: {low, high}, direction}

    Returns:
        HTML Div with structured forecast display
    """
    # Fetch data from API
    api_key = os.getenv('DATA_GOV_API')
    if not api_key:
        print("DATA_GOV_API environment variable not set")
        return html.P(
            "API key not configured",
            style={"padding": "10px", "color": "#999", "textAlign": "center"}
        )

    url = "https://api-open.data.gov.sg/v2/real-time/api/twenty-four-hr-forecast"
    headers = {
        "X-API-Key": api_key,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            print(f"24-hour weather forecast API failed: status={res.status_code}")
            return html.P(
                "Failed to fetch weather data",
                style={"padding": "10px", "color": "#999", "textAlign": "center"}
            )
        data = res.json()
    except (requests.exceptions.RequestException, ValueError) as error:
        print(f"Error calling 24-hour weather forecast API: {error}")
        return html.P(
            "Error fetching weather data",
            style={"padding": "10px", "color": "#999", "textAlign": "center"}
        )

    # Handle API structure: data.records[0].general
    records = data.get('data', {}).get('records', []) if data else []
    if not records:
        return html.P(
            "No data available",
            style={"padding": "10px", "color": "#999", "textAlign": "center"}
        )

    # Extract data from general key
    general = records[0].get('general', {})

    # Build weather info cards (4 cards: Temperature, Humidity, Wind, Forecast)
    grid_items = _build_weather_grid(general)

    if not grid_items:
        return html.P(
            "No forecast data available",
            style={"padding": "10px", "color": "#999", "textAlign": "center"}
        )

    # Return 2x2 grid layout
    return html.Div(
        grid_items,
        style={
            "display": "grid",
            "gridTemplateColumns": "1fr 1fr",
            "gridTemplateRows": "1fr 1fr",
            "gap": "10px",
            "width": "100%",
            "padding": "10px",
            "height": "100%",
        }
    )


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

    @app.callback(
        Output('weather-24h-content', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_weather_forecast_24h_main(n_intervals):
        """
        Update 24-hour weather forecast display on main dashboard periodically.

        Args:
            n_intervals: Number of intervals (from dcc.Interval component)

        Returns:
            HTML content for 24-hour forecast (temperature, humidity, forecast, wind)
        """
        # n_intervals is required by the callback but not used directly
        _ = n_intervals

        # Fetch and format 24-hour forecast
        return fetch_and_format_weather_24h()
