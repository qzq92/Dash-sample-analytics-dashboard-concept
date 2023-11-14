import pandas as pd
import logging

logger = logging.getLogger("project")

def process_traffic_cam_locations(filepath:str = "traffic_cams_location.csv") -> pd.DataFrame:
    """
    Function which loads in from a file containing a list of traffic camera locations. If such file is missing, causeway cctv footage information is constructed as a fallback.

    Args:
        filepath (str, optional): CSV File containing list of approximate location description based on known lat lon location of traffic camera positions based on 2021 data. Defaults to "traffic_cams_location.csv".

    Returns:
        pd.DataFrame: Loaded or constructed dataframe of traffic cam location.
    """
    try:
        traffic_cam_df = pd.read_csv(filepath)
      
    except FileNotFoundError:
        logger.error("File not found. Using limited data")
        fallback_sample_data_dict = {
            "ID": 2701,
            "Lat": 1.447023728,
            "Lon":	103.7716543,
            "Description":	"Causeway"

        }
        traffic_cam_df = pd.DataFrame.from_dict(fallback_sample_data_dict)

    return traffic_cam_df