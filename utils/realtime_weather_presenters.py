"""Small reusable realtime weather presentation helpers."""

from typing import Any, Dict, List, Optional

from dash import html
import dash_leaflet as dl


def create_reading_div(name: str, display_value: str, color: str) -> html.Div:
    """Create a compact station reading row."""
    return html.Div(
        [
            html.Span(name, style={"color": "#fff", "fontSize": "0.75rem"}),
            html.Span(display_value, style={"color": color, "fontSize": "0.75rem", "fontWeight": "600"}),
        ],
        style={
            "display": "flex",
            "justifyContent": "space-between",
            "gap": "0.5rem",
            "padding": "0.25rem 0",
            "borderBottom": "0.0625rem solid #3a4a5a",
        },
    )


def build_grid_content(reading_divs: List[html.Div], timestamp: str) -> html.Div:
    """Create the common scrollable reading grid container."""
    return html.Div(
        [
            html.Div(reading_divs, style={"overflowY": "auto", "flex": "1"}),
            html.Div(
                f"Updated: {timestamp}" if timestamp else "",
                style={"color": "#888", "fontSize": "0.6875rem", "textAlign": "center", "marginTop": "0.5rem"},
            ),
        ],
        style={"height": "100%", "display": "flex", "flexDirection": "column"},
    )


def get_error_div(message: str = "Error loading realtime weather data") -> html.Div:
    """Create a standard weather error display."""
    return html.Div(message, style={"color": "#ff6b6b", "textAlign": "center", "padding": "1rem"})


def create_textbox_marker(
    position: List[float],
    name: str,
    value: str,
    color: str,
    marker_id: Optional[Dict[str, Any]] = None,
) -> dl.DivMarker:
    """Create a text label marker for realtime weather maps."""
    return dl.DivMarker(
        id=marker_id,
        position=position,
        iconOptions={
            "html": (
                f"<div style='background:{color};color:#fff;border-radius:4px;"
                f"padding:2px 6px;font-size:11px;white-space:nowrap;'>{value}</div>"
            ),
            "className": "weather-textbox-marker",
        },
        children=[dl.Tooltip(name)],
    )
