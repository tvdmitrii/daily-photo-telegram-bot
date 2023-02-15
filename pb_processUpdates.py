#!./bin/python

from PIL import Image
from Bot import Bot, get_image_path


def execute_command(bot, reply_text, path, caption, message_id):
    reply_parts = reply_text.split(" ")
    if reply_parts[0][0] != "/":
        return

    if reply_parts[0] == "/rotate":
        image = Image.open(path)

        try:
            exif_data = image.info['exif']
        except KeyError:
            exif_data = None

        if len(reply_parts) != 2:
            image.close()
            bot.sendMessage("Syntax: /rotate cw|ccw")
            return

        if reply_parts[1] == "ccw":
            rotated = image.transpose(method=Image.ROTATE_90)
        elif reply_parts[1] == "cw":
            rotated = image.transpose(method=Image.ROTATE_270)
        else:
            image.close()
            bot.sendMessage("Syntax: /rotate cw|ccw")
            return

        image.close()
        if exif_data is not None:
            rotated.save(path, 'jpeg', quality=95, exif=exif_data)
        else:
            rotated.save(path, 'jpeg', quality=95)
        rotated.close()

        bot.deleteMessage(message_id)
        bot.sendPhoto(path, caption)

    elif reply_parts[0] == "/delete":
        bot.sendPoll("Should we remove this photo?", ["Yes", "No"], 43200, message_id)


bot = Bot("config.cfg")
updates = bot.getUpdates()

for update in updates:
    try:
        message_id = str(update["message"]["reply_to_message"]["message_id"])
        caption = update["message"]["reply_to_message"]["caption"]
        reply_text = update["message"]["text"]
        image_path = get_image_path(caption, bot.config["folders"])
        execute_command(bot, reply_text, image_path, caption, message_id)

    # Ignore messages that are not replies
    except KeyError as err:
        continue

bot.close()

