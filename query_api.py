
#import os
#import sys
import requests
import yaml
import numpy as np
from dash import Dash, dcc, html, Input, Output, callback
from conf.api_key import LTA_API_KEY
from geopy.distance import geodesic
from typing import Union, Dict, Tuple, List

# Load API URL configuration
with open("api_url_config.yml", "r") as f:
    api_url_dict = yaml.safe_load(f.read())

def api_query(api_link: str,  agent_id: str, api_key: str, params_dict: Dict = None) -> Union[Dict,None]:
    """Function which executes query via an api link using a provided agent_id as an identifier to avoid rejection of query request

    Args:
        api_link (str): API Link which requests is to be made
        agent_id (str): Id used for request header
        api_key (str): API Key provided
        params_dict (Dict): Dictionary containing parameters to be passed in requests' get method

    Returns:
        Dictionary containing request content. None when exception are encountered.
    """
    req_headers = {"User-agent": agent_id, "AccountKey": api_key, "Content-Type": "application/json"}
    try:
        res = requests.get(url=api_link,
                           params=params_dict,
                           headers=req_headers,
                           timeout=5)
        # Raise if HTTPError occured
        res.raise_for_status()

        # Check the status code before extending the number of posts
        if res.status_code == 200:
            print(f"Request successful with status code {res.status_code}")
            the_json = res.json()
            return the_json
        else:
            print(f"Return unssucessful with status code {res.status_code}")
            return res.status_code

    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)
    return None


def geodesic_distance_filter(centre_point: Tuple[float,float] , radius_in_km: float, data_list: List[Dict], latitude_key_name: str, longitude_key_name: str) -> List[Dict]:
    """Function which filters out locations from a list of locations of a particular transport related artifact of interest(e.g bus stops, taxi stands) that is located within a specified radius(radius_in_km) of a point of interest(centre_point).

    Args:
        centre_point (Tuple[float,float]): WGS84 Lat,Lon coordinates
        radius_in_km (float): Radius of centre_point considered
        data_list (List[Dict]): List of dictionary containing geographic related artefacts. 
        latitude_key_name (str): Dictionary key name representing latitude information in data_list
        longitude_key_name (str): Dictionary key name representing longitude information in data_list

    Returns:
        List of dictionary containing geographic related artefacts that is within a radius of specified point of interest.
    """

    distance_list = np.array([geodesic(centre_point, tuple([data[latitude_key_name], data[longitude_key_name]])).kilometers for data in data_list])

    idx_min_distance_list = np.argmin(distance_list)

    nearest_data_point = data_list[idx_min_distance_list]
    within_radius_idx = np.argwhere(distance_list < radius_in_km)[0]
    nearby_points = [data_list[idx] for idx in within_radius_idx]

    return nearby_points, nearest_data_point

def query_filter_surrounding_transport_artefacts(
        api_link: str,
        point_of_interest: Tuple[float,float],
        radius:float
    ) -> List:
    api_response = api_query(api_link=api_link,
                             agent_id="test",
                             api_key=LTA_API_KEY)
    api_response_data_list = api_response.get("value")

    # Get nearby data
    surrounding_data_list, nearest_data_list = geodesic_distance_filter(
        centre_point=point_of_interest,
        radius_in_km=radius,
        data_list=api_response_data_list,
        latitude_key_name="Latitude",
        longitude_key_name="Longitude"
    )

    return surrounding_data_list, nearest_data_list

