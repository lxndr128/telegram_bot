from daemon import runner
from pymemcache.client.base import Client
from pymemcache import serde
from datetime import datetime
import time
import asyncio
import httpx
import requests
import os
import json
import random
import importlib


UPDATE_ID = 0
LOG_NAME = str(datetime.now()) + "_" + "log"
STDOUT_PATH = os.environ["PATH_TO_BOT"] + f'/logs/{LOG_NAME}.txt'
STDERR_PATH = os.environ["PATH_TO_BOT"] + f'/logs/{LOG_NAME}.error'
INNER_LOGS = os.environ["PATH_TO_BOT"] + f'/logs/{LOG_NAME}.inner'


def catch_exeption(function):
    def wrapper(*arg):
        try:
            return function(*arg)
        except Exception as exc:
            with open(INNER_LOGS, "a+") as log:
                log.write(str(exc) + str(datetime.now()) +  "\n")
            return []
    return wrapper


@catch_exeption
def get_messages(update_id=None):
    token = os.environ['BOT_ID']
    link = f'https://api.telegram.org/bot{ token }/getUpdates'
    data_ = {'offset': update_id}
    return requests.post(link, data=data_).json()["result"]


def process_messages(messages):
    global UPDATE_ID
    lib_list = os.listdir(os.environ["PATH_TO_BOT"] + '/lib')
    functions = [i[:-3] for i in lib_list if ".py" in i]

    async def send(id, text):
        client = Client('localhost', serde=serde.pickle_serde)
        if client.get(str(id)) != None and "minesweeper" not in text:
            text = ["minesweeper", ' '.join(text)]
        if text[0] in functions:
            lib = importlib.import_module(f"lib.{ text[0] }")
            data = [None, text[-1]][len(text) == 2]
            result = await lib.module((id, data))
        else:
            lib = importlib.import_module("lib.default_answer")
            result = await lib.module()
        await send_response(id, *result)

    loop = asyncio.new_event_loop()
    tasks = []
    id_handler = []
    block_id = []

    for i in messages:
        if i == messages[-1]:
            UPDATE_ID = i["update_id"] + 1
        if 'message' not in i.keys():
            continue
        id = i["message"]["from"]["id"]

        if id in block_id:
            continue
        elif id in id_handler:
            txt = "Не более одного запроса за раз, пожалуйста."
            block_id.append(id)
            tasks.append(loop.create_task(send_response(id, txt)))
            continue

        if "photo" in i["message"].keys():
            text = ["echo", "Я не умею смотреть на картинки."]
        elif "text" in i["message"].keys():
            text = i["message"]["text"].split(" ", 1)
        elif "document" in i["message"].keys():
            text = ["echo", "Мне это не нужно."]
        else:
            text = ["echo", "?"]

        id_handler.append(id)
        tasks.append(loop.create_task(send(id, text)))

    if tasks != []:
        group = asyncio.gather(*tasks)
        loop.run_until_complete(group)
        loop.close()


@catch_exeption
async def send_response(id, data, is_image=False):
    token = os.environ['BOT_ID']
    slug = ['/sendMessage', '/sendPhoto'][is_image]
    link = f'https://api.telegram.org/bot{ token + slug }'
    if is_image:
        if isinstance(data, str):
            data_ = {'chat_id': id, 'photo': data}
            await httpx.AsyncClient().post(link, data=data_)
        else:
            data_ = {'chat_id': id}
            file = {'photo': data}
            await httpx.AsyncClient().post(link, data=data_, files=file)
    else:
        keyboard = []
        if "Список функций:" in data:
            keys = [[i[2:]] for i in data.split("\n")[1:][:-2]]
            keyboard = json.dumps({'keyboard': keys,
                                   'one_time_keyboard': True})
        data_ = {'chat_id': id, 'text': data, 'reply_markup': keyboard}
        await httpx.AsyncClient().post(link, data=data_)


class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = STDOUT_PATH
        self.stderr_path = STDERR_PATH
        self.pidfile_path = '/tmp/telegram_bot.pid'
        self.pidfile_timeout = 5

    def run(self):
        while True:
            messages = get_messages(UPDATE_ID)
            if messages != []:
                process_messages(messages)
            time.sleep(1)


if __name__ == "__main__":
    app = App()
    daemon_runner = runner.DaemonRunner(app)
    daemon_runner.do_action()
