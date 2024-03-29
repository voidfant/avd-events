import logging 
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup


import re
import os
from datetime import time
from collections import defaultdict

from dotenv import load_dotenv, find_dotenv

from bot.keyboards import *
from tools import *

try:
    from db.database import session
    from db.crud import *
except ModuleNotFoundError | ImportError:
    print(os.getcwd())
    print(os.listdir())
    exit()

logging.basicConfig(level=logging.INFO)
load_dotenv(find_dotenv())
API_TOKEN = os.getenv('API_TOKEN')

bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot,storage=storage)
dp.middleware.setup(LoggingMiddleware())

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

platforms = {'verh': 'Верхние Лихоборы', 'voyk': 'Войковская', 'zhiv': '\"Живописно\"', 'musm': 'Музей Света и Цвета', '': ''}
event_isPublic = {1: 'Открытое', 0: 'Закрытое', '': ''}
event_reverseIsPublic = {'public': 1, 'private': 0}
weekdays_arr = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
intervals_arr = ['11:00 - 13:00', '12:00 - 14:00', '13:00 - 15:00', '14:00 - 16:00', '15:00 - 17:00', '16:00 - 18:00', '17:00 - 19:00', '18:00 - 20:00', '19:00 - 21:00']


class UserStates(StatesGroup):
    admin = State()
    adminAwaitEventName = State()
    adminAwaitClientName = State()
    adminAwaitPlatform = State()
    adminAwaitQuota = State()
    adminAwaitDescription = State()
    adminAwaitDateTime = State()
    adminAwaitType = State()
    adminAwaitSelectToDel = State()
    adminAwaitSelectToEdit = State()
    adminAwaitForwardMsg = State()
    adminAwaitEmpName = State()
    adminSearchSelectPlatform = State()
    adminAwaitSelectEmpToDel = State()
    adminSeekApplications = State()
    AdminAwaitRepeatSelect = State()
    AdminSelectInterval = State()
    adminAwaitSelectClassToEdit = State()
    adminAwaitSelectClassToDel = State()
    client = State()
    clientRegName = State()
    clientRegPhone = State()
    clientAwaitSelectToView =State()
    clientAwaitApplicationName = State()
    clientAwaitApplicationChildrenName = State()
    clientAwaitApplicationPhone = State()
    clientAwaitApplicationGuestsAmount = State()
    clientAwaitSelectViewApplication = State()
    employee = State()
    empAwaitSelectToView = State()
    empAwaitSelectTable = State()
    


@dp.callback_query_handler(text='empty-callback', state='*')
async def emptyCallBackHandler(callback_query: types.CallbackQuery, state: FSMContext):
    pass

@dp.callback_query_handler(lambda c: c.data == 'admin-cancel', state=[UserStates.admin, 
                                                                UserStates.adminAwaitClientName, 
                                                                UserStates.adminAwaitDateTime, 
                                                                UserStates.adminAwaitDescription, 
                                                                UserStates.adminAwaitEventName,
                                                                UserStates.adminAwaitQuota,
                                                                UserStates.adminAwaitSelectToDel,
                                                                UserStates.adminAwaitType,
                                                                UserStates.adminAwaitPlatform,
                                                                UserStates.adminAwaitSelectToEdit,
                                                                UserStates.adminAwaitForwardMsg,
                                                                UserStates.adminAwaitEmpName,
                                                                UserStates.empAwaitSelectToView,
                                                                UserStates.adminAwaitSelectEmpToDel,
                                                                UserStates.adminSeekApplications,
                                                                UserStates.AdminAwaitRepeatSelect,
                                                                UserStates.AdminSelectInterval,
                                                                UserStates.adminAwaitSelectClassToEdit,
                                                                UserStates.adminAwaitSelectClassToDel,
                                                                UserStates.empAwaitSelectTable
                                                                ])
async def goBackAdmin(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(event_id='')
    await state.update_data(event_name='')
    await state.update_data(client_name='')
    await state.update_data(event_platform='')
    await state.update_data(event_quota='')
    await state.update_data(event_description='')
    await state.update_data(event_datetime='')
    await state.update_data(event_isPublic='')
    await state.update_data(admin_mode='reg')
    await state.set_state(UserStates.admin.state)
    await callback_query.message.answer("Добро пожаловать в админ-панель", reply_markup=AdminStartKeyboard.markup)


@dp.callback_query_handler(lambda c: c.data in ('confirm-event-field', 'select-interval-done'),
                            state=[UserStates.admin, 
                            UserStates.adminAwaitClientName, 
                            UserStates.adminAwaitDateTime, 
                            UserStates.adminAwaitDescription, 
                            UserStates.adminAwaitEventName,
                            UserStates.adminAwaitQuota,
                            UserStates.adminAwaitSelectToDel,
                            UserStates.adminAwaitType,
                            UserStates.adminAwaitPlatform,
                            UserStates.adminAwaitSelectToEdit,
                            UserStates.adminAwaitForwardMsg,
                            UserStates.adminAwaitEmpName,
                            UserStates.empAwaitSelectToView,
                            UserStates.adminAwaitSelectEmpToDel,
                            UserStates.adminSeekApplications,
                            UserStates.AdminAwaitRepeatSelect,
                            UserStates.AdminSelectInterval,
                            UserStates.adminAwaitSelectClassToEdit,
                            UserStates.adminAwaitSelectClassToDel
                            ])
async def confirmEventField(callback_query: types.CallbackQuery, state: FSMContext):
    eventData = await state.get_data()
    if eventData['admin_mode'] == 'reg':
        if eventData['isEvent']:
            if eventData['event_isPublic']:
                await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                                        reply_markup=AdminAddPublicKeyboard.markup)   
            else:
                await callback_query.message.edit_text(f"Карточка мероприятия:\n\nИмя клиента: {eventData['client_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nОписание мероприятия: {eventData['event_description']}\n\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                                        reply_markup=AdminAddPrivateKeyboard.markup)
        else:
            await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nВременные окна и дни недели: {serialize_intervals(eventData['class_intervals'])};{serialize_weekdays(eventData['class_weekdays'])}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nТип мероприятия: занятие", 
                                        reply_markup=AdminAddIntervalEvent.markup)

    elif eventData['admin_mode'] == 'edit':
        if eventData['isEvent']:
            if eventData['event_isPublic']:
                await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                                    reply_markup=AdminEditPublicKeyboard.markup)   
            else:
                await callback_query.message.edit_text(f"Карточка мероприятия:\n\nИмя клиента: {eventData['client_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nОписание мероприятия: {eventData['event_description']}\n\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                                    reply_markup=AdminEditPrivateKeyboard.markup)
        else:
            await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nВременные окна и дни недели: {serialize_intervals(eventData['class_intervals'])};{serialize_weekdays(eventData['class_weekdays'])}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nТип мероприятия: занятие", 
                                        reply_markup=AdminEditIntervalEvent.markup)

    await state.set_state(UserStates.admin.state)

@dp.callback_query_handler(text='confirm-event-reg', state=UserStates.admin)
async def confirmEventAdd(callback_query: types.CallbackQuery, state: FSMContext):
    eventData = await state.get_data()
    if not eventData['isEvent']:
        if not eventData['event_name'] or not eventData['event_platform'] or not eventData['event_quota'] or not eventData['event_description']:
            await callback_query.message.answer('Заполните все поля!', reply_markup=types.ReplyKeyboardRemove())
            return
        if eventData['admin_mode'] == 'reg':
            res_reg = register_class(db=session,
                                class_name=eventData['event_name'],
                                class_platform=eventData['event_platform'],
                                class_quota=eventData['event_quota'],
                                class_description=eventData['event_description'],
                                class_weekdays=serialize_weekdays(eventData['class_weekdays'], 1),
                                class_intervals=serialize_intervals(eventData['class_intervals'], 1))
            res_sched = await schedule_class(session=session, class_id=get_latest_class_record(session).id, scheduler=scheduler, initial=True)
        elif eventData['admin_mode'] == 'edit':
            await notify_clients_on_event_deletion(session=session, bot=bot, class_id=eventData['event_id'])
            res_del = delete_class(db=session, class_id=eventData['event_id'])
            
            res_edit = register_class(db=session,
                                  class_name=eventData['event_name'],
                                  class_platform=eventData['event_platform'],
                                  class_quota=eventData['event_quota'],
                                  class_description=eventData['event_description'],
                                  class_weekdays=serialize_weekdays(eventData['class_weekdays'], 1),
                                  class_intervals=serialize_intervals(eventData['class_intervals'], 1))
            scheduler.remove_job(f'{eventData["event_id"]}')
            res_reschedule = await schedule_class(session=session, class_id=get_latest_class_record(db=session).id, scheduler=scheduler, initial=True)

        await state.update_data(event_id='')
        await state.update_data(event_name='')
        await state.update_data(client_name='')
        await state.update_data(event_platform='')
        await state.update_data(event_quota='')
        await state.update_data(event_description='')
        await state.update_data(event_datetime='')
        await state.update_data(event_isPublic='')
        await state.update_data(admin_mode='reg')
        await state.update_data(isEvent=True)
        await state.update_data(class_weekdays=[0 for _ in range(7)])
        await state.update_data(class_intervals=[0 for _ in range(3)])

        match eventData['admin_mode']:
            case 'reg':
                if res_reg and res_sched:
                    await callback_query.message.answer('Мероприятие добавлено!', reply_markup=AdminStartKeyboard.markup)
                else:
                    logging.log(logging.ERROR, f'{res_reg} || {res_sched}')
                    await callback_query.message.answer('Что-то пошло не так.. Попробуйте еще раз', reply_markup=AdminStartKeyboard.markup)        
            case 'edit':
                if res_del and res_edit and res_reschedule:
                    await callback_query.message.answer('Мероприятие изменено!', reply_markup=AdminStartKeyboard.markup)
                else:
                    logging.log(logging.ERROR, f'{res_reg} || {res_sched}')
                    await callback_query.message.answer('Что-то пошло не так.. Попробуйте еще раз', reply_markup=AdminStartKeyboard.markup)        
        return

    if eventData['event_isPublic'] == True:
        if not eventData['event_name'] or not eventData['event_platform'] or not eventData['event_quota'] or not eventData['event_description'] or not eventData['event_datetime']:
            await callback_query.message.answer('Заполните все поля!', reply_markup=types.ReplyKeyboardRemove())
            return
    elif eventData['event_isPublic'] == False:
        if not eventData['client_name'] or not eventData['event_platform']:
            await callback_query.message.answer('Заполните все поля!', reply_markup=types.ReplyKeyboardRemove())
            return
    else:
        await callback_query.message.answer('Тебя здесь быть не должно..', reply_markup=types.ReplyKeyboardRemove())
        return
    if eventData['event_quota'] == '':
        eventData['event_quota'] = 0
    if eventData['admin_mode'] == 'reg':
        res = register_event(db=session, 
                            event_name=eventData['event_name'],
                            client_name=eventData['client_name'],
                            event_platform=eventData['event_platform'], 
                            event_quota=eventData['event_quota'], 
                            event_description=eventData['event_description'], 
                            event_datetime=datetime.strptime(eventData['event_datetime'], "%d.%m.%Y %H:%M"),
                            event_isPublic=eventData['event_isPublic']
                            )
        if eventData['event_isPublic'] == True:
            await notifier(bot, session, get_latest_event_record(session), storage)
    elif eventData['admin_mode'] == 'edit':
        res = edit_event(db=session, 
                        event_id=eventData['event_id'],
                        event_name=eventData['event_name'],
                        client_name=eventData['client_name'],
                        event_platform=eventData['event_platform'], 
                        event_quota=eventData['event_quota'], 
                        event_description=eventData['event_description'], 
                        event_datetime=datetime.strptime(eventData['event_datetime'], "%d.%m.%Y %H:%M"),
                        event_isPublic=eventData['event_isPublic']
                        )
    if res:
        await callback_query.message.answer(f'Мероприятие {"добавлено" if eventData["admin_mode"] == "reg" else "изменено"}!', reply_markup=AdminStartKeyboard.markup)
    else:
        await callback_query.message.answer('Что-то пошло не так.. Попробуйте еще раз', reply_markup=AdminStartKeyboard.markup)

    await state.update_data(event_id='')
    await state.update_data(event_name='')
    await state.update_data(client_name='')
    await state.update_data(event_platform='')
    await state.update_data(event_quota='')
    await state.update_data(event_description='')
    await state.update_data(event_datetime='')
    await state.update_data(event_isPublic='')
    await state.update_data(admin_mode='reg')
    await state.update_data(isEvent=True)
    await state.update_data(class_weekdays=[0 for _ in range(7)])
    await state.update_data(class_intervals=[0 for _ in range(3)])

@dp.callback_query_handler(text='select-event-type', state=UserStates.admin)
async def adminSelectEventType(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Выберите вид меропиятия:", reply_markup=AdminSelectTypeKeyboard.markup)


@dp.callback_query_handler(lambda c: re.fullmatch(r"add-(private|public)-event", c.data), state=[UserStates.admin,
                                                                                                 UserStates.empAwaitSelectToView])
async def adminRememberTypeChoice(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.admin)
    status = callback_query.data.split('-')[1]
    await state.update_data(event_isPublic=True if status == 'public' else False)
    eventData = await state.get_data()
    if eventData['admin_mode'] == 'reg':
        if eventData['isEvent']:
            if eventData['event_isPublic']:
                await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                                        reply_markup=AdminAddPublicKeyboard.markup)   
            else:
                await callback_query.message.edit_text(f"Карточка мероприятия:\n\nИмя клиента: {eventData['client_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nОписание мероприятия: {eventData['event_description']}\n\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                                        reply_markup=AdminAddPrivateKeyboard.markup)
        else:
            await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nВременные окна и дни недели: {eventData['class_intervals']};{eventData['class_weekdays']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                        reply_markup=AdminAddIntervalEvent.markup)
    elif eventData['admin_mode'] == 'edit':
        if eventData['isEvent']:
            if eventData['event_isPublic']:
                await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                                    reply_markup=AdminEditPublicKeyboard.markup)   
            else:
                await callback_query.message.edit_text(f"Карточка мероприятия:\n\nИмя клиента: {eventData['client_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nОписание мероприятия: {eventData['event_description']}\n\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                                    reply_markup=AdminEditPrivateKeyboard.markup)
        else:
            await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nВременные окна и дни недели: {eventData['class_intervals']};{eventData['class_weekdays']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                        reply_markup=AdminEditIntervalEvent.markup)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(lambda c: c.data in ('select-event-datetime', 'select-intervals-done', 'select-weekdays-done'), state=UserStates.admin)
async def adminSelectWhatToSelect(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text('Выберите вариант.', reply_markup=AdminSelectIntervalOrWeekdays.markup)

@dp.callback_query_handler(lambda c: c.data.startswith('select-interval'), state=UserStates.admin)
async def adminSelectIntervals(callback_query: types.CallbackQuery, state: FSMContext):
    # await state.set_state(UserStates.AdminSelectInterval.state)
    eventData = await state.get_data()
    if callback_query.data == 'select-intervals':
        # await state.update_data(class_intervals=[])
        await callback_query.message.edit_text('Выберите окна.', reply_markup=AdminSelectIntervals(eventData['class_intervals']).markup)
        return
    eventData['class_intervals'][int(callback_query.data[-1])] = not eventData['class_intervals'][int(callback_query.data[-1])]
    new_intervals = eventData['class_intervals']
    await state.update_data(class_intervals=new_intervals)
    await callback_query.message.edit_text('Выберите окна.', reply_markup=AdminSelectIntervals(new_intervals).markup)

@dp.callback_query_handler(lambda c: c.data.startswith('select-weekday'), state=UserStates.admin)
async def adminSelectWeekdays(callback_query: types.CallbackQuery, state: FSMContext):
    eventData = await state.get_data()
    if callback_query.data == 'select-weekdays':
        # await state.update_data(class_intervals=[])
        await callback_query.message.edit_text('Выберите дни недели.', reply_markup=AdminSelectWeekdays(eventData['class_weekdays']).markup)
        return
    eventData['class_weekdays'][int(callback_query.data[-1])] = not eventData['class_weekdays'][int(callback_query.data[-1])]
    new_weekdays = eventData['class_weekdays']
    await state.update_data(class_weekdays=new_weekdays)
    await callback_query.message.edit_text('Выберите дни недели.', reply_markup=AdminSelectWeekdays(new_weekdays).markup)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(lambda c: c.data == 'enter-event-name', state=UserStates.admin)
async def adminEnterEventName(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Введите название мероприятия", reply_markup=AdminConfirmEventDataKeyboard.markup)
    await state.set_state(UserStates.adminAwaitEventName.state)


@dp.message_handler(state=UserStates.adminAwaitEventName)
async def adminAwaitEventName(message: types.Message, state: FSMContext):
    await state.update_data(event_name=message.text)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(lambda c: c.data == 'enter-client-name', state=UserStates.admin)
async def adminEnterClientName(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Введите имя клиента", reply_markup=AdminConfirmEventDataKeyboard.markup)
    await state.set_state(UserStates.adminAwaitClientName.state)


@dp.message_handler(state=UserStates.adminAwaitClientName)
async def adminAwaitClientName(message: types.Message, state: FSMContext):
    await state.update_data(client_name=message.text)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(lambda c: c.data == 'enter-event-platform', state=UserStates.admin)
async def adminEnterPlatform(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Выберите платформу проведения мероприятия: ", reply_markup=SelectPlatform.markup)
    await state.set_state(UserStates.adminAwaitPlatform.state)


@dp.callback_query_handler(lambda c: c.data.startswith('select-'), state=UserStates.adminAwaitPlatform)
async def adminAwaitPlatform(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(event_platform=callback_query.data.split('-')[1])
    await state.set_state(UserStates.admin.state)
    eventData = await state.get_data()
    if eventData['admin_mode'] == 'reg':
        if eventData['isEvent']:
            if eventData['event_isPublic']:
                await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                                        reply_markup=AdminAddPublicKeyboard.markup)   
            else:
                await callback_query.message.edit_text(f"Карточка мероприятия:\n\nИмя клиента: {eventData['client_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nОписание мероприятия: {eventData['event_description']}\n\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                                        reply_markup=AdminAddPrivateKeyboard.markup)
        else:
            await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nВременные окна и дни недели: {serialize_intervals(eventData['class_intervals'])};{serialize_weekdays(eventData['class_weekdays'])}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                        reply_markup=AdminAddIntervalEvent.markup)

    elif eventData['admin_mode'] == 'edit':
        if eventData['isEvent']:
            if eventData['event_isPublic']:
                await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                                    reply_markup=AdminEditPublicKeyboard.markup)   
            else:
                await callback_query.message.edit_text(f"Карточка мероприятия:\n\nИмя клиента: {eventData['client_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nОписание мероприятия: {eventData['event_description']}\n\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                                   reply_markup=AdminEditPrivateKeyboard.markup)
        else:
            await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nВременные окна и дни недели: {serialize_intervals(eventData['class_intervals'])};{serialize_weekdays(eventData['class_weekdays'])}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                        reply_markup=AdminEditIntervalEvent.markup)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(lambda c: c.data == 'enter-event-quota', state=UserStates.admin)
async def adminEnterQuota(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Введите количество гостей", reply_markup=AdminConfirmEventDataKeyboard.markup)
    await callback_query.message.answer('Пожалуйста, введите числовое значение.', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(UserStates.adminAwaitQuota.state)


@dp.message_handler(state=UserStates.adminAwaitQuota)
async def adminAwaitQuota(message: types.Message, state: FSMContext):
    if not message.text.isnumeric():
        await message.answer('Введите числовое значение.')
        return
    await state.update_data(event_quota=message.text)

        
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(lambda c: c.data == 'enter-event-description', state=UserStates.admin)
async def adminEnterDescription(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Введите описание мероприятия", reply_markup=AdminConfirmEventDataKeyboard.markup)
    await state.set_state(UserStates.adminAwaitDescription.state)


@dp.message_handler(state=UserStates.adminAwaitDescription)
async def adminAwaitDescription(message: types.Message, state: FSMContext):
    await state.update_data(event_description=message.text)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(lambda c: c.data == 'enter-event-datetime', state=UserStates.admin)
async def adminEnterDatetime(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Введите дату и время проведения мероприятия в формате: \"дд.мм.гггг чч:мм\".\n\nПример: 20.01.1976 13:05", reply_markup=AdminConfirmEventDataKeyboard.markup)
    await state.set_state(UserStates.adminAwaitDateTime.state)


@dp.message_handler(state=UserStates.adminAwaitDateTime)
async def adminAwaitDatetime(message: types.Message, state: FSMContext):
    if not re.fullmatch(r'([0-9]{2}.[0-9]{2}.[0-9]{4}) ([0-9]{2}:[0-9]{2})', message.text):
        await message.reply("Введите дату и время проведения мероприятия в формате: \"дд.мм.гггг чч:мм\".\n\nПример: 20.01.1976 13:05", reply_markup=AdminConfirmEventDataKeyboard.markup)
    await state.update_data(event_datetime=message.text)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(text='select-event-repeat', state=UserStates.admin)
async def adminSelectRepeat(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Это занятие или мероприятие?", reply_markup=AdminSelectEventRepeat.markup)
    await state.set_state(UserStates.AdminAwaitRepeatSelect.state)

@dp.callback_query_handler(text='is-event', state=UserStates.AdminAwaitRepeatSelect)
async def adminSelectedIsEvent(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.admin.state)
    await state.update_data(isEvent=True)
    await callback_query.message.edit_text("Выберите вид меропиятия:", reply_markup=AdminSelectTypeKeyboard.markup)
    # await callback_query.message.edit_text('СЮДА КАРТОЧКУ')

@dp.callback_query_handler(text='is-class', state=UserStates.AdminAwaitRepeatSelect)
async def adminSelectedNotEvent(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.admin.state)
    await state.update_data(event_isPublic=True)
    await state.update_data(isEvent=False)
    eventData = await state.get_data()
    await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nВременные окна и дни недели: {serialize_intervals(eventData['class_intervals'])};{serialize_weekdays(eventData['class_weekdays'])}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                reply_markup=AdminAddIntervalEvent.markup)

# @dp.callback_query_handler(lambda c: c.data == 'select-event-type', state=UserStates.admin)
# async def adminSelectType(callback_qeury: types.CallbackQuery, state: FSMContext):
#     await callback_qeury.message.edit_text("Выберите вид мероприятия:", reply_markup=SelectType.markup)
#     await state.set_state(UserStates.adminAwaitType.state)


# @dp.callback_query_handler(lambda c: c.data.startswith('select-'), state=UserStates.adminAwaitType)
# async def adminAwaitType(callback_query: types.CallbackQuery, state: FSMContext):
#     await state.update_data(event_isPublic=event_reverseIsPublic[callback_query.data.split('-')[1]])
#     await state.set_state(UserStates.admin.state)
#     eventData = await state.get_data()
#     if eventData['admin_mode'] == 'reg':
#         await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nИмя клиента: {eventData['client_name']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
#                                                reply_markup=AdminAddKeyboard.markup)
#     elif eventData['admin_mode'] == 'edit':
#         await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nИмя клиента: {eventData['client_name']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
#                                                reply_markup=AdminEditKeyboard.markup)       

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(text='del-event', state=UserStates.admin)
async def adminDeleteEvent(callback_query: types.CallbackQuery, state: FSMContext):
    event_dates = [x.date.strftime("%d.%m.%Y") for x in get_all_events(session)]
    await callback_query.message.edit_text('Выберите дату мероприятия:', reply_markup=ParseDatesKeyboard(event_dates).markup)
    await state.set_state(UserStates.adminAwaitSelectToDel.state)

@dp.callback_query_handler(lambda c: re.fullmatch(r"day:[0-9]{2}-mon:[0-9]{2}-year:[0-9]{4}", c.data), state=UserStates.adminAwaitSelectToDel)
async def adminSelectPlatform(callback_query: types.CallbackQuery, state: FSMContext):
    eventSearchDate = datetime.strptime(f"{callback_query.data[19:]}:{callback_query.data[11:13]}:{callback_query.data[4:6]}", "%Y:%m:%d").date()
    await state.update_data(eventSearchDate=eventSearchDate)
    await callback_query.message.edit_text("Выберите филиал:", reply_markup=SearchSelectPlatform('adm').markup)


@dp.callback_query_handler(lambda c: c.data.startswith('select-'), state=UserStates.adminAwaitSelectToDel)
async def adminSelectToDel(callback_query: types.CallbackQuery, state: FSMContext):
    eventData = await state.get_data()
    event_date = eventData['eventSearchDate']
    event_platform = callback_query.data.split('-')[1]
    events = [[x.id, x.name, x.client_name, x.isPublic, x.time.strftime("%H:%M")] for x in get_events_by_date_and_platform(session, event_date, event_platform)]
    await callback_query.message.edit_text("Выберите мероприятие:", reply_markup=ParseEventsByDateKeyboard(events).markup)

@dp.callback_query_handler(lambda c: re.fullmatch(r"id:[0-9]{1,}-time:[0-9]{2}:[0-9]{2}", c.data), state=UserStates.adminAwaitSelectToDel)
async def adminSelectedEventToDel(callback_query: types.CallbackQuery, state: FSMContext):
    event = get_event_by_id(db=session, event_id=int(callback_query.data[callback_query.data.index(':')+1:callback_query.data.index('-')]))
    if event.isPublic:
        await callback_query.message.edit_text(f"Вы уверены, что хотите удалить это мероприятие?:\n\nНазвание мероприятия: {event.name}\nДата и время проведения мероприятия: {date.strftime(event.date, '%d.%m.%Y')} {time.strftime(event.time, '%H:%M')}\nПлощадка проведения: {platforms[event.platform]}\nКоличество гостей: {event.quota}\nОписание мероприятия: {event.description}\nТип мероприятия: {event_isPublic[event.isPublic]}", 
                                                reply_markup=AdminConfirmDeleteEvent(event.id).markup)
    else:
        await callback_query.message.edit_text(f"Вы уверены, что хотите удалить это мероприятие?\n\nИмя клиента: {event.client_name}\nДата и время проведения мероприятия: {date.strftime(event.date, '%d.%m.%Y')} {time.strftime(event.time, '%H:%M')}\nПлощадка проведения: {platforms[event.platform]}\nОписание мероприятия: {event.description}\n\nТип мероприятия: {event_isPublic[event.isPublic]}", 
                                                reply_markup=AdminConfirmDeleteEvent(event.id).markup)

# @dp.callback_query_handler(lambda c: re.fullmatch(r"id:[0-9]{1,}-time:[0-9]{2}:[0-9]{2}", c.data), state=UserStates.adminAwaitSelectToDel)
@dp.callback_query_handler(lambda c: c.data.startswith('del-event-'), state=UserStates.adminAwaitSelectToDel)
async def adminSelectEventToDel(callback_query: types.CallbackQuery, state: FSMContext):
    await notify_clients_on_event_deletion(session=session, bot=bot, event_id=int(callback_query.data[10:]))
    if delete_event(session, int(callback_query.data[10:])):
        await callback_query.message.answer('Событие удалено.', reply_markup=AdminStartKeyboard.markup)
        await state.set_state(UserStates.admin.state)
    else:
        await callback_query.message.answer('Что-то пошло не так.. Попробуйте еще раз.', reply_markup=AdminStartKeyboard.markup)
        await state.set_state(UserStates.admin.state)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(text='edit-event', state=UserStates.admin)
async def adminEditEvent(callback_query: types.CallbackQuery, state: FSMContext):
    event_dates = [x.date.strftime("%d.%m.%Y") for x in get_all_events(session)]
    await callback_query.message.edit_text('Выберите дату мероприятия:', reply_markup=ParseDatesKeyboard(event_dates).markup)
    await state.set_state(UserStates.adminAwaitSelectToEdit.state)

@dp.callback_query_handler(text="del-class", state=UserStates.admin)
async def selectClassToDel(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Выберите занятие:", reply_markup=ParseClassesKeyboard(get_all_classes(session)).markup)
    await state.set_state(UserStates.adminAwaitSelectClassToDel.state)

@dp.callback_query_handler(lambda c: c.data.startswith('select-class-'), state=UserStates.adminAwaitSelectClassToDel)
async def classToDelSelected(callback_query: types.CallbackQuery, state: FSMContext):
    class_to_display = get_class_by_id(db=session,
                                       class_id=int(callback_query.data[13:]))
    await state.update_data(event_id=class_to_display.id)
    await state.update_data(event_name=class_to_display.name)
    await state.update_data(event_platform=class_to_display.platform)
    await state.update_data(event_quota=class_to_display.quota)
    await state.update_data(event_description=class_to_display.description)
    await state.update_data(class_weekdays=[int(x) for x in class_to_display.weekdays])
    await state.update_data(class_intervals=[int(x) for x in class_to_display.intervals])
    await state.update_data(admin_mode='edit')
    await state.update_data(isEvent=False)
    eventData = await state.get_data()
    await callback_query.message.edit_text(f"Уверены, что хотите удалить это мероприятие?\n\nНазвание мероприятия: {eventData['event_name']}\nВременные окна и дни недели: {serialize_intervals(eventData['class_intervals'])};{serialize_weekdays(eventData['class_weekdays'])}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nТип мероприятия: занятие", 
                                        reply_markup=AdminConfirmDeleteClass(int(callback_query.data[13:])).markup)

@dp.callback_query_handler(lambda c: c.data.startswith('del-class-'), state=UserStates.adminAwaitSelectClassToDel)
async def confirmedClassDelete(callback_query: types.CallbackQuery, state: FSMContext):
    await notify_clients_on_event_deletion(session=session, bot=bot, class_id=int(callback_query.data[10:]))
    if delete_class(db=session, class_id=int(callback_query.data[10:])):
        await callback_query.message.edit_text('Событие удалено.', reply_markup=AdminStartKeyboard.markup)
    else:
        await callback_query.message.edit_text('Что-то пошло не так.. Попробуйте еще раз.', reply_markup=AdminStartKeyboard.markup)
    await state.set_state(UserStates.admin.state)

@dp.callback_query_handler(text='edit-class', state=UserStates.admin)
async def selectClassToEdit(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text('Выберите занятие:', reply_markup=ParseClassesKeyboard(get_all_classes(session)).markup)
    await state.set_state(UserStates.adminAwaitSelectClassToEdit.state)

@dp.callback_query_handler(lambda c: c.data.startswith('select-class-'), state=UserStates.adminAwaitSelectClassToEdit)
async def classToEditSelected(callback_query: types.CallbackQuery, state: FSMContext):
    class_to_display = get_class_by_id(db=session,
                                       class_id=int(callback_query.data.split('-class-')[1]))
    await state.update_data(event_id=class_to_display.id)
    await state.update_data(event_name=class_to_display.name)
    await state.update_data(event_platform=class_to_display.platform)
    await state.update_data(event_quota=class_to_display.quota)
    await state.update_data(event_description=class_to_display.description)
    await state.update_data(class_weekdays=[int(x) for x in class_to_display.weekdays])
    await state.update_data(class_intervals=[int(x) for x in class_to_display.intervals])
    await state.update_data(admin_mode='edit')
    await state.update_data(isEvent=False)
    eventData = await state.get_data()
    await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nВременные окна и дни недели: {serialize_intervals(eventData['class_intervals'])};{serialize_weekdays(eventData['class_weekdays'])}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nТип мероприятия: занятие", 
                                        reply_markup=AdminEditIntervalEvent.markup)
    await state.set_state(UserStates.admin.state)

@dp.callback_query_handler(lambda c: re.fullmatch(r"day:[0-9]{2}-mon:[0-9]{2}-year:[0-9]{4}", c.data), state=UserStates.adminAwaitSelectToEdit)
async def adminSelectPlatform(callback_query: types.CallbackQuery, state: FSMContext):
    eventSearchDate = datetime.strptime(f"{callback_query.data[19:]}:{callback_query.data[11:13]}:{callback_query.data[4:6]}", "%Y:%m:%d").date()
    await state.update_data(eventSearchDate=eventSearchDate)
    await callback_query.message.edit_text("Выберите филиал:", reply_markup=SearchSelectPlatform('adm').markup)

@dp.callback_query_handler(lambda c: c.data.startswith('select-'), state=UserStates.adminAwaitSelectToEdit)
async def adminSelectToEdit(callback_query: types.CallbackQuery, state: FSMContext):
    eventData = await state.get_data()
    event_date = eventData['eventSearchDate']
    event_platform = callback_query.data.split('-')[1]
    events = [[x.id, x.name, x.client_name, x.isPublic, x.time.strftime("%H:%M")] for x in get_events_by_date_and_platform(session, event_date, event_platform)]
    await callback_query.message.edit_text("Выберите мероприятие:", reply_markup=ParseEventsByDateKeyboard(events).markup)

@dp.callback_query_handler(lambda c: re.fullmatch(r"id:[0-9]{1,}-time:[0-9]{2}:[0-9]{2}", c.data), state=UserStates.adminAwaitSelectToEdit)
async def adminSelectEventToEdit(callback_query: types.CallbackQuery, state: FSMContext):
    event = get_event_by_id(session, int(callback_query.data[callback_query.data.index(':')+1:callback_query.data.index('-')]))
    await state.update_data(event_id=event.id)
    await state.update_data(event_name=event.name)
    await state.update_data(client_name=event.client_name)
    await state.update_data(event_platform=event.platform)
    await state.update_data(event_quota=event.quota)
    await state.update_data(event_description=event.description)
    await state.update_data(event_datetime=f"{date.strftime(event.date, '%d.%m.%Y')} {time.strftime(event.time, '%H:%M')}")
    await state.update_data(event_isPublic=event.isPublic)
    await state.update_data(admin_mode='edit')
    eventData = await state.get_data()
    # await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nИмя клиента: {eventData['client_name']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
    #                                        reply_markup=AdminAddKeyboard.markup)

    if eventData['event_isPublic']:
        await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                                reply_markup=AdminEditPublicKeyboard.markup)   
    else:
        await callback_query.message.edit_text(f"Карточка мероприятия:\n\nИмя клиента: {eventData['client_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nОписание мероприятия: {eventData['event_description']}\n\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                                reply_markup=AdminEditPrivateKeyboard.markup)

    await state.set_state(UserStates.admin.state)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



@dp.callback_query_handler(text='control-emps', state=UserStates.admin)
async def adminControlEmps(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text('Выберите действие', reply_markup=AdminControlEmpsKeyboard.markup)


@dp.callback_query_handler(text='add-emp', state=UserStates.admin)
async def adminAddEmp(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text('Перешлите любое сообщение от пользователя, чтобы дать ему доступ к мероприятиям.', reply_markup=AdminCancel.markup)
    await state.set_state(UserStates.adminAwaitForwardMsg.state)


@dp.message_handler(state=UserStates.adminAwaitForwardMsg)
async def adminGetId(message: types.Message, state: FSMContext):
    if message.is_forward():
        await state.update_data(emp_id=str(message.forward_from.id))
        await message.answer("Как зовут сотрудника?", reply_markup=AdminConfirmEmpAdd.markup)
        await state.set_state(UserStates.adminAwaitEmpName.state)
    else:
        await message.answer('Пожалуйста, перешлите мне сообщение от пользователя.')


@dp.message_handler(state=UserStates.adminAwaitEmpName)
async def adminAwaitEmpName(message: types.Message, state: FSMContext):
    await state.update_data(emp_name=message.text)


@dp.callback_query_handler(text='confirm-emp-reg', state=UserStates.adminAwaitEmpName)
async def confirmEmpName(callback_query: types.CallbackQuery, state: FSMContext):
    empData = await state.get_data()
    if not empData['emp_name']:
        await callback_query.message.answer('Введите имя сотрудника')
    elif register_user(session, empData['emp_id'], empData['emp_name'], '', 'emp'):
        await callback_query.message.answer("Сотрудник добавлен!", reply_markup=AdminStartKeyboard.markup)
        await state.update_data(emp_id='')
        await state.update_data(emp_name='')
        await state.set_state(UserStates.admin.state)
    else:
        await callback_query.message.answer("Что-то пошло не так.. Попробуйте еще раз.", reply_markup=AdminStartKeyboard.markup)
        await state.update_data(emp_id='')
        await state.update_data(emp_name='')
        await state.set_state(UserStates.admin.state)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(text='del-emp', state=UserStates.admin)
async def adminSelectEmpToDel(callback_query: types.CallbackQuery, state: FSMContext):
    emps = get_all_emps(session)
    await callback_query.message.edit_text('Выберите сотрудника, которого хотите удалить', reply_markup=AdminSelectEmpToDel(emps).markup)
    await state.set_state(UserStates.adminAwaitSelectEmpToDel.state)

@dp.callback_query_handler(lambda c: c.data.startswith('select-'), state=UserStates.adminAwaitSelectEmpToDel)
async def adminSelectedEmpToDel(callback_query: types.CallbackQuery, state: FSMContext):
    emp_id = callback_query.data.split('-')[1]
    if delete_employee(session, emp_id):
        await callback_query.message.edit_text('Сотрудник удален.', reply_markup=AdminStartKeyboard.markup)
        await state.set_state(UserStates.admin)
    else:
        await callback_query.message.edit_text('Что-то пошло не так.. Попробуйте еще раз.', reply_markup=AdminStartKeyboard.markup)
        await state.set_state(UserStates.admin)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(text='emp-cancel', state=[UserStates.employee,
                                                     UserStates.empAwaitSelectToView,
                                                     UserStates.empAwaitSelectTable])
async def goBackEmp(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.employee.state)
    await callback_query.message.answer("Добро пожаловать в панель сотрудника", reply_markup=EmpStartKeyboard.markup)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(text="all-events", state=[UserStates.employee, UserStates.admin])
async def empViewAllEvents(callback_query: types.CallbackQuery, state: FSMContext):
    event_dates = [x.date.strftime("%d.%m.%Y") for x in get_all_events(session)]
    usrData = await state.get_data()
    if usrData['usr_role'] == 'emp':
        await callback_query.message.edit_text('Выберите дату мероприятия:', reply_markup=ParseDatesKeyboard(event_dates, 'emp').markup)
    elif usrData['usr_role'] == 'adm':
        await callback_query.message.edit_text('Выберите дату мероприятия:', reply_markup=ParseDatesKeyboard(event_dates, 'adm').markup)
    else:
        await callback_query.message.edit_text('Ты кто..', reply_markup=types.ReplyKeyboardMarkup())
    await state.set_state(UserStates.empAwaitSelectToView.state)


@dp.callback_query_handler(lambda c: re.fullmatch(r"day:[0-9]{2}-mon:[0-9]{2}-year:[0-9]{4}", c.data), state=UserStates.empAwaitSelectToView)
async def empSelectPlatform(callback_query: types.CallbackQuery, state: FSMContext):
    eventSearchDate = datetime.strptime(f"{callback_query.data[19:]}:{callback_query.data[11:13]}:{callback_query.data[4:6]}", "%Y:%m:%d").date()
    await state.update_data(eventSearchDate=eventSearchDate)
    usrData = await state.get_data()
    if usrData['usr_role'] == 'emp':
        await callback_query.message.edit_text("Выберите филиал:", reply_markup=SearchSelectPlatform('emp').markup)
    elif usrData['usr_role'] == 'adm':
        await callback_query.message.edit_text("Выберите филиал:", reply_markup=SearchSelectPlatform('adm').markup)


@dp.callback_query_handler(lambda c: c.data.startswith('select-'), state=UserStates.empAwaitSelectToView)
async def empSelectToView(callback_query: types.CallbackQuery, state: FSMContext):
    eventData = await state.get_data()
    event_platform = callback_query.data.split('-')[1]
    event_date = eventData['eventSearchDate']
    events = [[x.id, x.name, x.client_name, x.isPublic, x.time.strftime("%H:%M")] for x in get_events_by_date_and_platform(session, event_date, event_platform)]
    usrData = await state.get_data()
    if usrData['usr_role'] == 'emp':
        await callback_query.message.edit_text("Выберите мероприятие:", reply_markup=ParseEventsByDateKeyboard(events, 'emp').markup)
    elif usrData['usr_role'] == 'adm':
        await callback_query.message.edit_text("Выберите мероприятие:", reply_markup=ParseEventsByDateKeyboard(events, 'adm').markup)
    else:
        await callback_query.message.edit_text("Ты кто..", reply_markup=types.ReplyKeyboardRemove())


@dp.callback_query_handler(lambda c: c.data.startswith('weekly-calendar:'), state=[UserStates.employee,
                                                                                   UserStates.admin,
                                                                                   UserStates.empAwaitSelectTable])
async def showWeeklyCalendar(callback_query: types.CallbackQuery, state: FSMContext):
    shift = int(callback_query.data[callback_query.data.index(':')+1:])
    order = ['voyk', 'musm', 'verh', 'zhiv']
    week_data = defaultdict(lambda: defaultdict())
    week_dates = get_week(date.today(), weeksdelta=shift)
    week_events = get_events_by_date_range(session, week_dates)
    for day in week_dates:
        for platform in order:
            week_data[day][platform] = 0
    for event in week_events:
        if not event.isPublic:
            week_data[event.date][event.platform] += 1
    usrData = await state.get_data()
    await callback_query.message.edit_text("Выберите слот в таблице", reply_markup=WeekTable(week_data=week_data, shift_weeks=int(callback_query.data.split(':')[1]), role=usrData['usr_role']).markup)
    await state.set_state(UserStates.empAwaitSelectTable.state)


@dp.callback_query_handler(lambda c: re.fullmatch(r"(date:([0-9]{2}.[0-9]{2}.[0-9]{4}))-(platform:(voyk|verh|musm|zhiv))", c.data), state=UserStates.empAwaitSelectTable)
async def showEventOnDateTable(callback_query: types.CallbackQuery, state: FSMContext):
    callback_data = re.search(r"(date:([0-9]{2}.[0-9]{2}.[0-9]{4}))-(platform:(voyk|verh|musm|zhiv))", callback_query.data, re.IGNORECASE)
    event_platform, event_date = callback_data.group(4), callback_data.group(2)
    events = [[x.id, x.name, x.client_name, x.isPublic, x.time.strftime("%H:%M")] for x in get_events_by_date_and_platform(session, datetime.strptime(event_date, '%d.%m.%Y').date(), event_platform)]
    usrData = await state.get_data()
    if usrData['usr_role'] == 'emp':
        await callback_query.message.edit_text("Выберите мероприятие:", reply_markup=ParseEventsByDateTableKeyboard(events, 'emp').markup)
        await state.set_state(UserStates.empAwaitSelectToView.state)
    elif usrData['usr_role'] == 'adm':
        await callback_query.message.edit_text("Выберите мероприятие:", reply_markup=ParseEventsByDateTableKeyboard(events, 'adm').markup)
        await state.update_data(event_isPublic=False)
        await state.update_data(event_platform=event_platform)
        await state.set_state(UserStates.empAwaitSelectToView.state)
    else:
        await callback_query.message.edit_text("Ты кто..", reply_markup=types.ReplyKeyboardRemove())



@dp.callback_query_handler(lambda c: re.fullmatch(r"id:[0-9]{1,}-time:[0-9]{2}:[0-9]{2}", c.data), state=UserStates.empAwaitSelectToView)
async def empSelectEventToView(callback_query: types.CallbackQuery, state: FSMContext):
    event = get_event_by_id(session, int(callback_query.data[callback_query.data.index(':')+1:callback_query.data.index('-')]))
    await state.update_data(event_id=event.id)
    await state.update_data(event_name=event.name)
    await state.update_data(client_name=event.client_name)
    await state.update_data(event_platform=event.platform)
    await state.update_data(event_quota=event.quota)
    await state.update_data(event_description=event.description)
    await state.update_data(event_datetime=f"{date.strftime(event.date, '%d.%m.%Y')} {time.strftime(event.time, '%H:%M')}")
    await state.update_data(event_isPublic=event.isPublic)
    eventData = await state.get_data()
    if eventData['usr_role'] == 'emp':
        if eventData['event_isPublic']:
            await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                                    reply_markup=EmpCancel.markup)
        else:
            await callback_query.message.edit_text(f"Карточка мероприятия:\n\nИмя клиента: {eventData['client_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nОписание мероприятия: {eventData['event_description']}\n\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                                    reply_markup=EmpCancel.markup)
        await state.set_state(UserStates.employee.state)
    elif eventData['usr_role'] == 'adm':
        if eventData['event_isPublic']:
            await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nКоличество гостей: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                                    reply_markup=AdminView.markup)
        else:
            await callback_query.message.edit_text(f"Карточка мероприятия:\n\nИмя клиента: {eventData['client_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nОписание мероприятия: {eventData['event_description']}\n\nТип мероприятия: {event_isPublic[eventData['event_isPublic']]}", 
                                                    reply_markup=AdminView.markup)
        await state.set_state(UserStates.admin.state)
    else:
        await callback_query.message.edit_text('Ты кто..', reply_markup=types.ReplyKeyboardRemove())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(text='admin-seek-applications', state=UserStates.admin)
async def adminSeekApplications(callback_query: types.CallbackQuery, state: FSMContext):
    eventData = await state.get_data()
    applications = get_applications_by_event(session, eventData['event_id'])
    await callback_query.message.edit_text('Заявки на это мероприятие:', reply_markup=AdminViewApplications(applications).markup)
    await state.set_state(UserStates.adminSeekApplications.state)


@dp.callback_query_handler(lambda c: re.fullmatch(r"(id:)([0-9]{1,})(-client_name:)((\S|\s){1,})", c.data), state=UserStates.adminSeekApplications)
async def adminViewApplications(callback_query: types.CallbackQuery, state: FSMContext):
    event = get_application_by_id(session, callback_query.data.split('-')[0].split(':')[1])
    await state.update_data(usr_name=callback_query.data.split('-')[1].split(':')[1])
    await state.update_data(children_names=event.children_name)
    await state.update_data(usr_phone=event.phone_number)
    await state.update_data(children_amount=event.guests_amount)
    await state.update_data(confirmed=event.confirmed)
    eventData = await state.get_data()
    await callback_query.message.edit_text(f'Карточка заявки:\n\nИмя клиента: {eventData["usr_name"]}\nИмена детей: {eventData["children_names"]}\nНомер телефона: {eventData["usr_phone"]}\n\nСтатус: {"Подтверждена" if eventData["confirmed"] else "Не подтверждена"}',
                                           reply_markup=AdminCancel.markup)
    
    

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(text='subscriptions', state=UserStates.client)
async def subscriptions(callback_query: types.CallbackQuery):
    subscriptions = get_subscriptions_by_id(session, str(callback_query.from_user.id))
    await callback_query.message.edit_text("Нажмите на филиал, чтобы подписаться/отписаться на рассылку мероприятий.", reply_markup=SubscriptionsKeyboard(subscriptions).markup)

@dp.callback_query_handler(lambda c: c.data.startswith('sub-'), state=UserStates.client)
async def subscribe(callback_query: types.CallbackQuery, state: FSMContext):
    if toggle_subscription(session, str(callback_query.from_user.id), callback_query.data.split('-')[1]):
        subscriptions = get_subscriptions_by_id(session, str(callback_query.from_user.id))
        await callback_query.message.edit_text('Нажмите на филиал, чтобы подписаться/отписаться на рассылку мероприятий.', reply_markup=SubscriptionsKeyboard(subscriptions).markup)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(text='client-cancel', state=[UserStates.client,
                                                        UserStates.clientAwaitSelectToView])
async def clientGoBack(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.client.state)
    await state.set_state(UserStates.client.state)
    await state.update_data(usr_role='usr')
    await callback_query.message.answer("Здравствуйте! Чем я могу помочь?", reply_markup=StartKeyboard.markup)


@dp.callback_query_handler(text="upcoming-events", state=UserStates.client)
async def clientViewAllEvents(callback_query: types.CallbackQuery, state: FSMContext):
    event_dates = [x.date.strftime("%d.%m.%Y") for x in get_all_public_events(session)]
    await callback_query.message.edit_text('Выберите дату мероприятия:', reply_markup=ParseDatesKeyboard(event_dates, 'usr').markup)
    await state.set_state(UserStates.clientAwaitSelectToView.state)


@dp.callback_query_handler(lambda c: re.fullmatch(r"day:[0-9]{2}-mon:[0-9]{2}-year:[0-9]{4}", c.data), state=UserStates.clientAwaitSelectToView)
async def clientSelectPlatform(callback_query: types.CallbackQuery, state: FSMContext):
    eventSearchDate = datetime.strptime(f"{callback_query.data[19:]}:{callback_query.data[11:13]}:{callback_query.data[4:6]}", "%Y:%m:%d").date()
    await state.update_data(eventSearchDate=eventSearchDate)
    await callback_query.message.edit_text("Выберите филиал:", reply_markup=SearchSelectPlatform('usr').markup)



@dp.callback_query_handler(lambda c: c.data.startswith('select-'), state=UserStates.clientAwaitSelectToView)
async def clientSelectToView(callback_query: types.CallbackQuery, state: FSMContext):
    eventData = await state.get_data()
    event_platform = callback_query.data.split('-')[1]
    event_date = eventData['eventSearchDate']
    events = [[x.id, x.name, x.client_name, x.isPublic, x.time.strftime("%H:%M")] for x in get_public_events_by_date_and_platform(session, event_date, event_platform)]
    await callback_query.message.edit_text("Выберите мероприятие:", reply_markup=ParseEventsByDateKeyboard(events, 'usr').markup)

@dp.callback_query_handler(lambda c: re.fullmatch(r"id:[0-9]{1,}-time:[0-9]{2}:[0-9]{2}", c.data), state=UserStates.clientAwaitSelectToView)
async def clientSelectEventToView(callback_query: types.CallbackQuery, state: FSMContext):
    event = get_event_by_id(session, int(callback_query.data[callback_query.data.index(':')+1:callback_query.data.index('-')]))
    await state.update_data(event_id=event.id)
    await state.update_data(event_name=event.name)
    await state.update_data(client_name=event.client_name)
    await state.update_data(event_platform=event.platform)
    await state.update_data(event_quota=get_vacant_amount_by_event_id(session, event.id))
    await state.update_data(event_description=event.description)
    await state.update_data(event_datetime=f"{date.strftime(event.date, '%d.%m.%Y')} {time.strftime(event.time, '%H:%M')}")
    # await state.update_data(event_isPublic=event.isPublic)
    eventData = await state.get_data()

    await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nСвободных мест: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}", 
                                            reply_markup=SubscribeKeyboard(event.id).markup)
    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(lambda c: c.data.startswith('apply-'), state=[UserStates.clientAwaitSelectToView,
                                                UserStates.clientAwaitApplicationChildrenName,
                                                UserStates.clientAwaitApplicationName,
                                                UserStates.clientAwaitApplicationPhone,
                                                UserStates.clientAwaitApplicationGuestsAmount,
                                                UserStates.client])
async def clientAppliedToAnEvent(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(event_id=int(callback_query.data.split('-')[1]))
    eventData = await state.get_data()
    await state.set_state(UserStates.clientAwaitSelectToView.state)
    await callback_query.message.answer(f'Ваша заявка:\n\nИмя контактного лица: {eventData["usr_name"]}\n{"Имя и фамилия ребенка" if eventData["guests_amount"] == 1 else "Имена детей"}: {eventData["children_names"]}\nКонтактный номер телефона: {eventData["usr_phone"]}\nКоличество детей: {eventData["guests_amount"]}',
                                        reply_markup=FillApplicationKeyboard.markup)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(text='client-fill-name', state=UserStates.clientAwaitSelectToView)
async def clientAwaitApplicationName(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer('Введите имя контактного лица', reply_markup=ClientCancel.markup)
    await state.set_state(UserStates.clientAwaitApplicationName.state)

@dp.message_handler(state=UserStates.clientAwaitApplicationName)
async def clientConfirmApplicationName(message: types.Message, state: FSMContext):
    await state.update_data(usr_name=message.text)
    eventData = await state.get_data()
    await message.answer(f'Имя контактного лица - {message.text}?', reply_markup=ClientConfirmCancelApplicationFields(eventData['event_id']).markup)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(text='client-fill-children-name', state=UserStates.clientAwaitSelectToView)
async def clientAwaitApplicationName(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer('Введите имя или имена детей через запятую', reply_markup=ClientCancel.markup)
    await state.set_state(UserStates.clientAwaitApplicationChildrenName.state)

@dp.message_handler(state=UserStates.clientAwaitApplicationChildrenName)
async def clientConfirmApplicationName(message: types.Message, state: FSMContext):
    await state.update_data(children_names=message.text)
    eventData = await state.get_data()
    await message.answer(f'Имена детей: {message.text}?', reply_markup=ClientConfirmCancelApplicationFields(eventData['event_id']).markup)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(text='client-fill-phone-number', state=UserStates.clientAwaitSelectToView)
async def clientAwaitApplicationName(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer('Введите контактный номер телефона', reply_markup=ClientCancel.markup)
    await state.set_state(UserStates.clientAwaitApplicationPhone.state)

@dp.message_handler(state=UserStates.clientAwaitApplicationPhone)
async def clientConfirmApplicationName(message: types.Message, state: FSMContext):
    await state.update_data(usr_phone=message.text)
    eventData = await state.get_data()
    await message.answer(f'Контактный номер телефона - {message.text}?', reply_markup=ClientConfirmCancelApplicationFields(eventData['event_id']).markup)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(text='client-fill-children-amount', state=UserStates.clientAwaitSelectToView)
async def clientAwaitApplicationName(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer('Введите количество детей', reply_markup=ClientCancel.markup)
    await state.set_state(UserStates.clientAwaitApplicationGuestsAmount.state)

@dp.message_handler(state=UserStates.clientAwaitApplicationGuestsAmount)
async def clientConfirmApplicationName(message: types.Message, state: FSMContext):
    eventData = await state.get_data()
    if eventData['event_quota'] < int(message.text):
        await message.answer(f'Увы, на Вас не хватит мест :(\n\nПриходите в другой раз!', reply_markup=StartKeyboard.markup)
        await state.set_state(UserStates.client.state)
    else:
        await state.update_data(guests_amount=int(message.text))
        eventData = await state.get_data()
        await message.answer(f'Количество детей - {message.text}?', reply_markup=ClientConfirmCancelApplicationFields(eventData['event_id']).markup)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(text='client-confirm-application', state=UserStates.clientAwaitSelectToView)
async def clientRegApplication(callback_query: types.CallbackQuery, state: FSMContext):
    eventData = await state.get_data()
    if register_application(session, eventData['usr_id'], eventData['event_id'], eventData['children_names'], eventData['usr_phone'], eventData['guests_amount']):
        await callback_query.message.answer('Заявка оставлена!', reply_markup=StartKeyboard.markup)
        await state.set_state(UserStates.client)
    else:
        await callback_query.message.answer('Что-то пошло не так.. Скорее всего Ваша заявка уже есть в базе.', reply_markup=StartKeyboard.markup)
        await state.set_state(UserStates.client)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.callback_query_handler(text='my-events', state=UserStates.client)
async def clientViewMyEvents(callback_query: types.CallbackQuery, state: FSMContext):
    # events = get_events_by_applications(session, str(callback_query.from_user.id))
    events = [[x.id, x.name, x.client_name, x.isPublic, x.time.strftime("%H:%M")] for x in get_events_by_applications(session, str(callback_query.from_user.id))]
    await callback_query.message.edit_text('Ваши заявки:', reply_markup=ClientMyEvents(events, 'usr').markup)
    await state.set_state(UserStates.clientAwaitSelectViewApplication.state)


@dp.callback_query_handler(lambda c: re.fullmatch(r"id:[0-9]{1,}-time:[0-9]{2}:[0-9]{2}", c.data), state=UserStates.clientAwaitSelectViewApplication)
async def clientSelectedApplication(callback_query: types.CallbackQuery, state: FSMContext):
    event = get_event_by_id(session, int(callback_query.data[callback_query.data.index(':')+1:callback_query.data.index('-')]))
    await state.update_data(event_id=event.id)
    await state.update_data(event_name=event.name)
    await state.update_data(client_name=event.client_name)
    await state.update_data(event_platform=event.platform)
    await state.update_data(event_quota=get_vacant_amount_by_event_id(session, event.id))
    await state.update_data(event_description=event.description)
    await state.update_data(event_datetime=f"{date.strftime(event.date, '%d.%m.%Y')} {time.strftime(event.time, '%H:%M')}")
    # await state.update_data(event_isPublic=event.isPublic)
    eventData = await state.get_data()
    await callback_query.message.edit_text(f"Карточка мероприятия:\n\nНазвание мероприятия: {eventData['event_name']}\nДата и время проведения мероприятия: {eventData['event_datetime']}\nПлощадка проведения: {platforms[eventData['event_platform']]}\nСвободных мест: {eventData['event_quota']}\nОписание мероприятия: {eventData['event_description']}", 
                                            reply_markup=ClientMyEventsUnsubscribe.markup)


@dp.callback_query_handler(text='client-cancel-application', state=UserStates.clientAwaitSelectViewApplication)
async def clientCancelApplication(callback_query: types.CallbackQuery, state: FSMContext):
    eventData = await state.get_data()
    if delete_application(session, eventData['event_id'], eventData['usr_id']):
        await callback_query.message.edit_text('Заявка удалена!', reply_markup=StartKeyboard.markup)
        await state.set_state(UserStates.client)
    else:
        await callback_query.message.edit_text('Что-то пошло не так.. Попробуйте еще раз позже.', reply_markup=StartKeyboard.markup)
        await state.set_state(UserStates.client)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dp.message_handler(state=UserStates.clientRegName)
async def clientAwaitName(message: types.Message, state: FSMContext):
    await state.update_data(usr_name=message.text)
    await message.answer(f'Ваше имя - {message.text}?', reply_markup=ClientConfirmName.markup)

@dp.callback_query_handler(text='confirm-client-user-name', state=UserStates.clientRegName)
async def clientRequestPhone(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer(f'Введите свой номер телефона.')
    await state.set_state(UserStates.clientRegPhone.state)

@dp.message_handler(state=UserStates.clientRegPhone)
async def clientAwaitPhone(message: types.Message, state: FSMContext):
    await state.update_data(usr_phone=message.text)
    await message.answer(f'Ваш номер телефона - {message.text}?', reply_markup=ClientConfirmPhone.markup)

@dp.callback_query_handler(text='confirm-client-phone', state=UserStates.clientRegPhone)
async def clientReg(callback_query: types.CallbackQuery, state: FSMContext):
    clientData = await state.get_data()
    if register_user(session, clientData['usr_id'] , clientData['usr_name'], clientData['usr_phone'], role='usr'):
        user = get_user_by_id(session, str(callback_query.from_user.id))
        await state.update_data(guests_amount=1)
        await state.update_data(children_names='')
        await state.update_data(usr_id=user.id)
        await state.update_data(usr_name=user.name)
        await state.update_data(usr_phone=user.phone)
        await state.set_state(UserStates.client.state)
        await state.update_data(usr_role='usr')
        await callback_query.message.answer("Здравствуйте! Чем я могу помочь?", reply_markup=StartKeyboard.markup)
    else:
        await state.finish()
        await callback_query.message.answer("Что-то пошло не так.. Попробуйте еще раз позже.")

@dp.callback_query_handler(text='client-cancel', state=[UserStates.client,
                                                        UserStates.clientRegName,
                                                        UserStates.clientRegPhone,
                                                        UserStates.clientAwaitSelectToView,
                                                        UserStates.clientAwaitApplicationName,
                                                        UserStates.clientAwaitApplicationPhone,
                                                        UserStates.clientAwaitApplicationGuestsAmount,
                                                        UserStates.clientAwaitSelectViewApplication])
async def clientGoBack(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.client.state)
    await callback_query.message.answer("Здравствуйте! Чем я могу помочь?", reply_markup=StartKeyboard.markup)

@dp.message_handler(state='*')
async def start(message: types.Message, state: FSMContext):
    user = get_user_by_id(session, str(message.from_user.id))
    if not user:
        await state.update_data(usr_id=str(message.from_user.id))
        await state.set_state(UserStates.clientRegName.state)
        await message.answer('Здравствуйте! Как я могу к Вам обращаться?')
    elif user.role == 'adm':
        await state.update_data(event_id='')
        await state.update_data(event_name='')
        await state.update_data(client_name='')
        await state.update_data(event_platform='')
        await state.update_data(event_quota='')
        await state.update_data(event_description='')
        await state.update_data(event_datetime='')
        await state.update_data(event_isPublic='')
        await state.update_data(usr_role='adm')
        await state.update_data(admin_mode='reg')
        await state.update_data(isEvent=True)
        await state.update_data(class_weekdays=[0 for _ in range(7)])
        await state.update_data(class_intervals=[0 for _ in range(9)])
        await state.set_state(UserStates.admin.state)
        await message.answer("Добро пожаловать в админ-панель", reply_markup=AdminStartKeyboard.markup)
    elif user.role == 'emp':
        await state.set_state(UserStates.employee.state)
        await state.update_data(usr_role='emp')
        await message.answer("Добро пожаловать в панель сотрудника", reply_markup=EmpStartKeyboard.markup)
    elif user.role == 'usr':
        await state.update_data(guests_amount=1)
        await state.update_data(children_names='')
        await state.update_data(usr_id=user.id)
        await state.update_data(usr_name=user.name)
        await state.update_data(usr_phone=user.phone)
        await state.set_state(UserStates.client.state)
        await state.update_data(usr_role='usr')
        await message.answer("Здравствуйте! Чем я могу помочь?", reply_markup=StartKeyboard.markup)

@dp.callback_query_handler(lambda c: c.data.startswith("confirm-"), state=[UserStates.client,
                                                                        UserStates.clientRegName,
                                                                        UserStates.clientRegPhone,
                                                                        UserStates.clientAwaitSelectToView,
                                                                        UserStates.clientAwaitApplicationName,
                                                                        UserStates.clientAwaitApplicationPhone,
                                                                        UserStates.clientAwaitApplicationGuestsAmount,
                                                                        UserStates.clientAwaitSelectViewApplication])
async def clientConfirmApplication(callback_query: types.CallbackQuery, state: FSMContext):
    if confirm_application(session, int(callback_query.data.split('-')[1])):
        await callback_query.message.edit_text('Спасибо, Ваше участие подтверждено!')
    else:
        await callback_query.message.edit_text('Кажется, что-то пошло не так..')

@dp.callback_query_handler(lambda c: c.data.startswith("decline-"), state=[UserStates.client,
                                                                        UserStates.clientRegName,
                                                                        UserStates.clientRegPhone,
                                                                        UserStates.clientAwaitSelectToView,
                                                                        UserStates.clientAwaitApplicationName,
                                                                        UserStates.clientAwaitApplicationPhone,
                                                                        UserStates.clientAwaitApplicationGuestsAmount,
                                                                        UserStates.clientAwaitSelectViewApplication])
async def clientDeclineApplication(callback_query: types.CallbackQuery, state: FSMContext):
    if delete_application_by_id(session, callback_query.data.split('-')[1]):
        await callback_query.message.edit_text('Спасибо, Ваша заявка удалена!')
    else:
        await callback_query.message.edit_text('Кажется, что-то пошло не так..')


@dp.callback_query_handler(text='dump-db', state=UserStates.admin)
async def dumpHandler(callback_query: types.CallbackQuery, state: FSMContext):
    await dumpDatabase(bot, session)


@dp.callback_query_handler(text='control-events', state=UserStates.admin)
async def controlEvents(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text('Выберите действие', reply_markup=AdminControlEvents.markup)

@dp.callback_query_handler(text='control-classes', state=UserStates.admin)
async def controlClasses(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text('Выберите действие', reply_markup=AdminControlClasses.markup)

if __name__ == '__main__':
    try:
        # scheduler.add_job(dumpDatabase, 'interval', args=[bot, session], weeks=2, start_date=datetime.strptime('2023-12-01 11:00:00', '%Y-%m-%d %H:%M:%S'), end_date=datetime.strptime('2030-12-28 11:00:00', '%Y-%m-%d %H:%M:%S'))
        scheduler.add_job(dumpDatabase, CronTrigger.from_crontab('0 11 1,14 * *'), args=[bot, session], id='dumpDB')
        # scheduler.add_job(checker, 'interval', args=[bot, session], days=1, start_date=datetime.strptime('2023-12-01 11:00:00', '%Y-%m-%d %H:%M:%S'), end_date=datetime.strptime('2030-12-28 11:00:00', '%Y-%m-%d %H:%M:%S'))
        scheduler.add_job(checker, CronTrigger.from_crontab('0 11 * * *'), args=[bot, session], id='checker')
        reschedule_on_startup(session=session, scheduler=scheduler)
        scheduler.start()
        executor.start_polling(dp, skip_updates=True)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
