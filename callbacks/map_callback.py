"""
Callback functions for handling map interactions and OneMap search API integration.
Reference: https://www.onemap.gov.sg/apidocs/search
"""
import requests
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from dash.dependencies import Input, Output
from dash import no_update, html
import dash_leaflet as dl
load_dotenv(override=True)

def search_location_via_onemap_info(searchVal: str, returnGeom: str = "Y", getAddrDetails: str = "Y", pageNum: int = 1):
    """
    Search for location using OneMap Search API.
    Reference: https://www.onemap.gov.sg/apidocs/search
    
    Args:
        searchVal: Search value (required)
        returnGeom: Return geometry coordinates (Y/N), default Y
        getAddrDetails: Return address details (Y/N), default Y
        pageNum: Page number for pagination, default 1
    
    Returns:
        List of search results from OneMap API
    """
    # Defensive: handle None/NaN/float and ensure URL-safe encoding
    if not searchVal or str(searchVal).strip() == "":
        return []
    
    searchVal = quote_plus(str(searchVal).strip())
    
    # OneMap Search API endpoint as per documentation
    onemap_search_url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={searchVal}&returnGeom={returnGeom}&getAddrDetails={getAddrDetails}&pageNum={pageNum}"
    print(f"OneMap Search API Request: {onemap_search_url}")

    req_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    }
    
    try:
        res = requests.get(onemap_search_url, headers=req_headers, timeout=10)
        if res.status_code == 200:
            print(f"Request successful with status code {res.status_code}")
            the_json = res.json()
            found = the_json.get("found", 0)
            total_num_pages = the_json.get("totalNumPages", 0)
            page_num = the_json.get("pageNum", 0)
            results = the_json.get("results", [])

            print(f"Found {found} results, Page {page_num} of {total_num_pages}")
            return results

        print(f"Request unsuccessful with status code {res.status_code}")
        return []
    except requests.exceptions.RequestException as error:
        print(f"Error during OneMap API request: {error}")
        return []

def _haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute great-circle distance in meters between two WGS84 lat/lon points."""
    from math import radians, sin, cos, asin, sqrt
    r = 6371000.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2.0)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2.0)**2
    c = 2.0 * asin(sqrt(a))
    return r * c


def fetch_nearest_mrt(lat: float, lon: float, radius_m: int = 1000) -> list:
    """Call OneMap Nearby Service to get nearest MRT/LRT stops within radius (meters)."""
    try:
        url = "https://www.onemap.gov.sg/api/public/nearbysvc/getNearestMrtStops"
        params = {"latitude": lat, "longitude": lon, "radius_in_meters": radius_m}
        # Public endpoint; add headers if key available
        headers = {}
        api_key = os.getenv("ONEMAP_API_KEY")
        if api_key:
            headers["Authorization"] = api_key
        res = requests.get(url, params=params, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            # Response structure may contain 'mrt_stops' or 'results'; be defensive
            results = data.get("results") or data.get("mrt_stops") or data
            return results if isinstance(results, list) else []
        print(f"Nearest MRT API failed: status={res.status_code}, body={res.text[:200]}")
    except Exception as e:
        print(f"Error calling nearest MRT API: {e}")
    return []


def register_search_callbacks(app):
    """
    Register search-related callbacks for the OneMap search functionality.
    Implements integrated search bar with top 5 most relevant results.
    Reference: https://www.onemap.gov.sg/apidocs/search
    """

    @app.callback(
        Output('input_search', 'options'),
        Input('input_search', 'search_value'),
        Input('input_search', 'value')
    )
    def update_search_options(search_value, selected_value):
        """
        Update dropdown with top 5 search results from OneMap API as user types.

        Args:
            search_value: Text entered in the search input
            selected_value: Currently selected value

        Returns:
            List of top 5 dropdown options with address labels and lat/lon values
        """
        # If user has selected a value, keep it in options
        if selected_value and not search_value:
            try:
                parts = selected_value.split(',', 2)
                address = parts[2] if len(parts) > 2 else "Selected Location"
                return [{'label': address, 'value': selected_value}]
            except (ValueError, IndexError):
                return []

        if not search_value or len(str(search_value).strip()) < 3:
            return []

        results = search_location_via_onemap_info(search_value)
        options = []

        # Limit to top 5 most relevant results
        for result in results[:5]:
            # Extract relevant fields from OneMap API response
            address = result.get('ADDRESS', 'Unknown Address')
            building = result.get('BUILDING', '')
            postal = result.get('POSTAL', '')
            lat = result.get('LATITUDE')
            lon = result.get('LONGITUDE')

            if lat and lon:
                # Create a descriptive label
                label_parts = []
                if building:
                    label_parts.append(building)
                if address:
                    label_parts.append(address)
                if postal:
                    label_parts.append(f"(S{postal})")

                label = ', '.join(label_parts) if label_parts else address

                # Store coordinates in EPSG:4326 format (Leaflet expects this)
                options.append({
                    'label': label,
                    'value': f'{lat},{lon},{address}'  # Store lat,lon,address in EPSG:4326
                })

        print(f"Generated {len(options)} dropdown options (top 5)")
        return options

    @app.callback(
        [Output('sg-map', 'center'),
         Output('sg-map', 'zoom'),
         Output('markers-layer', 'children')],
        Input('input_search', 'value')
    )
    def update_map_from_search_selection(dropdown_value):
        """
        Update map when user selects a location from the dropdown.
        Centers the map on the selected location and adds a marker.

        Args:
            dropdown_value: Selected value from dropdown (format: 'lat,lon,address')

        Returns:
            Tuple of (map center, zoom level, marker)
        """
        if not dropdown_value:
            return no_update, no_update, no_update

        try:
            # Parse the dropdown value
            parts = dropdown_value.split(',', 2)  # Split into max 3 parts
            lat_str, lon_str = parts[0], parts[1]
            address = parts[2] if len(parts) > 2 else "Selected Location"

            lat, lon = float(lat_str), float(lon_str)

            # Create marker with popup showing the address (Leaflet expects EPSG:4326)
            marker = dl.Marker(
                position=[lat, lon],
                children=[
                    dl.Tooltip(address),
                    dl.Popup(address)
                ]
            )

            # Center map on the location with appropriate zoom for street level.
            zoom_level = 18

            print(f"Map updated to: {lat}, {lon} - {address}")
            return [lat, lon], zoom_level, [marker]

        except (ValueError, IndexError) as error:
            print(f"Error parsing dropdown value: {error}")
            return no_update, no_update, no_update

    @app.callback(
        Output('nearest-mrt-panel', 'children'),
        Input('input_search', 'value')
    )
    def update_nearest_mrt_panel(dropdown_value):
        if not dropdown_value:
            return []
        try:
            parts = dropdown_value.split(',', 2)
            lat, lon = float(parts[0]), float(parts[1])
        except Exception:
            return []

        raw_results = fetch_nearest_mrt(lat, lon, radius_m=1000)
        items = []
        for r in raw_results:
            # Try common field names defensively
            name = r.get('NAME') or r.get('name') or r.get('STN_NAME') or r.get('stn_name') or 'Unknown Station'
            stn_no = r.get('STN_NO') or r.get('stn_no') or ''
            line = r.get('LINE') or r.get('line') or ''
            rlat = r.get('LATITUDE') or r.get('latitude') or r.get('lat')
            rlon = r.get('LONGITUDE') or r.get('longitude') or r.get('lng')
            try:
                rlat = float(rlat)
                rlon = float(rlon)
                dist_m = _haversine_distance_m(lat, lon, rlat, rlon)
            except Exception:
                dist_m = None

            subtitle_parts = []
            if stn_no:
                subtitle_parts.append(str(stn_no))
            if line:
                subtitle_parts.append(str(line))
            subtitle = ' • '.join(subtitle_parts)
            dist_str = f"{dist_m:.0f} m" if dist_m is not None else "—"

            items.append({
                "name": name,
                "subtitle": subtitle,
                "distance": dist_m if dist_m is not None else float('inf')
            })

        # Sort by distance and take top 5
        items = sorted(items, key=lambda x: x["distance"])[:5]

        # Render as simple list
        rendered = [
            html.Div(
                [
                    html.Div(item["name"], style={"fontWeight": "600"}),
                    html.Div(
                        (item["subtitle"] + (" • " if item["subtitle"] else "") + f"{int(item['distance'])} m") if item["distance"] != float('inf') else item["subtitle"],
                        style={"fontSize": "12px", "opacity": 0.8}
                    ),
                ],
                style={"padding": "6px 8px", "borderBottom": "1px solid #333"}
            ) for item in items
        ]

        header = html.Div("Nearest MRT/LRT within 1 km", style={"marginTop": "8px", "marginBottom": "4px", "fontWeight": "700"})
        return [header] + rendered