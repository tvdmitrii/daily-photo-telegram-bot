import os
from itertools import chain

"""
List of lowercase file extensions which defines whether a file is a photo or not.
"""
IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "bmp"]


def check_if_photo(file):
    """
    Checks if file is a photo by comparing its extension to IMAGE_EXTENSIONS list.

    :param file: absolute or relative file path
    :return: true if the file is a photo, false otherwise
    """
    _, extension = os.path.splitext(file)
    return extension.lower() in IMAGE_EXTENSIONS


def countFiles(directories):
    """
    Counts the total number of files in photo directories

    :param directories: list of absolute base file paths
    :return: total number of files
    """
    total = 0
    for _, _, files in chain.from_iterable(os.walk(directory) for directory in directories):
        total += len(files)
    return total


def getAbsolutePhotoPaths(directories):
    """
    Get absolute paths of all photos in directories. Uses yield to improve performance.

    :param directories: list of absolute base file paths
    :return: generator for absolute photo path
    """
    for dir_path, _, files in chain.from_iterable(os.walk(directory) for directory in directories):
        for file in files:
            yield os.path.abspath(os.path.join(dir_path, file))


def getRelativePath(abs_photo_path, base_paths):
    """
    Extracts the photo's path relative to bot's base folder paths.
    Photos shouldn't have identical relative paths unless they are copies.

    :param abs_photo_path: absolute photo path
    :param base_paths: list of absolute base file paths
    :return: relative photo path
    """
    for base in base_paths:
        parts = abs_photo_path.split(base)
        if len(parts) == 1:
            continue
        else:
            return parts[1][1:]

    return None


def getAbsolutePath(rel_path, base_paths):
    """
    Reconstructs absolute photo path from relative photo path,

    :param rel_path: relative photo path
    :param base_paths: list of absolute base file paths
    :return: absolute photo path
    """
    abs_path = ""
    for folder in base_paths:
        abs_path = folder + "/" + rel_path
        if not os.path.exists(abs_path):
            continue

    return abs_path
