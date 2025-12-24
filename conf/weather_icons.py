"""
Weather forecast icons configuration.
Maps forecast text descriptions to appropriate icons/emojis.
Reference: https://data.gov.sg/datasets?query=weather
"""
from typing import Optional

# Weather forecast icon mapping
# Keys are the forecast text values from the API
WEATHER_ICONS = {
    # Fair conditions
    "Fair": "☀️",
    "Fair (Day)": "🌞",
    "Fair (Night)": "🌙",
    "Fair and Warm": "🌤️",

    # Cloudy conditions
    "Partly Cloudy": "⛅",
    "Partly Cloudy (Day)": "🌤️",
    "Partly Cloudy (Night)": "☁️",
    "Cloudy": "☁️",

    # Hazy conditions
    "Hazy": "🌫️",
    "Slightly Hazy": "😶‍🌫️",

    # Wind and visibility
    "Windy": "💨",
    "Mist": "🌁",
    "Fog": "🌫️",

    # Rain conditions
    "Light Rain": "🌧️",
    "Moderate Rain": "🌧️",
    "Heavy Rain": "⛈️",

    # Showers
    "Passing Showers": "🌦️",
    "Light Showers": "🌦️",
    "Showers": "🌧️",
    "Heavy Showers": "⛈️",

    # Thundery conditions
    "Thundery Showers": "⛈️",
    "Heavy Thundery Showers": "🌩️",
    "Heavy Thundery Showers with Gusty Winds": "🌪️",
}

# Fallback icon for unknown forecast types
DEFAULT_ICON = "🌡️"


def get_weather_icon(forecast_text: Optional[str]) -> str:
    """
    Get the weather icon for a given forecast text.

    Args:
        forecast_text: The forecast description from the API

    Returns:
        String containing the appropriate weather icon/emoji
    """
    if not forecast_text:
        return DEFAULT_ICON
    return WEATHER_ICONS.get(forecast_text, DEFAULT_ICON)


def get_weather_icon_with_text(forecast_text: Optional[str]) -> str:
    """
    Get the weather icon combined with the forecast text.

    Args:
        forecast_text: The forecast description from the API

    Returns:
        String containing icon followed by forecast text
    """
    icon = get_weather_icon(forecast_text)
    return f"{icon} {forecast_text}" if forecast_text else f"{icon} Unknown"

