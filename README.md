# Daily Photo Telegram Bot
One day I realized that we have many vacation photos on our family server that we rarely look at. Moreover, when it comes to adding photos, vacation photos are dumped from all the phones into a single folder without looking at them. I thought that it would be cool to have some sort of service that randomly picks a photo from preselected folders and send it to us to reminisce and review. A bot for a messenger Telegram fits the job description perfectly. It has been in operation since early 2020.

# Description
- Telegram Bots are not really designed for this. They are meant to be accessible to everybody. My solution to that is to restrict the bot to only listen and respond to one particular chat id, provided in the configuration file.
- Although Telegram has a Python package for an always-online service, I decided to simply use an API. First, it is not required for it to be always available. Second, the simpler the program the more difficult it is to abuse it.
- Every X number of hours a script launches and selects one photo at random from a preselected list of folders. Supported formats currently are **jpg**, **jpeg**, **png**, and **bmp**. The image also cannot be more than 10 MB due to Telegram's limitations.
- The EXIF data gets extracted from the image. The two things I am interested in are the date and time when the photo was taken and the GPS coordinates.
- The bot sends the image to our family chat along with its relative path, the date/time it was taken (or the date/time of the file creation, if not available), and a location pin if the image contained GPS data. Note that the image is uploaded to Telegram, which could be a potential security concern for some.
- There are two commands the bot supports, which are triggered by replying to the message containing the photo:
  - **/delete** - The command tells the bot to create a poll so we can vote on whether to remove the image from the server.
  - **/rotate cw|ccw** - The command tells the bot to rotate the image clockwise or counterclockwise and resend the image.
- These commands are processed by a separate script that runs once a minute.

# Learning Outcomes
This has been a great opportunity to learn about Telegram bots, EXIF, GPS, image processing, and how to use Python to iterate over very large lists that might not fit into memory.

# The Files
- **config.cfg-mock** - A mock configuration file that contains API token, chat id, bot id, and list of folders to look through. It also acts as temporary storage to help distinguish between processed and new messages and to store the ids of ongoing polls. Rename it to config.cfg when in use.
- **pb_sendPicture.py** - A script that you run (with cron, for example) whenever you want to send a new random image
- **pb_processUpdates.py** - A script that you run whenever you want to process user messages
- **Bot.py** - A convenient wrapper around Telegram API calls
- **FSUtils.py** - Some helpful functions related to the filesystem
- **EXIFUtils.py** - Some helpful functions for working with EXIF data
- **requirements.txt** - Contains Python package requirements for the project
