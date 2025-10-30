import os
import requests
from urllib.parse import quote_plus


def search_location_via_onemap_info(searchVal: str, returnGeom: str = "Y", getAddrDetails: str = "N", onemap_url: str = "https://www.onemap.gov.sg/api/common/elastic/search?"):
    env_onemap = os.getenv("ONEMAP_API")
    if env_onemap:
        onemap_url = env_onemap

    # Defensive: handle None/NaN/float and ensure URL-safe encoding
    if searchVal is None:
        return {}
    searchVal = quote_plus(str(searchVal).strip())

    onemap_search_url = onemap_url + f"searchVal={searchVal}&returnGeom={returnGeom}&getAddrDetails={getAddrDetails}"
    print(onemap_search_url)

    req_headers = {"User-agent": "quekzhiqiang",
                   "Content-Type": "application/json"}
    res = requests.request("GET", onemap_search_url, headers=req_headers)
    if res.status_code == 200:
        print(f"Request successful with status code {res.status_code}")
        the_json = res.json()
        return the_json.get("results", [{}])[0]
    print(f"Return unsuccessful with status code {res.status_code}")
    res.raise_for_status()
    return {}