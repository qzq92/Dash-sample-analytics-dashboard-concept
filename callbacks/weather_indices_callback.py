"""
Callbacks for fetching and displaying realtime exposure indexes data.
Handles UV Index, WBGT, and other exposure indexes.

Uses ThreadPoolExecutor for async API fetching to improve performance.
"""
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import plotly.graph_objects as go
import dash_leaflet as dl
from dash import html, dcc, Input, Output, State
from utils.async_fetcher import fetch_url, get_default_headers

# Thread pool for async exposure index fetching
_exposure_executor = ThreadPoolExecutor(max_workers=5)

# API URLs
PSI_URL = "https://api-open.data.gov.sg/v2/real-time/api/psi"
UV_URL = "https://api-open.data.gov.sg/v2/real-time/api/uv"
WBGT_URL = "https://api-open.data.gov.sg/v2/real-time/api/weather?api=wbgt"


# PSI (Pollutant Standards Index) categories
PSI_CATEGORIES = [
    (0, 50, "#3ea72d", "Good"),
    (51, 100, "#fff300", "Moderate"),
    (101, 200, "#f18b00", "Unhealthy"),
    (201, 300, "#e53210", "Very Unhealthy"),
    (301, 999, "#b567a4", "Hazardous"),
]



# WBGT Heat Stress color coding
WBGT_CATEGORIES = [
    (0, 28, "#3ea72d", "Low"),           # Green - Low risk
    (28, 30, "#fff300", "Moderate"),     # Yellow - Moderate risk
    (30, 32, "#f18b00", "High"),         # Orange - High risk
    (32, 34, "#e53210", "Very High"),    # Red - Very high risk
    (34, 999, "#1a1a1a", "Extreme"),       # Black - Extreme risk
]




def get_psi_category(value):
    """Get PSI category info (color and label) based on value."""
    if value is None:
        return "#888", "Unknown"
    try:
        val = float(value)
    except (ValueError, TypeError):
        return "#888", "Unknown"
    for min_val, max_val, color, label in PSI_CATEGORIES:
        if min_val <= val <= max_val:
            return color, label
    return "#888", "Unknown"


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


# Pollutant units mapping
# SO₂, PM2.5, PM10, O₃, NO₂ are measured in µg/m³
# CO is measured in mg/m³
# PSI is an index (no unit)
POLLUTANT_UNITS = {
    "so2_twenty_four_hourly": "µg/m³",
    "pm25_twenty_four_hourly": "µg/m³",
    "pm10_twenty_four_hourly": "µg/m³",
    "o3_eight_hour_max": "µg/m³",
    "no2_one_hour_max": "µg/m³",
    "co_eight_hour_max": "mg/m³",
    "psi_twenty_four_hourly": "",  # PSI is an index, no unit
}


def _get_pollutant_unit(pollutant_key):
    """Get the unit of measurement for a pollutant."""
    return POLLUTANT_UNITS.get(pollutant_key, "")


def fetch_psi_data():
    """Fetch PSI data from Data.gov.sg API."""
    return fetch_url(PSI_URL, get_default_headers())


def fetch_psi_data_async():
    """
    Fetch PSI data asynchronously (returns Future).
    Call .result() to get the data when needed.
    """
    return _exposure_executor.submit(fetch_psi_data)


def fetch_uv_data():
    """Fetch UV index data from Data.gov.sg API."""
    return fetch_url(UV_URL, get_default_headers())


def fetch_uv_data_async():
    """
    Fetch UV data asynchronously (returns Future).
    Call .result() to get the data when needed.
    """
    return _exposure_executor.submit(fetch_uv_data)


def fetch_wbgt_data():
    """Fetch WBGT data from Data.gov.sg API."""
    return fetch_url(WBGT_URL, get_default_headers())


def fetch_wbgt_data_async():
    """
    Fetch WBGT data asynchronously (returns Future).
    Call .result() to get the data when needed.
    """
    return _exposure_executor.submit(fetch_wbgt_data)


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


def _build_pollutant_row_html(pollutant_key, pollutant_name, value):
    """Build HTML for a single pollutant row with unit."""
    unit = _get_pollutant_unit(pollutant_key)
    value_with_unit = f"{value} {unit}" if unit else str(value)

    if pollutant_key == "psi_twenty_four_hourly":
        color, category = get_psi_category(value)
        return (
            f'<div style="margin: 2px 0;">'
            f'{pollutant_name}: '
            f'<span style="color:{color};font-weight:bold;">{value}</span> '
            f'({category})'
            f'</div>'
        )
    return f'<div style="margin: 2px 0;">{pollutant_name}: {value_with_unit}</div>'


def _create_single_psi_marker(region_info, readings, pollutants):
    """Create a single PSI text box for a region."""
    region_name = region_info.get("name", "")
    label_location = region_info.get("labelLocation", {})
    lat = label_location.get("latitude")
    lon = label_location.get("longitude")

    if not lat or not lon or not region_name:
        return None

    # Build the pollutant values HTML
    pollutant_rows = []
    for pollutant_key, pollutant_name in pollutants:
        pollutant_data = readings.get(pollutant_key, {})
        value = pollutant_data.get(region_name)
        if value is not None:
            row_html = _build_pollutant_row_html(pollutant_key,
                                                  pollutant_name, value)
            pollutant_rows.append(row_html)

    pollutant_html = "".join(pollutant_rows)

    # Create text box HTML
    text_box_html = f'''
        <div style="
            background-color: rgba(74, 90, 106, 0.95);
            border: 2px solid #60a5fa;
            border-radius: 8px;
            padding: 8px 10px;
            min-width: 140px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        ">
            <div style="
                font-weight: bold;
                font-size: 12px;
                color: #60a5fa;
                margin-bottom: 4px;
                text-align: center;
                border-bottom: 1px solid #60a5fa;
                padding-bottom: 3px;
            ">{region_name.upper()}</div>
            <div style="
                font-size: 10px;
                color: #fff;
                line-height: 1.3;
            ">{pollutant_html}</div>
        </div>
    '''

    return dl.DivMarker(
        id=f"psi-{region_name}",
        position=[lat, lon],
        iconOptions={
            'className': 'psi-textbox',
            'html': text_box_html,
            'iconSize': [160, 130],
            'iconAnchor': [80, 65],
        }
    )


def create_psi_markers(data):
    """Create map markers for PSI regions with pollutant data in tooltips."""
    if not data or data.get("code") != 0:
        return []

    items = data.get("data", {}).get("items", [])
    region_metadata = data.get("data", {}).get("regionMetadata", [])

    if not items or not region_metadata:
        return []

    readings = items[0].get("readings", {})
    pollutants = [
        ("psi_twenty_four_hourly", "24H Avg PSI"),
        ("pm25_twenty_four_hourly", "24H Avg PM2.5"),
        ("pm10_twenty_four_hourly", "24H Avg PM10"),
        ("so2_twenty_four_hourly", "24H Avg SO₂"),
        ("co_eight_hour_max", "8H Avg CO"),
        ("o3_eight_hour_max", "8H Avg O₃"),
        ("no2_one_hour_max", "1H Max NO₂")
    ]

    markers = [
        _create_single_psi_marker(region_info, readings, pollutants)
        for region_info in region_metadata
    ]
    return [m for m in markers if m is not None]


def format_psi_display(data):
    """Format PSI data as a table with regions as rows and pollutants as columns."""
    if not data or data.get("code") != 0:
        return html.P(
            "Error retrieving PSI data",
            style={"color": "#ff6b6b", "textAlign": "center"}
        )

    items = data.get("data", {}).get("items", [])
    if not items:
        return html.P(
            "No PSI data available",
            style={"color": "#ccc", "textAlign": "center"}
        )

    readings = items[0].get("readings", {})
    update_time_str = _parse_timestamp(items[0].get("updatedTimestamp", ""))

    # Define pollutants and regions
    pollutants = [
        ("psi_twenty_four_hourly", "24H Mean PSI"),
        ("pm25_twenty_four_hourly", "24H Mean PM2.5 Particulate Matter"),
        ("pm10_twenty_four_hourly", "24H Mean PM10 Particulate Matter"),
        ("so2_twenty_four_hourly", "24H Mean Sulphur Dioxide"),
        ("co_eight_hour_max", "8H Mean Carbon Monoxide"),
        ("o3_eight_hour_max", "8H Mean Ozone"),
        ("no2_one_hour_max", "1H Max Nitrogen Dioxide")
    ]
    regions = ["north", "south", "east", "west", "central"]

    # Create table header
    header_row = html.Div(
        style={
            "display": "grid",
            "gridTemplateColumns": "70px repeat(7, 1fr)",
            "gap": "4px",
            "padding": "8px 4px",
            "backgroundColor": "#2a3a4a",
            "borderRadius": "4px 4px 0 0",
            "fontWeight": "bold",
        },
        children=[
            html.Div("Region", style={
                "fontSize": "9px",
                "color": "#60a5fa",
                "textAlign": "center"
            })
        ] + [
            html.Div(name, style={
                "fontSize": "9px",
                "color": "#60a5fa",
                "textAlign": "center"
            })
            for _, name in pollutants
        ]
    )

    # Create table rows for each region
    table_rows = []
    for region in regions:
        cells = [
            html.Div(
                region.capitalize(),
                style={
                    "fontSize": "10px",
                    "color": "#ccc",
                    "textAlign": "center",
                    "fontWeight": "600"
                }
            )
        ]

        # Add cell for each pollutant
        for pollutant_key, _ in pollutants:
            pollutant_data = readings.get(pollutant_key, {})
            value = pollutant_data.get(region)

            if value is not None:
                # Color code PSI values, use blue for others
                if pollutant_key == "psi_twenty_four_hourly":
                    color, _ = get_psi_category(value)
                else:
                    color = "#60a5fa"

                # Get unit for pollutant
                unit = _get_pollutant_unit(pollutant_key)
                display_value = f"{value} {unit}" if unit else str(value)

                cells.append(
                    html.Div(
                        display_value,
                        style={
                            "fontSize": "10px",
                            "color": color,
                            "textAlign": "center",
                            "fontWeight": "bold"
                        }
                    )
                )
            else:
                cells.append(
                    html.Div(
                        "-",
                        style={
                            "fontSize": "10px",
                            "color": "#666",
                            "textAlign": "center"
                        }
                    )
                )

        table_rows.append(
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "70px repeat(7, 1fr)",
                    "gap": "4px",
                    "padding": "8px 4px",
                    "backgroundColor": "#3a4a5a",
                    "borderBottom": "1px solid #2a3a4a",
                },
                children=cells
            )
        )

    return html.Div(
        children=[
            html.Div(
                style={
                    "backgroundColor": "#3a4a5a",
                    "borderRadius": "6px",
                    "overflow": "hidden"
                },
                children=[header_row] + table_rows
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
            )
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
    def toggle_wbgt_markers(_n_clicks, current_data):
        """Toggle WBGT markers on map."""
        current_type = current_data.get('type') if current_data else None

        if current_type == 'wbgt':
            # Turn off WBGT
            new_data = {'type': None, 'ts': time.time()}
            return new_data, _get_toggle_style(False)

        # Turn on WBGT
        new_data = {'type': 'wbgt', 'ts': time.time()}
        return new_data, _get_toggle_style(True)

    @app.callback(
        Output('weather-indices-markers', 'children'),
        Input('exposure-marker-type', 'data')
    )
    def update_exposure_map_markers(marker_data):
        """Update map markers based on selected type (WBGT only)."""
        if not marker_data:
            return []

        marker_type = marker_data.get('type')
        if marker_type == 'wbgt':
            data = fetch_wbgt_data()
            return create_wbgt_markers(data)

        return []

    @app.callback(
        Output('psi-markers', 'children'),
        Input('weather-indices-interval', 'n_intervals')
    )
    def update_psi_markers(_n_intervals):
        """Update PSI markers on map (always displayed)."""
        data = fetch_psi_data()
        return create_psi_markers(data)

    @app.callback(
        Output('psi-24h-content', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_main_page_psi(_n_intervals):
        """Update 24H PSI display on main page."""
        data = fetch_psi_data()
        return format_main_page_psi(data)


def format_main_page_psi(data):
    """Format 24H PSI data for compact display on main page."""
    if not data or data.get("code") != 0:
        return html.P(
            "Error loading PSI data",
            style={"color": "#ff6b6b", "textAlign": "center", "fontSize": "11px"}
        )

    items = data.get("data", {}).get("items", [])
    if not items:
        return html.P(
            "No PSI data available",
            style={"color": "#999", "textAlign": "center", "fontSize": "11px"}
        )

    readings = items[0].get("readings", {})
    psi_data = readings.get("psi_twenty_four_hourly", {})

    regions = ["north", "south", "east", "west", "central"]

    # Create compact row of PSI values
    psi_items = []
    for region in regions:
        value = psi_data.get(region)
        if value is not None:
            color, category = get_psi_category(value)
            psi_items.append(
                html.Div(
                    [
                        html.Div(
                            region.capitalize(),
                            style={
                                "fontSize": "10px",
                                "color": "#aaa",
                                "textAlign": "center",
                                "marginBottom": "2px",
                            }
                        ),
                        html.Div(
                            str(value),
                            style={
                                "fontSize": "16px",
                                "fontWeight": "bold",
                                "color": color,
                                "textAlign": "center",
                            }
                        ),
                        html.Div(
                            category,
                            style={
                                "fontSize": "9px",
                                "color": color,
                                "textAlign": "center",
                            }
                        ),
                    ],
                    style={
                        "flex": "1",
                        "padding": "4px",
                        "backgroundColor": "#1a2a3a",
                        "borderRadius": "4px",
                        "minWidth": "50px",
                    }
                )
            )

    return html.Div(
        psi_items,
        style={
            "display": "flex",
            "gap": "6px",
            "justifyContent": "space-between",
        }
    )


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
