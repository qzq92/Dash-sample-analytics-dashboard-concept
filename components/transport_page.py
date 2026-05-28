"""
Component for the Transport Information page.
Displays transport-related information including taxi availability.
"""
from dash import html, dcc
from conf.cache_config import INTERVAL_TRANSPORT_MS, INTERVAL_EV_CHARGING_MS
import dash_leaflet as dl
from utils.transport.bus import get_bus_stops_count
from utils.map_utils import (
    get_onemap_attribution,
    SG_MAP_CENTER,
    SG_MAP_DEFAULT_ZOOM,
    SG_MAP_BOUNDS,
    ONEMAP_TILES_URL
)
from components.metric_card import create_metric_card
from components.traffic_incidents_legend import build_traffic_incidents_legend
from conf.page_layout_config import PAGE_PADDING, PAGE_HEIGHT, get_content_container_style, STANDARD_GAP


def transport_page():
    """
    Create the Transport Information page layout.
    Features: Taxi availability display with map.

    Returns:
        HTML Div containing the Transport Information section
    """
    # Use standardized map configuration
    sg_center = SG_MAP_CENTER
    onemap_tiles_url = ONEMAP_TILES_URL
    fixed_zoom = SG_MAP_DEFAULT_ZOOM
    onemap_attribution = get_onemap_attribution()
    sg_bounds = SG_MAP_BOUNDS
    try:
        initial_bus_stops_count = str(get_bus_stops_count())
    except Exception:
        initial_bus_stops_count = "--"

    return html.Div(
        id="transport-page",
        style={
            "display": "none",  # Hidden by default
            "padding": PAGE_PADDING,
            "height": PAGE_HEIGHT,
            "width": "100%",
        },
        children=[
            # Main content container
            html.Div(
                id="transport-content",
                style=get_content_container_style(gap=STANDARD_GAP),
                children=[
                    # Left side: Transport info panel
                    html.Div(
                        id="transport-info-panel",
                        style={
                            "flex": "1",
                            "minWidth": "18.75rem",
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "0.9375rem",
                        },
                        children=[
                            # Taxi Availability card
                            html.Div(
                                id="taxi-availability-card",
                                style={
                                    "backgroundColor": "#4a5a6a",
                                    "borderRadius": "0.5rem",
                                    "padding": "0.625rem",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "gap": "0.5rem",
                                },
                                children=[
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "flexDirection": "row",
                                            "alignItems": "center",
                                            "justifyContent": "space-between",
                                        },
                                        children=[
                                            html.Span(
                                                "🚕 Current Taxi Availability/Stands",
                                                style={
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                    "fontSize": "0.8125rem"
                                                }
                                            ),
                                            html.Div(
                                                id="taxi-count-value",
                                                style={
                                                    "color": "#FFD700",
                                                    "fontSize": "1.125rem",
                                                    "fontWeight": "700",
                                                },
                                                children=[
                                                    html.Div(
                                                        html.Span(initial_bus_stops_count, style={"color": "#4169E1" if initial_bus_stops_count != "--" else "#999"}),
                                                        style={
                                                            "backgroundColor": "rgb(58, 74, 90)",
                                                            "padding": "0.25rem 0.5rem",
                                                            "borderRadius": "0.25rem",
                                                        }
                                                    )
                                                ]
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            # Camera metrics row: LTA Traffic Cameras and SPF Speed Camera
                            html.Div(
                                style={
                                    "display": "grid",
                                    "gridTemplateColumns": "1fr 1fr",
                                    "gap": "0.5rem",
                                    "marginBottom": "0.5rem",
                                },
                                children=[
                                    # CCTV Traffic Cameras card
                                    html.Div(
                                        id="cctv-card",
                                        style={
                                            "backgroundColor": "#4a5a6a",
                                            "borderRadius": "0.5rem",
                                            "padding": "0.625rem",
                                            "display": "flex",
                                            "flexDirection": "column",
                                            "gap": "0.5rem",
                                        },
                                        children=[
                                            html.Div(
                                                style={
                                                    "display": "flex",
                                                    "flexDirection": "row",
                                                    "alignItems": "center",
                                                    "justifyContent": "space-between",
                                                },
                                                children=[
                                                    html.Span(
                                                        "📹 LTA Traffic Cameras",
                                                        style={
                                                            "color": "#fff",
                                                            "fontWeight": "600",
                                                            "fontSize": "0.8125rem"
                                                        }
                                                    ),
                                                    html.Div(
                                                        id="cctv-count-value",
                                                        style={
                                                            "color": "#4CAF50",
                                                            "fontSize": "1.125rem",
                                                            "fontWeight": "700",
                                                        },
                                                        children=[
                                                            html.Div(
                                                                html.Span("--", style={"color": "#999"}),
                                                                style={
                                                                    "backgroundColor": "rgb(58, 74, 90)",
                                                                    "padding": "0.25rem 0.5rem",
                                                                    "borderRadius": "0.25rem",
                                                                }
                                                            )
                                                        ]
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                    # SPF Speed Camera card
                                    html.Div(
                                        id="speed-camera-card",
                                        style={
                                            "backgroundColor": "#4a5a6a",
                                            "borderRadius": "0.5rem",
                                            "padding": "0.625rem",
                                            "display": "flex",
                                            "flexDirection": "column",
                                            "gap": "0.5rem",
                                        },
                                        children=[
                                            html.Div(
                                                style={
                                                    "display": "flex",
                                                    "flexDirection": "row",
                                                    "alignItems": "center",
                                                    "justifyContent": "space-between",
                                                },
                                                children=[
                                                    html.Span(
                                                        "📸 SPF Speed Camera",
                                                        style={
                                                            "color": "#fff",
                                                            "fontWeight": "600",
                                                            "fontSize": "0.8125rem"
                                                        }
                                                    ),
                                                    html.Div(
                                                        id="speed-camera-count-value",
                                                        style={
                                                            "color": "#A5D6A7",
                                                            "fontSize": "1.125rem",
                                                            "fontWeight": "700",
                                                        },
                                                        children=[
                                                            html.Div(
                                                                html.Span("--", style={"color": "#999"}),
                                                                style={
                                                                    "backgroundColor": "rgb(58, 74, 90)",
                                                                    "padding": "0.25rem 0.5rem",
                                                                    "borderRadius": "0.25rem",
                                                                }
                                                            )
                                                        ]
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            # ERP and VMS metrics row: ERP Gantries and VMS Display boards
                            html.Div(
                                style={
                                    "display": "grid",
                                    "gridTemplateColumns": "1fr 1fr",
                                    "gap": "0.5rem",
                                    "marginBottom": "0.5rem",
                                },
                                children=[
                                    # ERP Gantry card
                                    html.Div(
                                        id="erp-card",
                                        style={
                                            "backgroundColor": "#4a5a6a",
                                            "borderRadius": "0.5rem",
                                            "padding": "0.625rem",
                                            "display": "flex",
                                            "flexDirection": "column",
                                            "gap": "0.5rem",
                                        },
                                        children=[
                                            html.Div(
                                                style={
                                                    "display": "flex",
                                                    "flexDirection": "row",
                                                    "alignItems": "center",
                                                    "justifyContent": "space-between",
                                                },
                                                children=[
                                                    html.Span(
                                                        "🚧 ERP Gantries",
                                                        style={
                                                            "color": "#fff",
                                                            "fontWeight": "600",
                                                            "fontSize": "0.8125rem"
                                                        }
                                                    ),
                                                    html.Div(
                                                        id="erp-count-value",
                                                        style={
                                                            "color": "#FF6B6B",
                                                            "fontSize": "1.125rem",
                                                            "fontWeight": "700",
                                                        },
                                                        children=[
                                                            html.Div(
                                                                html.Span("--", style={"color": "#999"}),
                                                                style={
                                                                    "backgroundColor": "rgb(58, 74, 90)",
                                                                    "padding": "0.25rem 0.5rem",
                                                                    "borderRadius": "0.25rem",
                                                                }
                                                            )
                                                        ]
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                    # VMS card
                                    html.Div(
                                        id="vms-card",
                                        style={
                                            "backgroundColor": "#4a5a6a",
                                            "borderRadius": "0.5rem",
                                            "padding": "0.625rem",
                                            "display": "flex",
                                            "flexDirection": "column",
                                            "gap": "0.5rem",
                                        },
                                        children=[
                                            html.Div(
                                                style={
                                                    "display": "flex",
                                                    "flexDirection": "row",
                                                    "alignItems": "center",
                                                    "justifyContent": "space-between",
                                                },
                                                children=[
                                                    html.Span(
                                                        "📺 VMS Display boards",
                                                        style={
                                                            "color": "#fff",
                                                            "fontWeight": "600",
                                                            "fontSize": "0.8125rem"
                                                        }
                                                    ),
                                                    html.Div(
                                                        id="vms-count-value",
                                                        style={
                                                            "color": "#C0C0C0",
                                                            "fontSize": "1.125rem",
                                                            "fontWeight": "700",
                                                        },
                                                        children=[
                                                            html.Div(
                                                                html.Span("--", style={"color": "#999"}),
                                                                style={
                                                                    "backgroundColor": "rgb(58, 74, 90)",
                                                                    "padding": "0.25rem 0.5rem",
                                                                    "borderRadius": "0.25rem",
                                                                }
                                                            )
                                                        ]
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            # EV Charging Points card
                            create_metric_card(
                                card_id="ev-charging-points-card",
                                label="🔌 EV Charging Points",
                                value_id="ev-charging-points-count-value",
                                initial_value="--",
                                value_color="#87CEEB",
                            ),
                            # Traffic Incidents card
                            html.Div(
                                id="traffic-incidents-card",
                                style={
                                    "backgroundColor": "#4a5a6a",
                                    "borderRadius": "0.5rem",
                                    "padding": "0.625rem",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "gap": "0.5rem",
                                },
                                children=[
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "flexDirection": "row",
                                            "alignItems": "center",
                                            "justifyContent": "space-between",
                                        },
                                        children=[
                                            html.Span(
                                                "🚦 Traffic Incidents",
                                                style={
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                    "fontSize": "0.8125rem"
                                                }
                                            ),
                                            html.Div(
                                                id="traffic-incidents-count-value",
                                                style={
                                                    "color": "#FF9800",
                                                    "fontSize": "1.125rem",
                                                    "fontWeight": "700",
                                                },
                                                children=[
                                                    html.Div(
                                                        html.Span("--", style={"color": "#999"}),
                                                        style={
                                                            "backgroundColor": "rgb(58, 74, 90)",
                                                            "padding": "0.25rem 0.5rem",
                                                            "borderRadius": "0.25rem",
                                                        }
                                                    )
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        id="traffic-incidents-messages",
                                        style={
                                            "maxHeight": "9.375rem",
                                            "overflowY": "auto",
                                            "display": "none",
                                        }
                                    ),
                                ]
                            ),
                            # Bus Stops card
                            html.Div(
                                id="bus-stops-card",
                                style={
                                    "backgroundColor": "#4a5a6a",
                                    "borderRadius": "0.5rem",
                                    "padding": "0.625rem",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "gap": "0.5rem",
                                },
                                children=[
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "flexDirection": "row",
                                            "alignItems": "center",
                                            "justifyContent": "space-between",
                                        },
                                        children=[
                                            html.Span(
                                                "🚏 Bus Stops",
                                                style={
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                    "fontSize": "0.8125rem"
                                                }
                                            ),
                                            html.Div(
                                                id="bus-stops-count-value",
                                                style={
                                                    "color": "#4169E1",
                                                    "fontSize": "1.125rem",
                                                    "fontWeight": "700",
                                                },
                                                children=[
                                                    html.Div(
                                                        html.Span("--", style={"color": "#999"}),
                                                        style={
                                                            "backgroundColor": "rgb(58, 74, 90)",
                                                            "padding": "0.25rem 0.5rem",
                                                            "borderRadius": "0.25rem",
                                                        }
                                                    )
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        id="bus-stops-disclaimer",
                                        style={"display": "none"},
                                        children=[
                                            html.P(
                                                "⚠️ Note: Bus stop markers may deviate from actual locations due to road construction works.",
                                                style={
                                                    "color": "#fbbf24",
                                                    "fontSize": "0.7rem",
                                                    "fontStyle": "italic",
                                                    "margin": "0",
                                                    "lineHeight": "1.3",
                                                }
                                            )
                                        ]
                                    ),
                                ]
                            ),
                            # Bus Services card
                            create_metric_card(
                                card_id="bus-services-card",
                                label="🚌 Bus Services Currently in Operation",
                                value_id="bus-services-count-value",
                                initial_value="--"
                            ),
                        ]
                    ),
                    # Middle: Map
                    html.Div(
                        id="transport-map-panel",
                        style={
                            "flex": "2",
                            "minWidth": "31.25rem",
                            "backgroundColor": "#1a2a3a",
                            "borderRadius": "0.5rem",
                            "overflow": "hidden",
                            "display": "flex",
                            "flexDirection": "column",
                        },
                        children=[
                            # Toggle buttons container above map
                            html.Div(
                                id="transport-toggle-buttons-container",
                                style={
                                    "display": "flex",
                                    "flexDirection": "row",
                                    "gap": "0.625rem",
                                    "padding": "0.9375rem",
                                    "backgroundColor": "#2c3e50",
                                    "borderRadius": "0.5rem 0.5rem 0 0",
                                    "flexWrap": "wrap",
                                    "justifyContent": "flex-start",
                                    "alignItems": "center",
                                },
                                children=[
                                    html.Button(
                                        "Show Current Taxi Availability/Stands",
                                        id="taxi-toggle-btn",
                                        n_clicks=0,
                                        style={
                                            "backgroundColor": "transparent",
                                            "border": "0.125rem solid #FFD700",
                                            "borderRadius": "0.25rem",
                                            "color": "#FFD700",
                                            "cursor": "pointer",
                                            "padding": "0.25rem 0.625rem",
                                            "fontSize": "0.75rem",
                                            "fontWeight": "600",
                                        },
                                    ),
                                    html.Button(
                                        "Show LTA Traffic Cameras Location",
                                        id="cctv-toggle-btn",
                                        n_clicks=0,
                                        style={
                                            "backgroundColor": "transparent",
                                            "border": "0.125rem solid #4CAF50",
                                            "borderRadius": "0.25rem",
                                            "color": "#4CAF50",
                                            "cursor": "pointer",
                                            "padding": "0.25rem 0.625rem",
                                            "fontSize": "0.75rem",
                                            "fontWeight": "600",
                                        },
                                    ),
                                    html.Button(
                                        "Show ERP Gantries Location",
                                        id="erp-toggle-btn",
                                        n_clicks=0,
                                        style={
                                            "backgroundColor": "transparent",
                                            "border": "0.125rem solid #FF6B6B",
                                            "borderRadius": "0.25rem",
                                            "color": "#FF6B6B",
                                            "cursor": "pointer",
                                            "padding": "0.25rem 0.625rem",
                                            "fontSize": "0.75rem",
                                            "fontWeight": "600",
                                        },
                                    ),
                                    html.Button(
                                        "Show Traffic Incidents",
                                        id="traffic-incidents-toggle-btn",
                                        n_clicks=0,
                                        style={
                                            "backgroundColor": "transparent",
                                            "border": "0.125rem solid #FF9800",
                                            "borderRadius": "0.25rem",
                                            "color": "#FF9800",
                                            "cursor": "pointer",
                                            "padding": "0.25rem 0.625rem",
                                            "fontSize": "0.75rem",
                                            "fontWeight": "600",
                                        },
                                    ),
                                    html.Button(
                                        "Show VMS Display boards Locations",
                                        id="vms-toggle-btn",
                                        n_clicks=0,
                                        style={
                                            "backgroundColor": "transparent",
                                            "border": "0.125rem solid #C0C0C0",
                                            "borderRadius": "0.25rem",
                                            "color": "#C0C0C0",
                                            "cursor": "pointer",
                                            "padding": "0.25rem 0.625rem",
                                            "fontSize": "0.75rem",
                                            "fontWeight": "600",
                                        },
                                    ),
                                    html.Button(
                                        "Show SPF Speed Camera Locations",
                                        id="speed-camera-toggle-btn",
                                        n_clicks=0,
                                        style={
                                            "backgroundColor": "transparent",
                                            "border": "0.125rem solid #81C784",
                                            "borderRadius": "0.25rem",
                                            "color": "#81C784",
                                            "cursor": "pointer",
                                            "padding": "0.25rem 0.625rem",
                                            "fontSize": "0.75rem",
                                            "fontWeight": "600",
                                        },
                                    ),
                                    html.Button(
                                        "Show EV Charging Points",
                                        id="ev-charging-toggle-btn",
                                        n_clicks=0,
                                        style={
                                            "backgroundColor": "transparent",
                                            "border": "0.125rem solid #87CEEB",
                                            "borderRadius": "0.25rem",
                                            "color": "#87CEEB",
                                            "cursor": "pointer",
                                            "padding": "0.25rem 0.625rem",
                                            "fontSize": "0.75rem",
                                            "fontWeight": "600",
                                        },
                                    ),
                                    html.Button(
                                        "Show Bus Stop Locations",
                                        id="transport-bus-stops-toggle-btn",
                                        n_clicks=0,
                                        style={
                                            "backgroundColor": "transparent",
                                            "border": "0.125rem solid #4169E1",
                                            "borderRadius": "0.25rem",
                                            "color": "#4169E1",
                                            "cursor": "pointer",
                                            "padding": "0.25rem 0.625rem",
                                            "fontSize": "0.75rem",
                                            "fontWeight": "600",
                                        },
                                    ),
                                ]
                            ),
                            html.Div(
                                style={
                                    "position": "relative",
                                    "width": "100%",
                                    "height": "100%",
                                    "flex": "1",
                                    "minHeight": "25rem",
                                },
                                children=[
                                    dl.Map(
                                        id="transport-map",
                                        center=sg_center,
                                        zoom=fixed_zoom,
                                        minZoom=10,
                                        maxZoom=18,
                                        maxBounds=sg_bounds,
                                        maxBoundsViscosity=1.0,
                                        style={
                                            "width": "100%",
                                            "height": "100%",
                                            "backgroundColor": "#1a2a3a",
                                        },
                                        children=[
                                            dl.TileLayer(
                                                url=onemap_tiles_url,
                                                attribution=onemap_attribution,
                                                maxNativeZoom=18,
                                            ),
                                            dl.LayerGroup(id="taxi-markers"),
                                            dl.LayerGroup(id="cctv-markers"),
                                            dl.LayerGroup(id="erp-markers"),
                                            dl.LayerGroup(id="speed-camera-markers"),
                                            dl.LayerGroup(id="traffic-incidents-markers"),
                                            dl.LayerGroup(id="vms-markers"),
                                            dl.LayerGroup(id="ev-charging-markers"),
                                            dl.LayerGroup(id="transport-bus-stops-markers"),
                                        ],
                                        zoomControl=True,
                                        dragging=True,
                                        scrollWheelZoom=True,
                                    ),
                                    # Taxi legend overlay
                                    html.Div(
                                        id="taxi-legend",
                                        style={
                                            "position": "absolute",
                                            "top": "0.625rem",
                                            "right": "0.625rem",
                                            "backgroundColor": "rgba(26, 42, 58, 0.9)",
                                            "borderRadius": "0.5rem",
                                            "padding": "0.625rem",
                                            "zIndex": "1000",
                                            "boxShadow": "0 0.125rem 0.5rem rgba(0, 0, 0, 0.3)",
                                            "display": "none",  # Hidden by default, shown when taxi toggle is on
                                        },
                                        children=[
                                            html.Div(
                                                style={
                                                    "fontSize": "0.75rem",
                                                    "fontWeight": "600",
                                                    "color": "#fff",
                                                    "marginBottom": "0.5rem",
                                                    "borderBottom": "0.0625rem solid #4a5a6a",
                                                    "paddingBottom": "0.25rem",
                                                },
                                                children="Taxi Legend"
                                            ),
                                            html.Div(
                                                style={
                                                    "display": "flex",
                                                    "alignItems": "center",
                                                    "marginBottom": "0.375rem",
                                                },
                                                children=[
                                                    html.Div(
                                                        style={
                                                            "width": "0.75rem",
                                                            "height": "0.75rem",
                                                            "borderRadius": "50%",
                                                            "backgroundColor": "#FFD700",
                                                            "marginRight": "0.5rem",
                                                        }
                                                    ),
                                                    html.Span(
                                                        "Taxi Locations",
                                                        style={
                                                            "color": "#fff",
                                                            "fontSize": "0.6875rem",
                                                        }
                                                    ),
                                                ]
                                            ),
                                            html.Div(
                                                style={
                                                    "display": "flex",
                                                    "alignItems": "center",
                                                },
                                                children=[
                                                    html.Div(
                                                        style={
                                                            "width": "0",
                                                            "height": "0",
                                                            "borderLeft": "0.375rem solid transparent",
                                                            "borderRight": "0.375rem solid transparent",
                                                            "borderBottom": "0.75rem solid #FFA500",
                                                            "marginRight": "0.5rem",
                                                        }
                                                    ),
                                                    html.Span(
                                                        "Taxi Stands",
                                                        style={
                                                            "color": "#fff",
                                                            "fontSize": "0.6875rem",
                                                        }
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                    # Traffic Incidents Legend overlay
                                    build_traffic_incidents_legend("traffic-incidents-legend"),
                                    # Bus Stop Zoom Message Overlay
                                    html.Div(
                                        id="transport-bus-stop-zoom-message",
                                        style={
                                            "position": "absolute",
                                            "top": "50%",
                                            "left": "50%",
                                            "transform": "translate(-50%, -50%)",
                                            "backgroundColor": "rgba(0, 0, 0, 0.8)",
                                            "color": "#fbbf24",
                                            "padding": "1rem 2rem",
                                            "borderRadius": "0.5rem",
                                            "zIndex": "1000",
                                            "textAlign": "center",
                                            "display": "none",
                                            "fontWeight": "600",
                                            "fontSize": "1rem",
                                            "border": "0.0625rem solid #fbbf24",
                                        },
                                        children="Zoom in to level 15+ to view bus stops"
                                    ),
                                ]
                            ),
                        ]
                    ),
                    # Right side: Train Service Alerts
                    html.Div(
                        id="train-advisory-panel",
                        style={
                            "flex": "1",
                            "minWidth": "18.75rem",
                            "backgroundColor": "#4a5a6a",
                            "borderRadius": "0.5rem",
                            "padding": "0.9375rem",
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "0.75rem",
                            "overflowY": "auto",
                        },
                        children=[
                            # Train Service Alerts card
                            html.Div(
                                id="train-service-alerts-card",
                                style={
                                    "backgroundColor": "#4a5a6a",
                                    "borderRadius": "0.5rem",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "gap": "0.5rem",
                                    "marginBottom": "0.9375rem",
                                    "flex": "4",
                                    "minHeight": "0",
                                    "overflow": "hidden",
                                },
                                children=[
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "flexDirection": "row",
                                            "alignItems": "center",
                                            "justifyContent": "space-between",
                                        },
                                        children=[
                                            html.Span(
                                                "🚇 Train Service Alerts/Advisory",
                                                style={
                                                    "color": "#fff",
                                                    "fontWeight": "600",
                                                    "fontSize": "0.8125rem"
                                                }
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        id="train-service-alerts-content",
                                        style={
                                            "padding": "0.25rem",
                                            "color": "#999",
                                            "fontSize": "0.5rem",
                                            "textAlign": "center",
                                            "maxHeight": "15rem",
                                            "overflowY": "auto",
                                            "overflowX": "hidden",
                                            "display": "flex",
                                            "flexDirection": "column",
                                        },
                                        children=[
                                            html.P(
                                                "All service running fine",
                                                style={
                                                    "margin": "0",
                                                    "color": "#999",
                                                    "fontSize": "0.5rem",
                                                    "fontStyle": "italic",
                                                }
                                            )
                                        ]
                                    ),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
            # Store for toggle states
            dcc.Store(id="taxi-toggle-state", data=False),
            dcc.Store(id="transport-bus-stops-toggle-state", data=False),
            dcc.Store(id="cctv-toggle-state", data=False),
            dcc.Store(id="erp-toggle-state", data=False),
            dcc.Store(id="speed-camera-toggle-state", data=False),
            dcc.Store(id="traffic-incidents-toggle-state", data=False),
            dcc.Store(id="vms-toggle-state", data=False),
            dcc.Store(id="ev-charging-toggle-state", data=False),
            dcc.Store(id="evc-batch-refresh-result", data=None),
            # Interval for auto-refresh
            dcc.Interval(
                id='transport-interval',
                interval=INTERVAL_TRANSPORT_MS,
                n_intervals=0
            ),
            # Interval for map invalidation (fixes grey tiles)
            dcc.Interval(
                id='transport-map-invalidate-interval',
                interval=300,  # 300 ms — intentionally short for map tile fix
                n_intervals=0,
                max_intervals=1,  # Only fire once per activation
                disabled=True  # Start disabled
            ),
            # Interval for EV charging points updates
            dcc.Interval(
                id='ev-charging-interval',
                interval=INTERVAL_EV_CHARGING_MS,
                n_intervals=0
            ),
        ]
    )
