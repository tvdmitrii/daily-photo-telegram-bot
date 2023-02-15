import json
import requests
import time
import logging
from FSUtils import *


class Bot:
    """
    A class that implements bot API commands.
    ...

        Attributes
        ----------
        logger : logs any errors that occur
        config_path : absolute path to the config file
        config : bot configuration dictionary in a JSON format
        base_url : base url for API calls including the auth token
    """

    def __init__(self, config_path):
        """
        Bot class constructor. Mainly loads the config dictionary.

        :param config_path: absolute path to the config file
        """
        self.logger = logging.getLogger(__name__)

        # Read config file
        self.config_path = config_path
        file = open(config_path, "r")
        self.config = json.loads(file.read())
        file.close()

        self.base_url = "https://api.telegram.org/bot" + self.config["token"]
        # self.last_update_id = self.config["last_update_id"]
        # self._check_polls()

    def logErrorResponse(self, response):
        """
        Logs nicely formated API response in case if response is not OK.

        :param response: response to be logged
        :return: void
        """
        self.logger.error(json.dumps(response, indent=4, sort_keys=True))

    def sendPhoto(self, image_path, caption):
        """
        Wrapper around sendPhoto API request.

        :param image_path: absolute path to the photo
        :param caption: caption for the photo
        :return: response
        """
        url = self.base_url + '/sendPhoto?chat_id=' + self.config["chat_id"] + "&caption=" + caption
        data = {'photo': open(image_path, 'rb')}
        response = requests.post(url, files=data).json()

        if not response["ok"]:
            self.logErrorResponse(response)

        return response

    def sendMessage(self, text, reply_to_message_id=None):
        if reply_to_message_id is None:
            url = self.base_url + '/sendMessage?chat_id=' + self.config["chat_id"] + "&text=" + str(text)
        else:
            url = self.base_url + '/sendMessage?chat_id=' + self.config["chat_id"] + "&text=" + str(
                text) + "&reply_to_message_id=" + str(reply_to_message_id)

        response = requests.post(url).json()

        if not response["ok"]:
            self.logErrorResponse(response)

        return response

    def deleteMessage(self, message_id):
        url = self.base_url + '/deleteMessage?chat_id=' + self.config["chat_id"] + "&message_id=" + str(message_id)
        response = requests.post(url).json()

        if not response["ok"]:
            self.logErrorResponse(response)

        return response

    def sendVenue(self, latitude, longitude):
        url = self.base_url + '/sendVenue?chat_id=' + self.config["chat_id"] + "&latitude=" + str(
            latitude) + "&longitude=" + str(longitude) + "&title=&address="
        response = requests.post(url).json()

        if not response["ok"]:
            self.logErrorResponse(response)

        return response

    def _voted_to_delete_photo(self, poll):
        self.deleteMessage(poll["image_message_id"])
        os.remove(poll["image_path"])
        self.sendMessage("The photo was deleted!", poll["poll_message_id"])

    def _voted_to_keep_photo(self, poll):
        r = self.sendMessage("The photo stays!", poll["poll_message_id"])

    def _check_polls(self):
        indexes = []
        for i, poll in enumerate(self.config["polls"]):
            if poll["close_date"] <= time.time():
                indexes.append(i)
                [yes, no] = self.stopPoll(poll["poll_message_id"])
                if yes > no:
                    self._voted_to_delete_photo(poll)
                else:
                    self._voted_to_keep_photo(poll)

        indexes = reversed(indexes)
        for i in indexes:
            del self.config["polls"][i]

        file = open(self.config_path, 'w')
        file.write(json.dumps(self.config))
        file.close()

    def _save_poll(self, poll_message_id, close_date, image_path, image_message_id):
        dict = {"poll_message_id": poll_message_id, "close_date": close_date, "image_path": image_path,
                "image_message_id": image_message_id}
        self.config["polls"].append(dict)
        file = open(self.config_path, 'w')
        file.write(json.dumps(self.config))
        file.close()

    def sendPoll(self, question, options, open_period, reply_to_message_id):
        url = self.base_url + '/sendPoll?chat_id=' + self.config["chat_id"] + "&question=" + question + \
              "&reply_to_message_id=" + str(reply_to_message_id)
        data = {'options': json.dumps(options)}
        response = requests.post(url, data).json()

        if response["ok"]:
            poll_message_id = str(response["result"]["message_id"])
            close_date = response["result"]["date"] + open_period
            caption = str(response["result"]["reply_to_message"]["caption"])
            image_path = getAbsolutePath(caption.split("\n")[0], self.config["folders"])
            image_message_id = str(response["result"]["reply_to_message"]["message_id"])
            self._save_poll(poll_message_id, close_date, image_path, image_message_id)
        else:
            self.logErrorResponse(response)

        return response

    def stopPoll(self, message_id):
        url = self.base_url + '/stopPoll?chat_id=' + self.config["chat_id"] + "&message_id=" + str(message_id)
        response = requests.post(url).json()

        yes = 0
        no = 0
        if response["ok"]:
            for option in response["result"]["options"]:
                if option["text"].lower() == "yes":
                    yes = option["voter_count"]
                if option["text"].lower() == "no":
                    no = option["voter_count"]
        else:
            self.logErrorResponse(response)

        return [yes, no]

    def getUpdates(self):
        url = self.base_url + '/getUpdates?offset=' + str(self.config["last_update_id"] + 1)
        r = requests.post(url).json()

        updates = []
        for result in r["result"]:
            self.config["last_update_id"] = result["update_id"]

            try:
                chat_id = str(result["message"]["chat"]["id"])

                # Ignore updates from the incorrect chats
                if chat_id != self.config["chat_id"]:
                    continue
                reply_from_id = str(result["message"]["reply_to_message"]["from"]["id"])

                # Must be a message with a photo
                photo = result["message"]["reply_to_message"]["photo"]

                # Ignore replies to non-bot messages
                if reply_from_id != self.config["bot_id"]:
                    continue

                caption = result["message"]["reply_to_message"]["caption"]
                reply_text = result["message"]["text"]

            # Ignore messages that are not replies
            except KeyError as err:
                continue

            updates.append(result)

        return updates

    def close(self):
        self.config.update({"last_update_id": self.config["last_update_id"]})
        file = open(self.config_path, 'w')
        file.write(json.dumps(self.config))
        file.close()
