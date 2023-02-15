from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime
import os

"""
Dictionary of EXIF tags.
"""
_TAGS = dict(((v, k) for k, v in TAGS.items()))

"""
Dictionary of GPS EXIF tags.
"""
_GPSTAGS = dict(((v, k) for k, v in GPSTAGS.items()))


def _convert_to_degrees(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degrees.
    Credit to https://gist.github.com/snakeye/fdc372dbf11370fe29eb.

    :param value: GPS latitude or longitude from EXIF data
    :return: GPS latitude or longitude in degrees
    """
    d = float(value[0][0]) / float(value[0][1])
    m = float(value[1][0]) / float(value[1][1])
    s = float(value[2][1]) / float(value[2][1])

    return d + (m / 60.0) + (s / 3600.0)


def getGPSData(exif_data):
    """
    Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)
    Slightly modified from https://gist.github.com/snakeye/fdc372dbf11370fe29eb.

    :param exif_data: EXIF data from a photo
    :return: latitude, longitude compatible with maps. None, None if exif_data does not exist.
    """
    try:
        gps_latitude = exif_data[_GPSTAGS['GPSLatitude']]
        gps_latitude_ref = exif_data[_GPSTAGS['GPSLatitudeRef']]
        gps_longitude = exif_data[_GPSTAGS['GPSLongitude']]
        gps_longitude_ref = exif_data[_GPSTAGS['GPSLongitudeRef']]

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _convert_to_degrees(gps_latitude)
            if gps_latitude_ref[0] != 'N':
                lat = 0 - lat

            lon = _convert_to_degrees(gps_longitude)
            if gps_longitude_ref[0] != 'E':
                lon = 0 - lon
    except Exception:
        lat = None
        lon = None

    return lat, lon


def getDateTime(exif_data, image_path):
    """
    Extracts date/time from EXIF data. Uses filesystem file creation time as a fallback.

    :param exif_data: EXIF data from a photo
    :param image_path: absolute path to a photo
    :return: string containing date/time of when the photo was taken / file was created
    """
    try:
        date_time = str(exif_data[_TAGS["DateTime"]])
        parts = date_time.split(" ")
        date = parts[0].split(":")
        time = parts[1].split(":")
        date_time = datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2]))
        date_time = "Photo taken on: " + date_time.strftime("%B %d %Y, %H:%M")
    except Exception:
        date_time = datetime.fromtimestamp(os.path.getctime(image_path))
        date_time = "File created on: " + date_time.strftime("%B %d %Y, %H:%M")

    return date_time
