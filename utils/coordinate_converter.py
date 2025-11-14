"""
Helper functions for coordinate system conversions.
"""
from pyproj import Transformer
from typing import Tuple, Union
import pandas as pd


def convert_svy21_to_wgs84(x_coord: float, y_coord: float) -> Tuple[float, float]:
    """
    Convert coordinates from SVY21 (EPSG:3414) to WGS84 lat/lon (EPSG:4326).
    
    SVY21 is Singapore's projected coordinate system, and this function converts
    it to standard latitude/longitude coordinates (WGS84).
    
    Args:
        x_coord: X coordinate in SVY21 system
        y_coord: Y coordinate in SVY21 system
    
    Returns:
        Tuple of (latitude, longitude) in WGS84 format
    
    Example:
        >>> lat, lon = convert_svy21_to_wgs84(33758.4143, 33695.5198)
        >>> print(f"Lat: {lat}, Lon: {lon}")
    """
    # Create transformer from SVY21 (EPSG:3414) to WGS84 (EPSG:4326)
    svy21_to_wgs84 = Transformer.from_crs("EPSG:3414", "EPSG:4326")
    
    # Transform coordinates: returns (latitude, longitude)
    lat, lon = svy21_to_wgs84.transform(x_coord, y_coord)
    
    return lat, lon


def convert_dataframe_svy21_to_wgs84(
    df: pd.DataFrame, 
    x_col: str = "x_coord", 
    y_col: str = "y_coord",
    lat_col: str = "latitude",
    lon_col: str = "longitude"
) -> pd.DataFrame:
    """
    Convert SVY21 coordinates in a DataFrame to WGS84 lat/lon coordinates.
    
    This function adds new latitude and longitude columns to the DataFrame
    by converting the existing x_coord and y_coord columns from SVY21 to WGS84.
    
    Args:
        df: DataFrame containing x_coord and y_coord columns in SVY21
        x_col: Name of the x coordinate column (default: "x_coord")
        y_col: Name of the y coordinate column (default: "y_coord")
        lat_col: Name for the output latitude column (default: "latitude")
        lon_col: Name for the output longitude column (default: "longitude")
    
    Returns:
        DataFrame with added latitude and longitude columns
    
    Example:
        >>> df = pd.read_csv("data/HDBCarparkInformation.csv")
        >>> df_converted = convert_dataframe_svy21_to_wgs84(df)
    """
    # Create transformer from SVY21 (EPSG:3414) to WGS84 (EPSG:4326)
    svy21_to_wgs84 = Transformer.from_crs("EPSG:3414", "EPSG:4326")
    
    # Apply transformation row by row
    def convert_row(row):
        try:
            lat, lon = svy21_to_wgs84.transform(row[x_col], row[y_col])
            return pd.Series([lat, lon])
        except (ValueError, TypeError) as e:
            # Handle missing or invalid coordinates
            return pd.Series([None, None])
    
    # Apply conversion and assign to new columns
    df[[lat_col, lon_col]] = df.apply(convert_row, axis=1)
    
    return df

