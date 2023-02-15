#!./bin/python

import random
import itertools
import logging
from PIL import Image
from Bot import Bot
from FSUtils import *
from EXIFUtils import *

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB


def getRandomPhoto(base_path):
    """
        Counts the number of files in folders and generates a random integer to pick one file.
        If file is not a photo it is skipped.

        :param base_path: list of base photo file paths from which a photo will be selected
        :return: absolute file path to a photo
        """
    N_files = countFiles(base_path)

    abs_photo_paths = getAbsolutePhotoPaths(base_path)
    log = logging.getLogger(__name__)

    log.info("getRandomPhoto. Generating random photo ...")
    log.info("Total number of files: " + str(N_files))

    while 1 > 0:
        file_number = random.randint(0, N_files - 1)
        log.info("Choosing file number: " + str(file_number))
        image_path = next(itertools.islice(abs_photo_paths, file_number, None))
        log.info("Picked photo: " + str(image_path))

        # Check that file is a photo
        if ~check_if_photo(image_path):
            log.info("Not an image! Skipping... ")
            continue

        # Check that a photo is not too large
        size = os.path.getsize(image_path)
        if size > MAX_IMAGE_SIZE:
            log.info("Image is too large! Size: " + str(size / 1024 / 1024) + " MB. Skipping ...")
            continue

    abs_photo_paths.close()
    return image_path


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename="picture_bot.log",
                    level=logging.INFO)

bot = Bot("config.cfg")

image_path = getRandomPhoto(bot.config["folders"])
image = Image.open(image_path)
exif_data = image._getexif()
image.close()

[latitude, longitude] = getGPSData(exif_data)
date_time = getDateTime(exif_data, image_path)

rel_path = getRelativePath(image_path, bot.config["folders"])
caption = rel_path + "\n" + date_time
bot.sendPhoto(image_path, caption)

if latitude and longitude:
    bot.sendVenue(latitude, longitude)

bot.close()
