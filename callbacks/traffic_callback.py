# Create a traffic callback to extract latest traffic from link ID 2701 (causeway) and 4713 (second link ) via lta API

from typing import Union, Dict
import base64
import requests
import numpy as np
from datetime import datetime
def api_query(api_link: str,  agent_id: str) -> Union[Dict,None]:
    """Function which executes query via an api link using a provided agent_id as an identifier to avoid rejection of query request

    Args:
        api_link (str): API Link which requests is to be made
        agent_id (str): Id used for request header

    Returns:
        Dictioanry containing request content. None when exception are encountered.
    """
    req_headers = {"User-agent": agent_id}
    try:
        res = requests.get(api_link,
                            headers=req_headers,
                            timeout=5)
        # Raise if HTTPError occured
        res.raise_for_status()

        # Check the status code before extending the number of posts
        if res.status_code == 200:
            print("Request sucessful for traffic_callback")
            the_json = res.json()
            return the_json['items']
        return None

    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)
    return None

def query_traffic_metadata():
    api_link = "https://api.data.gov.sg/v1/transport/traffic-images"
    agent_id = "test_qzq"
    cctv_feed = api_query(api_link=api_link, agent_id=agent_id)
    all_traffic_metadata_dict = {}
    if not cctv_feed:
        print("No response received")
        return {}
    number_of_cameras = len(cctv_feed[0]["cameras"])
    print(number_of_cameras)
    for i in range(number_of_cameras):
        camera_feed = cctv_feed[0]["cameras"][i]

        # Process information to dictionary
        metadata_dict = {"timestamp" : camera_feed["timestamp"],
                "image_url": camera_feed["image"],
                "lat": camera_feed["location"]["latitude"],
                "lon": camera_feed["location"]["longitude"],
                "md5": camera_feed["image_metadata"]["md5"]
        }
        all_traffic_metadata_dict[camera_feed["camera_id"]] = metadata_dict
    return all_traffic_metadata_dict


def get_camera_feed(metadata_dict: Dict, camera_id: str, agent_id: str="test_qzq"):
    try:
        # Extract the camera id from metadata_dict to obtain its metadata of interest
        specific_camera_metadata_dict = metadata_dict[camera_id]

    except KeyError:
        print("Invalid id received. No information obtained")
        return None

    # Randomised agent id
    rand_agent_id = agent_id + str(np.random.randint(0,500))
    try:
        response = requests.get(specific_camera_metadata_dict["image_url"],
                        stream=True,
                        headers={'User-agent': rand_agent_id},
                        timeout=5
                        )

        # Raise if HTTPError occured
        response.raise_for_status()
        # Write to a file if success and log the stat
        return response.raw
    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)
    return None


def get_camera_image_base64(metadata_dict: Dict, camera_id: str, agent_id: str = "test_qzq") -> str:
    """
    Get camera feed image and convert to base64 string for display in Dash.
    
    Args:
        metadata_dict: Dictionary containing camera metadata
        camera_id: Camera ID to fetch
        agent_id: User agent ID for request header
    
    Returns:
        Base64 encoded image string or None if error
    """
    try:
        raw_response = get_camera_feed(metadata_dict, camera_id, agent_id)
        if raw_response is None:
            return None
        
        # Read the raw response content
        image_data = raw_response.read()
        
        # Convert to base64
        base64_string = base64.b64encode(image_data).decode('utf-8')
        
        # Determine image format (assuming JPEG, but could be PNG)
        # Most traffic camera feeds are JPEG
        image_format = "jpeg"
        
        # Return data URI format
        return f"data:image/{image_format};base64,{base64_string}"
    except (IOError, ValueError, AttributeError) as error:
        print(f"Error converting image to base64 for camera {camera_id}: {error}")
        return None


def format_metadata_text(metadata_dict, camera_id):
    """
    Format metadata text for display under camera image.

    Args:
        metadata_dict: Dictionary containing all camera metadata
        camera_id: Camera ID to get metadata for

    Returns:
        Formatted metadata string with datetime and location (camera ID and lat/lon excluded)
    """
    try:
        if not metadata_dict or camera_id not in metadata_dict:
            return "Metadata unavailable"

        camera_meta = metadata_dict[camera_id]
        timestamp = camera_meta.get('timestamp', 'N/A')
        lat = camera_meta.get('lat')
        lon = camera_meta.get('lon')

        location = "Causeway" if camera_id=="2701" else "Second Link"

        # Format timestamp (assuming ISO format like "2024-01-01T12:00:00+08:00")
        formatted_time = ""
        if timestamp and timestamp != 'N/A':
            try:
                if isinstance(timestamp, str):
                    # Try to parse and format the timestamp
                    parsed_datetime = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = parsed_datetime.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    formatted_time = str(timestamp)
            except (ValueError, AttributeError):
                formatted_time = str(timestamp) if timestamp else ""

        # Build metadata text (excluding camera ID and lat/lon)
        metadata_parts = []
        
        # Add datetime if available
        if formatted_time:
            metadata_parts.append(f"Time: {formatted_time}")
        
        # Add location
        metadata_parts.append(location)

        return " | ".join(metadata_parts)
    except (KeyError, AttributeError, TypeError, ValueError) as error:
        print(f"Error formatting metadata: {error}")
        return "Metadata unavailable"


def register_camera_feed_callbacks(app):
    """
    Register callbacks for displaying camera feed images on the main page.
    """
    from dash import Input, Output

    @app.callback(
        [Output('camera-feed-2701', 'src'),
         Output('camera-feed-4713', 'src'),
         Output('camera-2701-metadata', 'children'),
         Output('camera-4713-metadata', 'children')],
        Input('interval-component', 'n_intervals')
    )
    def update_camera_feeds(n_intervals):
        """
        Update camera feed images periodically.

        Args:
            n_intervals: Number of intervals (from dcc.Interval component)

        Returns:
            Tuple of (image_2701, image_4713, metadata_2701, metadata_4713)
        """
        # n_intervals is required by the callback but not used directly
        _ = n_intervals
        try:
            # Get metadata for all cameras
            metadata_dict = query_traffic_metadata()

            if not metadata_dict:
                return None, None, "Metadata unavailable", "Metadata unavailable"

            # Get images for specific cameras
            img_2701 = get_camera_image_base64(metadata_dict, "2701")
            img_4713 = get_camera_image_base64(metadata_dict, "4713")

            # Get metadata text
            meta_2701 = format_metadata_text(metadata_dict, "2701")
            meta_4713 = format_metadata_text(metadata_dict, "4713")

            return img_2701, img_4713, meta_2701, meta_4713
        except (KeyError, AttributeError, TypeError) as error:
            print(f"Error updating camera feeds: {error}")
            return None, None, "Metadata unavailable", "Metadata unavailable"
