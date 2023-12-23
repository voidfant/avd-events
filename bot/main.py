import logging 

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup

import os
from dotenv import load_dotenv, find_dotenv

from keyboards import *

try:
    from ..db.database import session
    # from db import database
    from ..db.crud import *
except ModuleNotFoundError | ImportError:
    print(os.getcwd())
    print(os.listdir())
    exit()



logging.basicConfig(level=logging.INFO)
load_dotenv(find_dotenv())
API_TOKEN = os.getenv('API_TOKEN')


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


isAdmin = True
platforms = ['Верхние Лихоборы', 'Войковская', '\"Живописно\"', 'Музей Света и Цвета']


class UserStates(StatesGroup):
    admin = State()
    adminAwaitEventName = State()
    adminAwaitClientName = State()
    adminAwaitPlatform = State()
    adminAwaitQuota = State()
    adminAwaitDescription = State()
    adminAwaitDateTime = State()
    client = State()
    employee = State()


@dp.message_handler(commands=['menu', 'меню', 'start', 'старт'])
async def start(message: types.Message, state: FSMContext):
    global isAdmin

    if isAdmin:
        await state.set_state(UserStates.admin.state)
        await state.update_data(event_name='')
        await state.update_data(client_name='')
        await state.update_data(event_platform='')
        await state.update_data(event_quota='')
        await state.update_data(event_description='')
        await state.update_data(event_datetime='')
        await message.answer("Добро пожаловать в админ-панель", reply_markup=AdminStartKeyboard.markup)
    else:
        await state.set_state(UserStates.client.state)
        await message.reply("Здравствуйте! Чем я могу помочь?", reply_markup=StartKeyboard.markup)
        

@dp.callback_query_handler(lambda c: c.data == 'cancel-event-reg', state=UserStates.admin)
async def goBack(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Добро пожаловать в админ-панель", reply_markup=AdminStartKeyboard.markup)


@dp.callback_query_handler(lambda c: c.data == 'confirm-event-reg', state=UserStates.admin)
async def confirmEvent(callback_query: types.CallbackQuery, state: FSMContext):
    eventData = await state.get_data()
    if not eventData['event_name'] or not eventData['client_name'] or not eventData['event_platform'] or not eventData['event_quota'] or not eventData['event_description'] or not eventData['event_datetime']:
        callback_query.message.answer('Заполните все поля!', reply_markup=types.ReplyKeyboardRemove())
        return
    # else:


# @dp.message_handler(state=UserStates.admin)
# async def adminPanel(message: types.Message, state: FSMContext):
    
# @dp.callback_query_handler(lambda c: c.data == 'cancel-event-reg', state=UserStates.admin)
# async def 

# @dp.callback_query_handler(lambda c: c.data == 'add-event', state=UserStates.admin)
# async def adminAddEvent(callback_query: types.CallbackQuery, state: FSMContext):

#     await callback_query.message.edit_text("Выберите тип мероприятия", reply_markup=AdminAddKeyboard.markup)


@dp.callback_query_handler(lambda c: c.data == 'add-event', state=UserStates.admin)
async def adminAddPrivateEvent(callback_query: types.CallbackQuery, state: FSMContext):
    eventData = await state.get_data()
    await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nИмя клиента: {eventData['client_name']}\nПлощадка проведения: {eventData['event_platform']}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nДата и время проведения мероприятия: {eventData['event_datetime']}", 
                                           reply_markup=AdminAddPrivateKeyboard.markup)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(lambda c: c.data == 'enter-event-name', state=UserStates.admin)
async def adminEnterEventName(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Введите название мероприятия", reply_markup=AdminConfirmPrivateEventDataKeyboard.markup)
    await state.set_state(UserStates.adminAwaitEventName.state)


@dp.message_handler(state=UserStates.adminAwaitEventName)
async def adminAwaitEventName(message: types.Message, state: FSMContext):
    await state.update_data(event_name=message.text)
    await state.set_state(UserStates.admin.state)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(lambda c: c.data == 'enter-client-name', state=UserStates.admin)
async def adminEnterClientName(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Введите имя клиента", reply_markup=AdminConfirmPrivateEventDataKeyboard.markup)
    await state.set_state(UserStates.adminAwaitClientName.state)


@dp.message_handler(state=UserStates.adminAwaitClientName)
async def adminAwaitClientName(message: types.Message, state: FSMContext):
    await state.update_data(client_name=message.text)
    await state.set_state(UserStates.admin.state)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(lambda c: c.data == 'enter-event-platform', state=UserStates.admin)
async def adminEnterPlatform(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Выберите платформу проведения мероприятия", reply_markup=AdminConfirmPrivateEventDataKeyboard.markup)
    await callback_query.message.answer('Выберите один из предложенных вариантов', reply_markup=SelectPlatform.markup)
    await state.set_state(UserStates.adminAwaitPlatform.state)


@dp.message_handler(state=UserStates.adminAwaitPlatform)
async def adminAwaitPlatform(message: types.Message, state: FSMContext):
    if message.text not in platforms:
        await message.answer('Выберите один из предложенных вариантов')
        return
    await state.update_data(event_platform=message.text)
    await state.set_state(UserStates.admin.state)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(lambda c: c.data == 'enter-event-quota', state=UserStates.admin)
async def adminEnterPlatform(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Введите количество гостей", reply_markup=AdminConfirmPrivateEventDataKeyboard.markup)
    await state.set_state(UserStates.adminAwaitQuota.state)


@dp.message_handler(state=UserStates.adminAwaitQuota)
async def adminAwaitPlatform(message: types.Message, state: FSMContext):
    await state.update_data(event_quota=message.text)
    await state.set_state(UserStates.admin.state)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(lambda c: c.data == 'enter-event-description', state=UserStates.admin)
async def adminEnterPlatform(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Введите описание мероприятия", reply_markup=AdminConfirmPrivateEventDataKeyboard.markup)
    await state.set_state(UserStates.adminAwaitDescription.state)


@dp.message_handler(state=UserStates.adminAwaitDescription)
async def adminAwaitPlatform(message: types.Message, state: FSMContext):
    await state.update_data(event_description=message.text)
    await state.set_state(UserStates.admin.state)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(lambda c: c.data == 'enter-event-datetime', state=UserStates.admin)
async def adminEnterPlatform(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Введите дату и время проведения мероприятия в формате: \"дд.мм.гггг чч:мм:cc\".\n\nПример: 20.01.1976 13:05:00", reply_markup=AdminConfirmPrivateEventDataKeyboard.markup)
    await state.set_state(UserStates.adminAwaitDateTime.state)


@dp.message_handler(state=UserStates.adminAwaitDateTime)
async def adminAwaitPlatform(message: types.Message, state: FSMContext):
    await state.update_data(event_datetime=message.text)
    await state.set_state(UserStates.admin.state)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



@dp.callback_query_handler(lambda c: c.data == 'subscriptions', state=UserStates.client)
async def subscriptions(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Ха-ха! Хуй!", reply_markup=StartKeyboard.markup)


@dp.callback_query_handler(lambda c: c.data == 'my-events', state=UserStates.client)
async def subscriptions(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Выберите дату", reply_markup=StartKeyboard.markup)


@dp.callback_query_handler(lambda c: c.data == 'upcoming-events', state=UserStates.client)
async def subscriptions(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Выберите филиал", reply_markup=StartKeyboard.markup)


@dp.callback_query_handler(lambda c: c.data.startswith("event-"), state=UserStates.client)
async def showEvent(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Меро типа", reply_markup=SubscribeKeyboard.markup)



if __name__ == '__main__':
    # registered_users = dict(get_users(session))
    # logging.log(logging.INFO, registered_users)
    executor.start_polling(dp, skip_updates=True)


