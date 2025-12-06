"""
Callbacks for fetching and displaying realtime exposure indexes data.
Handles UV Index, WBGT, and other exposure indexes.
"""
import os
import time
from datetime import datetime

import requests
import numpy as np
import plotly.graph_objects as go
import dash_leaflet as dl
from dash import html, dcc, Input, Output, State
from dotenv import load_dotenv

load_dotenv(override=True)



# WBGT Heat Stress color coding
WBGT_CATEGORIES = [
    (0, 28, "#3ea72d", "Low"),           # Green - Low risk
    (28, 30, "#fff300", "Moderate"),     # Yellow - Moderate risk
    (30, 32, "#f18b00", "High"),         # Orange - High risk
    (32, 34, "#e53210", "Very High"),    # Red - Very high risk
    (34, 999, "#1a1a1a", "Extreme"),       # Black - Extreme risk
]




def get_wbgt_category(value):
    """Get WBGT category info (color and label) based on value."""
    if value is None:
        return "#888", "Unknown"
    try:
        val = float(value)
    except (ValueError, TypeError):
        return "#888", "Unknown"
    for min_val, max_val, color, label in WBGT_CATEGORIES:
        if min_val <= val < max_val:
            return color, label
    # Check last category (extreme)
    if val >= 34:
        return "#b567a4", "Extreme"
    return "#888", "Unknown"


def fetch_uv_data():
    """Fetch UV index data from Data.gov.sg API."""
    url = "https://api-open.data.gov.sg/v2/real-time/api/uv"
    api_key = os.getenv('DATA_GOV_API')
    headers = {
        "X-Api-Key": api_key
    } if api_key else {}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def fetch_wbgt_data():
    """Fetch WBGT data from Data.gov.sg API."""
    url = "https://api-open.data.gov.sg/v2/real-time/api/weather?api=wbgt"
    api_key = os.getenv('DATA_GOV_API')
    headers = {
        "X-Api-Key": api_key
    } if api_key else {}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def _parse_timestamp(timestamp_str):
    """Parse ISO timestamp string to formatted string."""
    if not timestamp_str:
        return ""
    try:
        if "." in timestamp_str:
            parsed = datetime.fromisoformat(
                timestamp_str.replace("Z", "+00:00")
            )
        else:
            parsed = datetime.fromisoformat(timestamp_str)
        return parsed.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return timestamp_str




def _create_uv_chart(index_data):
    """Create UV index line chart using numpy and plotly."""
    times = []
    values = []

    # Sort chronologically
    sorted_data = sorted(index_data, key=lambda x: x.get('hour', ''))

    for item in sorted_data:
        ts_str = item.get('hour', '')
        val = item.get('value', 0)
        if ts_str:
            try:
                if "." in ts_str:
                    date_obj = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                else:
                    date_obj = datetime.fromisoformat(ts_str)
                times.append(date_obj)
                values.append(val)
            except (ValueError, TypeError):
                continue

    # Convert to numpy arrays as requested
    x_data = np.array(times)
    y_data = np.array(values)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_data,
        y=y_data,
        mode='lines+markers',
        name='UV Index',
        line=dict(color='#f18b00', width=2),
        marker=dict(size=6, color='#fff300', line=dict(width=1, color='#333')),
        hovertemplate='%{x|%H:%M}<br>UV Index: %{y}<extra></extra>'
    ))

    fig.update_layout(
        margin=dict(l=30, r=20, t=20, b=20),
        height=220,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ccc', size=10),
        xaxis=dict(
            showgrid=False,
            tickformat='%H:%M',
            linecolor='#555',
            showline=True
        ),
        yaxis=dict(
            title='UV Index',
            showgrid=True,
            gridcolor='#444',
            zeroline=False,
            rangemode='tozero'
        )
    )

    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False},
        style={'width': '100%'}
    )




def format_uv_display(data):
    """Format UV data for display."""
    if not data or data.get("code") != 0:
        return html.P(
            "Error retrieving UV data",
            style={"color": "#ff6b6b", "textAlign": "center"}
        )

    records = data.get("data", {}).get("records", [])
    if not records:
        return html.P(
            "No UV data available",
            style={"color": "#ccc", "textAlign": "center"}
        )

    record = records[0]
    index_data = record.get("index", [])
    update_time_str = _parse_timestamp(record.get("updatedTimestamp", ""))

    if not index_data:
        return html.P(
            "No UV readings available",
            style={"color": "#ccc", "textAlign": "center"}
        )

    uv_chart = _create_uv_chart(index_data)

    return html.Div(
        children=[
            html.Div(
                "Hourly Trend",
                style={
                    "color": "#fff",
                    "fontSize": "14px",
                    "fontWeight": "600",
                    "marginBottom": "8px",
                    "paddingLeft": "8px",
                }
            ),
            html.Div(
                style={
                    "backgroundColor": "#3a4a5a",
                    "borderRadius": "6px",
                    "padding": "5px",
                    "overflow": "hidden",
                },
                children=[uv_chart]
            ),
            html.Div(
                f"Updated: {update_time_str}",
                style={
                    "textAlign": "center",
                    "color": "#888",
                    "fontSize": "11px",
                    "marginTop": "10px",
                    "fontStyle": "italic",
                }
            ),
        ]
    )


def _create_wbgt_row(name, wbgt, heat_stress):
    """Create a single WBGT reading row."""
    color, _ = get_wbgt_category(wbgt)

    return html.Div(
        style={
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "center",
            "padding": "4px 8px",
            "backgroundColor": "#3a4a5a",
            "borderRadius": "4px",
            "marginBottom": "4px",
        },
        children=[
            html.Span(
                name,
                style={
                    "fontSize": "11px",
                    "color": "#ccc",
                    "flex": "1",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis",
                    "whiteSpace": "nowrap",
                    "marginRight": "10px",
                }
            ),
            html.Span(
                style={"display": "flex", "alignItems": "center", "gap": "8px"},
                children=[
                    html.Span(
                        heat_stress,
                        style={
                            "color": color,
                            "fontSize": "11px",
                            "fontWeight": "500",
                        }
                    ),
                    html.Span(
                        f"{wbgt}°C",
                        style={
                            "color": color,
                            "fontWeight": "600",
                            "fontSize": "12px",
                            "minWidth": "50px",
                            "textAlign": "right",
                        }
                    ),
                ]
            ),
        ]
    )


def format_wbgt_display(data):
    """Format WBGT data for display."""
    # Check if data is None or empty dict
    if not data:
        return html.P(
            "Error retrieving WBGT data",
            style={"color": "#ff6b6b", "textAlign": "center"}
        )

    # Handle case where code might be missing or different
    if data.get("code") not in [0, 1]:
        print(f"WBGT API Error Code: {data.get('code')}")
        return html.P(
            f"Error retrieving WBGT data (Code: {data.get('code')})",
            style={"color": "#ff6b6b", "textAlign": "center"}
        )

    records = data.get("data", {}).get("records", [])
    if not records:
        return html.P(
            "No WBGT data available",
            style={"color": "#ccc", "textAlign": "center"}
        )

    record = records[0]
    item = record.get("item", {})
    readings = item.get("readings", [])
    update_time_str = _parse_timestamp(record.get("updatedTimestamp", ""))

    if not readings:
        return html.P(
            "No WBGT readings available",
            style={"color": "#ccc", "textAlign": "center"}
        )

    # Sort readings alphabetically by station name
    sorted_readings = sorted(
        readings,
        key=lambda x: x.get("station", {}).get("name", "")
    )

    wbgt_rows = [
        _create_wbgt_row(
            r.get("station", {}).get("name", "Unknown"),
            r.get("wbgt", "N/A"),
            r.get("heatStress", "Unknown")
        )
        for r in sorted_readings
    ]

    return html.Div(
        children=[
            html.Div(
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "flex": "1",
                    "overflowY": "auto",
                    "overflowX": "hidden",
                    "minHeight": "0",
                },
                children=wbgt_rows
            ),
            html.Div(
                f"Updated: {update_time_str}",
                style={
                    "textAlign": "center",
                    "color": "#888",
                    "fontSize": "11px",
                    "marginTop": "10px",
                    "fontStyle": "italic",
                    "flexShrink": "0",
                }
            ),
        ],
        style={
            "display": "flex",
            "flexDirection": "column",
            "height": "100%",
            "overflow": "hidden",
        }
    )


def _create_single_wbgt_marker(reading):
    """Create a single WBGT map marker from reading data."""
    location = reading.get("location", {})
    # API response uses 'latitude' and 'longtitude' (typo in API)
    lat = location.get("latitude")
    lon = location.get("longtitude")  # Handle API typo

    # If not found, try correct spelling just in case API gets fixed
    if lon is None:
        lon = location.get("longitude")

    if not lat or not lon:
        return None

    try:
        lat, lon = float(lat), float(lon)
    except (ValueError, TypeError):
        return None

    station = reading.get("station", {})
    name = station.get("name", "Unknown")
    wbgt = reading.get("wbgt", "N/A")
    heat_stress = reading.get("heatStress", "Unknown")
    color, _ = get_wbgt_category(wbgt)

    return dl.DivMarker(
        id=f"wbgt-{station.get('id', 'unknown')}",
        position=[lat, lon],
        iconOptions={
            "className": "wbgt-marker",
            "html": f'''
                <div style="
                    background-color: {color};
                    width: 14px;
                    height: 14px;
                    border-radius: 50%;
                    border: 2px solid white;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                "></div>
            ''',
            "iconSize": [14, 14],
            "iconAnchor": [7, 7],
        },
        children=[
            dl.Tooltip(
                f"{name}: {wbgt}°C ({heat_stress})",
                permanent=False,
                direction="top"
            )
        ]
    )


def create_wbgt_markers(data):
    """Create map markers for WBGT stations."""
    if not data or data.get("code") != 0:
        return []

    records = data.get("data", {}).get("records", [])
    if not records:
        return []

    readings = records[0].get("item", {}).get("readings", [])
    markers = [_create_single_wbgt_marker(r) for r in readings]
    return [m for m in markers if m is not None]


def register_weather_indices_callbacks(app):
    """
    Register callbacks for realtime exposure indexes page.

    Args:
        app: Dash app instance
    """
    @app.callback(
        Output('uv-index-content', 'children'),
        Input('weather-indices-interval', 'n_intervals')
    )
    def update_uv_index(_n_intervals):
        """Update UV index display."""
        data = fetch_uv_data()
        return format_uv_display(data)

    @app.callback(
        Output('wbgt-index-content', 'children'),
        Input('weather-indices-interval', 'n_intervals')
    )
    def update_wbgt_index(_n_intervals):
        """Update WBGT display."""
        data = fetch_wbgt_data()
        return format_wbgt_display(data)

    @app.callback(
        [Output('exposure-marker-type', 'data'),
         Output('wbgt-map-toggle', 'style')],
        Input('wbgt-map-toggle', 'n_clicks'),
        State('exposure-marker-type', 'data'),
        prevent_initial_call=True
    )
    def toggle_wbgt_markers(n_clicks, current_data):
        """Toggle WBGT markers on map."""
        if not n_clicks:
            return current_data, _get_toggle_style(False)

        current_type = current_data.get('type') if current_data else None

        if current_type == 'wbgt':
            # Turn off
            new_data = {'type': None, 'ts': time.time()}
            return new_data, _get_toggle_style(False)

        # Turn on
        new_data = {'type': 'wbgt', 'ts': time.time()}
        return new_data, _get_toggle_style(True)

    @app.callback(
        Output('weather-indices-markers', 'children'),
        Input('exposure-marker-type', 'data')
    )
    def update_exposure_map_markers(marker_data):
        """Update map markers based on selected type."""
        if not marker_data:
            return []

        marker_type = marker_data.get('type')
        if marker_type == 'wbgt':
            data = fetch_wbgt_data()
            return create_wbgt_markers(data)

        return []


def _get_toggle_style(active):
    """Get button style based on active state."""
    if active:
        return {
            "backgroundColor": "#f18b00",
            "border": "1px solid #f18b00",
            "borderRadius": "4px",
            "color": "#fff",
            "cursor": "pointer",
            "padding": "4px 8px",
            "fontSize": "14px",
        }
    return {
        "backgroundColor": "transparent",
        "border": "1px solid #6a7a8a",
        "borderRadius": "4px",
        "color": "#ccc",
        "cursor": "pointer",
        "padding": "4px 8px",
        "fontSize": "14px",
    }
