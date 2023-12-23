import re
import os
import requests
import asyncio

from dotenv import load_dotenv, find_dotenv

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup

from main import dp

try:
    from db.database import session
    from db.crud import *
except ModuleNotFoundError | ImportError:
    print(os.getcwd())
    print(os.listdir())
    exit()

from time import sleep

# def sendTelegram(user_ids, data):
#     token = os.getenv('API_TOKEN')
#     url = "https://api.telegram.org/bot"
#     url += token
#     method = url + "/sendMessage"
#     for user_id in user_ids:
#         r = requests.post(method, data={
#             "chat_id": user_id,
#             "text": f"Просим обратить внимание на то, что срок поставки по заказу {data[0]} истек {data[1]}"
#             })

#     if r.status_code != 200:
#         raise Exception("post_text error")


async def main():
    while True:
        events = check_if_up_to_date(session)
        for i in events:
            if i[1] == 1:
                continue
            elif i[1] == 0:
                delete_event(session, i[0].id)
            else:

        sleep(3600)


async def notify(message: types.Message, )


asyncio.run(main())
