import os
import re
from typing import Optional

from fastapi import FastAPI, Request
import telegram

import sys

sys.path.insert(1, '..')

from telebot import credentials, ai
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

global bot
global TOKEN
TOKEN = os.getenv('BOT_TOKEN')
URL = os.getenv('URL')
bot = telegram.Bot(token=TOKEN)

sentry_sdk.init(
    dsn="https://c8a4639aa2cb4217a5a9c8de5e76e00e@o863874.ingest.sentry.io/5840018",
    integrations=[FlaskIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)

app = FastAPI()


@app.post('/{}'.format(TOKEN))
async def respond(request: Request):
    print(request)
    body = await request.json()
    event = request.headers.get("X-Github-Event")
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(body, bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode('utf-8').decode()
    # for debugging purposes only
    print("got text message :", text)
    # the first time you chat with the bot AKA the welcoming message
    if text == "/start":
        # print the welcoming message
        bot_welcome = """
       Welcome to coolAvatar bot, the bot is using the service from http://avatars.adorable.io/ to generate cool looking avatars based on the name you enter so please enter a name and the bot will reply with an avatar for your name.
       """
        # send the welcoming message
        bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)
    else:
        try:
            # clear the message we got from any non alphabets
            text = re.sub(r"\W", "_", text)
            # create the api link for the avatar based on http://avatars.adorable.io/
            url = "https://api.adorable.io/avatars/285/{}.png".format(text.strip())
            # reply with a photo to the name the user sent,
            # note that you can send photos by url and telegram will fetch it for you
            # bot.sendPhoto(chat_id=chat_id, photo=url, reply_to_message_id=msg_id)
            reply = ai.generate_smart_reply(text)
            bot.sendMessage(chat_id=chat_id, text=reply, reply_to_message_id=msg_id)
        except Exception:
            # if things went wrong
            bot.sendMessage(chat_id=chat_id,
                            text="There was a problem in the name you used, please enter different name",
                            reply_to_message_id=msg_id)

    return 'ok'


@app.api_route("/webhook", methods=["GET", "POST"])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.get('/')
def index():
    return {"Hello": "World"}
