from random import randint
from datetime import datetime
from typing import Union, Dict
from conf.logging_config
import logging
import os
import csv
import requests

logger = logging.getLogger("project")

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
            logger.info("Request sucessful with %s", res.status_code)
            the_json = res.json()
        return the_json['items']

    except requests.exceptions.HTTPError as errh:
        logging.error("Http Error: %s", errh)
    except requests.exceptions.ConnectionError as errc:
        logging.error("Error Connecting: %s", errc)
    except requests.exceptions.Timeout as errt:
        logging.error("Timeout Error: %s", errt)
    except requests.exceptions.RequestException as err:
        logging.error("Exception Error: %s", err)
    return None

def query_traffic_metadata(api_link: str, agent_id: str): 
    logging.info("Scraping image data via api query")
    cctv_feed = api_query(api_link=api_link, agent_id=agent_id)

    number_of_cameras = len(cctv_feed[0]["cameras"])

    for i in range(number_of_cameras):
        logging.info("Processing %s out of %s", i+1,number_of_cameras)
        camera_feed = cctv_feed[0]["cameras"][i]

        # Process information to dictionary
        metadata_dict = {"timestamp" : camera_feed["timestamp"],
                "image_url": camera_feed["image"],
                "lat": camera_feed["location"]["latitude"],
                "lon": camera_feed["location"]["longitude"],
                "camera_id": camera_feed["camera_id"],
                "height": camera_feed["image_metadata"]["height"],
                "width": camera_feed["image_metadata"]["width"],
                "md5": camera_feed["image_metadata"]["md5"]
        }
    return metadata_dict

def get_cctv_feed(metadata_dict: Dict, agent_id: str="Simple project"):
    """This function downloads the cctv image feed based on the url information provided as a response from LTA API response.
    Args:
      args_parsed:
        Command line inputs made by users containing model option number and the hyperparameters.
      metadata_dict:
        Ordered dictionary containing various metadata information as returned from LTA API call.
        
    Returns:
      None

    Raises:
      None
    """
    # Timestamp is in the form of yyyy-mm-ddThh:mm:ss+08:00. Convert to yyyymmdd_hhmmss to be used for image name
    rename_timestamp = metadata_dict["timestamp"].replace("-","_").replace(":","").replace("T","_")[:-5]

    # Extract the extension from the url
    extension = metadata_dict["image_url"].split(".")[-1]

    #Create folder based on camera id if required
    folder_name = metadata_dict["camera_id"]
    os.makedirs("./datasets/" + folder_name, exist_ok = True)

    # Define the name of the image to be downloaded
    img_file = "./datasets/" + folder_name + "/"+ rename_timestamp + "." + extension

    metadata_dict.update({"file_name": img_file})
    
    # Randomised agent id
    rand_agent_id = agent_id + str(randint(0,500))
    try:
        r = requests.get(metadata_dict["image_url"],
                        stream=True,
                        headers={'User-agent': rand_agent_id},
                        timeout=5
                        )

        # Raise if HTTPError occured
        r.raise_for_status()
        # Write to a file if success and log the status
        if r.status_code == 200:
            open(img_file, 'wb').write(r.content)
            logging.info("Successfully downloaded image file %s", metadata_dict["image_url"])

    except requests.exceptions.HTTPError as errh:
        logging.error("Http Error: %s", errh)
    except requests.exceptions.ConnectionError as errc:
        logging.error("Error Connecting: %s", errc)
    except requests.exceptions.Timeout as errt:
        logging.error("Timeout Error: %s", errt)
    except requests.exceptions.RequestException as err:
        logging.error("Exception Error: %s", err)
    return None

def get_cctv_coordinates(args_parsed):
    """Main function that extract,process and stores the metadata of the traffic cameras and the image footages returned through the querying of LTA's API for traffic images. It also downloads the traffic footages and organises the images into respective traffic camera ID

    Args:
      args_parsed:
        Parameters passed during script exection.

    Returns:
      None

    Raises:
      IOError: When file could not be accessed.
    """
    logging.info("Scraping image data via api query")
    cctv_feed = api_query(args_parsed)

    number_of_cameras = len(cctv_feed[0]["cameras"])
    # Metadata extraction for each camera

    try:
        # Open file in append mode and creates if does not exist
        with open(args_parsed.camera_coord_metadata, mode='w',
            encoding='utf-8') as csv_file:
            # Define headers and write content from dictionary
            headers = ['camera_id', 'lat', 'lon']
            writer = csv.DictWriter(csv_file, fieldnames = headers)
            writer.writeheader()
            for i in range(number_of_cameras):
                logging.info("Processing %s out of %s traffic cameras", i+1,number_of_cameras)
                camera_feed = cctv_feed[0]["cameras"][i]

                # Process information to dictionary
                cctv_location_dict = {
                    "camera_id": camera_feed["camera_id"],
                    "lat": camera_feed["location"]["latitude"],
                    "lon": camera_feed["location"]["longitude"],
                }
                writer.writerow(cctv_location_dict)
    except IOError as exc:
        logging.error("I/O error encountered when opening %s", args_parsed.
          camera_coord_metadata)
        raise IOError from exc
    return None
