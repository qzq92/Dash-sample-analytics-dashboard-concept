"""
Component for the Pollutant & Exposure Indexes page.
Displays various exposure indexes across Singapore.
"""
from dash import html, dcc
import dash_leaflet as dl
from utils.map_utils import get_onemap_attribution


def weather_indices_page():
    """
    Create the Pollutant & Exposure Indexes page layout.
    Features: UV Index, WBGT, and other exposure indexes.

    Returns:
        HTML Div containing the Pollutant & Exposure Indexes section
    """
    # Singapore center coordinates
    sg_center = [1.36, 103.82]
    onemap_tiles_url = "https://www.onemap.gov.sg/maps/tiles/Night/{z}/{x}/{y}.png"
    fixed_zoom = 12
    onemap_attribution = get_onemap_attribution()

    # Map bounds to restrict view to Singapore area
    sg_bounds = [[1.1304753, 103.6020882], [1.492007, 104.145897]]

    return html.Div(
        id="weather-indices-page",
        style={
            "display": "none",  # Hidden by default
            "padding": "20px",
            "height": "calc(100vh - 120px)",
            "width": "100%",
        },
        children=[
            # Store for active marker type on map
            dcc.Store(id="exposure-marker-type", data={'type': None, 'ts': 0}),
            # Main content container: map on left, indices on right
            html.Div(
                id="weather-indices-content",
                style={
                    "display": "flex",
                    "gap": "10px",
                    "height": "calc(100% - 50px)",
                    "maxWidth": "1800px",
                    "margin": "0 auto",
                    "padding": "0 5px",
                },
                children=[
                    # Left side: Indices panels
                    html.Div(
                        id="weather-indices-panel",
                        style={
                            "flex": "2",
                            "minWidth": "300px",
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "10px",
                            "overflowY": "auto",
                        },
                        children=[
                            # UV Index card
                            html.Div(
                                id="uv-index-card",
                                style={
                                    "backgroundColor": "#4a5a6a",
                                    "borderRadius": "8px",
                                    "padding": "10px",
                                    "display": "flex",
                                    "flexDirection": "column",
                                },
                                children=[
                                    # Header with toggle button
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "alignItems": "center",
                                            "borderBottom": "1px solid #5a6a7a",
                                            "paddingBottom": "6px",
                                            "marginBottom": "8px",
                                        },
                                        children=[
                                            html.H5(
                                                "☀️ UV Index Today (Daylight hourly trend)",
                                                style={
                                                    "margin": "0",
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                }
                                            ),
                                            # Note: UV doesn't have station locations
                                        ]
                                    ),
                                    html.Div(
                                        id="uv-index-content",
                                        style={
                                            "flex": "1",
                                            "overflowY": "auto",
                                        },
                                        children=[
                                            html.P(
                                                "Loading UV data...",
                                                style={
                                                    "color": "#ccc",
                                                    "textAlign": "center",
                                                    "padding": "12px",
                                                }
                                            )
                                        ]
                                    ),
                                ]
                            ),
                            # WBGT (Wet Bulb Globe Temperature) card
                            html.Div(
                                id="wbgt-index-card",
                                style={
                                    "backgroundColor": "#4a5a6a",
                                    "borderRadius": "8px",
                                    "padding": "10px",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "flex": "1",
                                    "minHeight": "300px",
                                },
                                children=[
                                    # Header with toggle button
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "alignItems": "center",
                                            "borderBottom": "1px solid #5a6a7a",
                                            "paddingBottom": "6px",
                                            "marginBottom": "8px",
                                        },
                                        children=[
                                            html.H5(
                                                "🌡️ Wet-Bulb Globe Temperature (WBGT) (Heat Stress) across detected areas",
                                                style={
                                                    "margin": "0",
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                }
                                            ),
                                            html.Button(
                                                "📍",
                                                id="wbgt-map-toggle",
                                                n_clicks=0,
                                                style={
                                                    "backgroundColor": "transparent",
                                                    "border": "1px solid #6a7a8a",
                                                    "borderRadius": "4px",
                                                    "color": "#ccc",
                                                    "cursor": "pointer",
                                                    "padding": "4px 8px",
                                                    "fontSize": "14px",
                                                },
                                                title="Show WBGT stations on map"
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        id="wbgt-index-content",
                                        style={
                                            "flex": "1",
                                            "overflowY": "auto",
                                            "overflowX": "hidden",
                                            "minHeight": "0",
                                        },
                                        children=[
                                            html.P(
                                                "Loading WBGT data...",
                                                style={
                                                    "color": "#ccc",
                                                    "textAlign": "center",
                                                    "padding": "12px",
                                                }
                                            )
                                        ]
                                    ),
                                ]
                            ),
                        ]
                    ),
                    # Map container
                    html.Div(
                        id="weather-indices-map-panel",
                        style={
                            "flex": "6",
                            "minWidth": "400px",
                            "backgroundColor": "#1a2a3a",
                            "borderRadius": "8px",
                            "overflow": "hidden",
                            "display": "flex",
                            "flexDirection": "column",
                        },
                        children=[
                            # Map
                            html.Div(
                                style={
                                    "flex": "1",
                                    "minHeight": "0",
                                },
                                children=[
                                    dl.Map(
                                        id="weather-indices-map",
                                        center=sg_center,
                                        zoom=fixed_zoom,
                                        minZoom=fixed_zoom,
                                        maxZoom=fixed_zoom,
                                        maxBounds=sg_bounds,
                                        maxBoundsViscosity=1.0,
                                        style={
                                            "width": "100%",
                                            "height": "100%",
                                            "minHeight": "400px",
                                            "backgroundColor": "#1a2a3a",
                                        },
                                        children=[
                                            dl.TileLayer(
                                                url=onemap_tiles_url,
                                                attribution=onemap_attribution,
                                                maxNativeZoom=19,
                                            ),
                                            dl.LayerGroup(
                                                id="weather-indices-markers"
                                            ),
                                            dl.LayerGroup(
                                                id="psi-markers"
                                            ),
                                        ],
                                        zoomControl=False,
                                        dragging=False,
                                        scrollWheelZoom=False,
                                        touchZoom=False,
                                        doubleClickZoom=False,
                                        boxZoom=False,
                                        keyboard=False,
                                    ),
                                ]
                            ),
                        ]
                    ),
                    # Pollutant Legend (separate div, not sharing parent with map)
                    html.Div(
                        id="pollutant-legend",
                        style={
                            "flex": "2",
                            "minWidth": "250px",
                            "backgroundColor": "#2a3a4a",
                            "borderRadius": "8px",
                            "padding": "8px",
                            "overflowY": "auto",
                            "maxHeight": "100%",
                        },
                        children=[
                            html.Div(
                                "Pollutant Abbreviations",
                                style={
                                    "fontSize": "11px",
                                    "fontWeight": "700",
                                    "color": "#60a5fa",
                                    "marginBottom": "4px",
                                }
                            ),
                            html.Div(
                                style={
                                    "display": "flex",
                                    "flexWrap": "wrap",
                                    "gap": "4px 8px",
                                    "fontSize": "10px",
                                    "color": "#ccc",
                                },
                                children=[
                                    html.Span([
                                        html.Strong("PSI", style={"color": "#fff"}),
                                        " = Pollutant Standards Index"
                                    ]),
                                    html.Span([
                                        html.Strong("PM2.5", style={"color": "#fff"}),
                                        " = Particulate Matter ≤2.5µm"
                                    ]),
                                    html.Span([
                                        html.Strong("PM10", style={"color": "#fff"}),
                                        " = Particulate Matter ≤10µm"
                                    ]),
                                    html.Span([
                                        html.Strong("SO₂", style={"color": "#fff"}),
                                        " = Sulphur Dioxide"
                                    ]),
                                    html.Span([
                                        html.Strong("CO", style={"color": "#fff"}),
                                        " = Carbon Monoxide"
                                    ]),
                                    html.Span([
                                        html.Strong("O₃", style={"color": "#fff"}),
                                        " = Ozone"
                                    ]),
                                    html.Span([
                                        html.Strong("NO₂", style={"color": "#fff"}),
                                        " = Nitrogen Dioxide"
                                    ]),
                                ]
                            ),
                            # PSI Color Legend
                            html.Div(
                                        style={
                                            "marginTop": "6px",
                                            "paddingTop": "6px",
                                            "borderTop": "1px solid #3a4a5a",
                                        },
                                children=[
                                    html.Div(
                                        "PSI Color Categories",
                                        style={
                                            "fontSize": "10px",
                                            "fontWeight": "600",
                                            "color": "#60a5fa",
                                            "marginBottom": "3px",
                                        }
                                    ),
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "flexWrap": "wrap",
                                            "gap": "4px 8px",
                                            "fontSize": "9px",
                                            "color": "#ccc",
                                        },
                                        children=[
                                            html.Span([
                                                html.Span(
                                                    "●",
                                                    style={
                                                        "color": "#3ea72d",
                                                        "fontSize": "12px",
                                                        "marginRight": "4px",
                                                    }
                                                ),
                                                "Good (0-50)"
                                            ]),
                                            html.Span([
                                                html.Span(
                                                    "●",
                                                    style={
                                                        "color": "#fff300",
                                                        "fontSize": "12px",
                                                        "marginRight": "4px",
                                                    }
                                                ),
                                                "Moderate (51-100)"
                                            ]),
                                            html.Span([
                                                html.Span(
                                                    "●",
                                                    style={
                                                        "color": "#f18b00",
                                                        "fontSize": "12px",
                                                        "marginRight": "4px",
                                                    }
                                                ),
                                                "Unhealthy (101-200)"
                                            ]),
                                            html.Span([
                                                html.Span(
                                                    "●",
                                                    style={
                                                        "color": "#e53210",
                                                        "fontSize": "12px",
                                                        "marginRight": "4px",
                                                    }
                                                ),
                                                "Very Unhealthy (201-300)"
                                            ]),
                                            html.Span([
                                                html.Span(
                                                    "●",
                                                    style={
                                                        "color": "#b567a4",
                                                        "fontSize": "12px",
                                                        "marginRight": "4px",
                                                    }
                                                ),
                                                "Hazardous (301+)"
                                            ]),
                                        ]
                                    ),
                                    html.Div(
                                        style={
                                            "marginTop": "4px",
                                            "paddingTop": "4px",
                                            "borderTop": "1px solid #3a4a5a",
                                            "fontSize": "8px",
                                            "color": "#888",
                                            "fontStyle": "italic",
                                        },
                                        children=[
                                            "Source: Singapore NEA PSI Standards"
                                        ]
                                    ),
                                ]
                            ),
                            # Pollutant Color Categories Legend
                            html.Div(
                                        style={
                                            "marginTop": "6px",
                                            "paddingTop": "6px",
                                            "borderTop": "1px solid #3a4a5a",
                                        },
                                children=[
                                    html.Div(
                                        "Pollutant Color Categories",
                                        style={
                                            "fontSize": "10px",
                                            "fontWeight": "600",
                                            "color": "#60a5fa",
                                            "marginBottom": "3px",
                                        }
                                    ),
                                    html.Table(
                                        style={
                                            "width": "100%",
                                            "fontSize": "8px",
                                            "color": "#ccc",
                                            "borderCollapse": "collapse",
                                        },
                                        children=[
                                            # Header row
                                            html.Thead(
                                                children=[
                                                    html.Tr(
                                                        children=[
                                                            html.Th(
                                                                "Pollutant",
                                                                style={
                                                                    "textAlign": "left",
                                                                    "padding": "3px 4px",
                                                                    "borderBottom": "1px solid #3a4a5a",
                                                                    "fontWeight": "600",
                                                                    "color": "#fff",
                                                                }
                                                            ),
                                                            html.Th(
                                                                "Good",
                                                                style={
                                                                    "textAlign": "center",
                                                                    "padding": "3px 4px",
                                                                    "borderBottom": "1px solid #3a4a5a",
                                                                    "fontWeight": "600",
                                                                    "color": "#fff",
                                                                }
                                                            ),
                                                            html.Th(
                                                                "Moderate",
                                                                style={
                                                                    "textAlign": "center",
                                                                    "padding": "3px 4px",
                                                                    "borderBottom": "1px solid #3a4a5a",
                                                                    "fontWeight": "600",
                                                                    "color": "#fff",
                                                                }
                                                            ),
                                                            html.Th(
                                                                "Unhealthy",
                                                                style={
                                                                    "textAlign": "center",
                                                                    "padding": "3px 4px",
                                                                    "borderBottom": "1px solid #3a4a5a",
                                                                    "fontWeight": "600",
                                                                    "color": "#fff",
                                                                }
                                                            ),
                                                            html.Th(
                                                                "Very Unhealthy",
                                                                style={
                                                                    "textAlign": "center",
                                                                    "padding": "3px 4px",
                                                                    "borderBottom": "1px solid #3a4a5a",
                                                                    "fontWeight": "600",
                                                                    "color": "#fff",
                                                                }
                                                            ),
                                                            html.Th(
                                                                "Hazardous",
                                                                style={
                                                                    "textAlign": "center",
                                                                    "padding": "3px 4px",
                                                                    "borderBottom": "1px solid #3a4a5a",
                                                                    "fontWeight": "600",
                                                                    "color": "#fff",
                                                                }
                                                            ),
                                                        ]
                                                    )
                                                ]
                                            ),
                                            # Data rows
                                            html.Tbody(
                                                children=[
                                                    html.Tr(
                                                        children=[
                                                            html.Td(
                                                                [html.Strong("PM2.5", style={"color": "#fff"}), " (µg/m³)"],
                                                                style={"padding": "4px 6px", "borderBottom": "1px solid #2a2a2a"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#3ea72d", "fontSize": "10px", "marginRight": "4px"}), "0-15"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#3ea72d"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#fff300", "fontSize": "10px", "marginRight": "4px"}), "15-35"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#fff300"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#f18b00", "fontSize": "10px", "marginRight": "4px"}), "35-55"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#f18b00"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#e53210", "fontSize": "10px", "marginRight": "4px"}), "55-150"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#e53210"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#b567a4", "fontSize": "10px", "marginRight": "4px"}), "150+"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#b567a4"}
                                                            ),
                                                        ]
                                                    ),
                                                    html.Tr(
                                                        children=[
                                                            html.Td(
                                                                [html.Strong("PM10", style={"color": "#fff"}), " (µg/m³)"],
                                                                style={"padding": "4px 6px", "borderBottom": "1px solid #2a2a2a"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#3ea72d", "fontSize": "10px", "marginRight": "4px"}), "0-45"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#3ea72d"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#fff300", "fontSize": "10px", "marginRight": "4px"}), "45-100"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#fff300"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#f18b00", "fontSize": "10px", "marginRight": "4px"}), "100-200"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#f18b00"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#e53210", "fontSize": "10px", "marginRight": "4px"}), "200-300"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#e53210"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#b567a4", "fontSize": "10px", "marginRight": "4px"}), "300+"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#b567a4"}
                                                            ),
                                                        ]
                                                    ),
                                                    html.Tr(
                                                        children=[
                                                            html.Td(
                                                                [html.Strong("SO₂", style={"color": "#fff"}), " (µg/m³)"],
                                                                style={"padding": "4px 6px", "borderBottom": "1px solid #2a2a2a"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#3ea72d", "fontSize": "10px", "marginRight": "4px"}), "0-20"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#3ea72d"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#fff300", "fontSize": "10px", "marginRight": "4px"}), "20-50"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#fff300"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#f18b00", "fontSize": "10px", "marginRight": "4px"}), "50-125"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#f18b00"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#e53210", "fontSize": "10px", "marginRight": "4px"}), "125-250"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#e53210"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#b567a4", "fontSize": "10px", "marginRight": "4px"}), "250+"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#b567a4"}
                                                            ),
                                                        ]
                                                    ),
                                                    html.Tr(
                                                        children=[
                                                            html.Td(
                                                                [html.Strong("CO", style={"color": "#fff"}), " (mg/m³)"],
                                                                style={"padding": "4px 6px", "borderBottom": "1px solid #2a2a2a"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#3ea72d", "fontSize": "10px", "marginRight": "4px"}), "0-4"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#3ea72d"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#fff300", "fontSize": "10px", "marginRight": "4px"}), "4-9"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#fff300"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#f18b00", "fontSize": "10px", "marginRight": "4px"}), "9-15"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#f18b00"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#e53210", "fontSize": "10px", "marginRight": "4px"}), "15-30"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#e53210"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#b567a4", "fontSize": "10px", "marginRight": "4px"}), "30+"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#b567a4"}
                                                            ),
                                                        ]
                                                    ),
                                                    html.Tr(
                                                        children=[
                                                            html.Td(
                                                                [html.Strong("O₃", style={"color": "#fff"}), " (µg/m³)"],
                                                                style={"padding": "4px 6px", "borderBottom": "1px solid #2a2a2a"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#3ea72d", "fontSize": "10px", "marginRight": "4px"}), "0-100"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#3ea72d"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#fff300", "fontSize": "10px", "marginRight": "4px"}), "100-160"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#fff300"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#f18b00", "fontSize": "10px", "marginRight": "4px"}), "160-240"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#f18b00"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#e53210", "fontSize": "10px", "marginRight": "4px"}), "240-300"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#e53210"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#b567a4", "fontSize": "10px", "marginRight": "4px"}), "300+"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#b567a4"}
                                                            ),
                                                        ]
                                                    ),
                                                    html.Tr(
                                                        children=[
                                                            html.Td(
                                                                [html.Strong("NO₂", style={"color": "#fff"}), " (µg/m³)"],
                                                                style={"padding": "4px 6px", "borderBottom": "1px solid #2a2a2a"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#3ea72d", "fontSize": "10px", "marginRight": "4px"}), "0-200"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#3ea72d"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#fff300", "fontSize": "10px", "marginRight": "4px"}), "200-400"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#fff300"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#f18b00", "fontSize": "10px", "marginRight": "4px"}), "400-1000"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#f18b00"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#e53210", "fontSize": "10px", "marginRight": "4px"}), "1000-2000"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#e53210"}
                                                            ),
                                                            html.Td(
                                                                [html.Span("●", style={"color": "#b567a4", "fontSize": "10px", "marginRight": "4px"}), "2000+"],
                                                                style={"textAlign": "center", "padding": "4px 6px", "borderBottom": "1px solid #2a2a2a", "color": "#b567a4"}
                                                            ),
                                                        ]
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        style={
                                            "marginTop": "4px",
                                            "paddingTop": "4px",
                                            "borderTop": "1px solid #3a4a5a",
                                            "fontSize": "8px",
                                            "color": "#888",
                                            "fontStyle": "italic",
                                        },
                                        children=[
                                            "Source: WHO/EPA Air Quality Standards"
                                        ]
                                    ),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
            # Interval for auto-refresh
            dcc.Interval(
                id='weather-indices-interval',
                interval=60*1000,  # Update every 60 seconds
                n_intervals=0
            ),
        ]
    )
