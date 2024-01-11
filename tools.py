from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import types, Bot

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from bot.keyboards import *
# from db.database import *
from db.crud import *

platforms = {'verh': 'Верхние Лихоборы', 'voyk': 'Войковская', 'zhiv': '\"Живописно\"', 'musm': 'Музей Света и Цвета', '': ''}
weekdays_arr = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
intervals_arr = ['14:00 - 16:00', '16:00 - 18:00', '18:00 - 20:00']

async def checker(bot: Bot, session: Session) -> None:
    events = check_if_up_to_date(session)
    for i in events:
        if i[1] == 1:
            continue
        elif i[1] == 0:
            delete_event(session, i[0].id)
        else:
            applications = get_not_confirmed_applications_by_event(session, i[0].id)            
            for j in applications:
                await bot.send_message(chat_id=j[2], text=f'Вы подтверждаете свое участие в мероприятии, которое состоится {datetime.strftime(j[3], "%d.%m.%Y")}?',reply_markup=ClientSendConfirm(j[0]).markup)

async def dumpDatabase(bot: Bot, session: Session) -> None:
    dump_table(session, 'events', 'events_dump')
    dump_table(session, 'applications', 'applications_dump')
    admins = get_all_admins(session)
    basedir = os.path.abspath(os.path.dirname(__file__))
    for i in admins:
        events = types.InputFile(os.path.join(basedir, f'db/events_dump.csv'), filename=f'events_dump_{datetime.today().strftime("%d-%m-%Y")}.csv')
        applications = types.InputFile(os.path.join(basedir, f'db/applications_dump.csv'), filename=f'applications_dump_{datetime.today().strftime("%d-%m-%Y")}.csv')
        await bot.send_message(chat_id=i.id, text=f'Резервная копия базы мероприятий от {datetime.today().strftime("%d.%m.%Y")}:')
        await bot.send_document(chat_id=i.id, document=events)
        await bot.send_document(chat_id=i.id, document=applications)


async def notifier(bot: Bot, session: Session, event: models.Event, state: MemoryStorage) -> None:
    subscriptions = get_subscriptions_by_platform(session, event.platform)
    for i in subscriptions:
        await state.update_data(chat=i.user_id, user=i.user_id, event_id=event.id)
        await state.update_data(chat=i.user_id, user=i.user_id, event_name=event.name)
        await state.update_data(chat=i.user_id, user=i.user_id, client_name=event.client_name)
        await state.update_data(chat=i.user_id, user=i.user_id, event_platform=event.platform)
        await state.update_data(chat=i.user_id, user=i.user_id, event_quota=get_vacant_amount_by_event_id(session, event.id))
        await state.update_data(chat=i.user_id, user=i.user_id, event_description=event.description)
        await state.update_data(chat=i.user_id, user=i.user_id, event_datetime=f"{date.strftime(event.date, '%d.%m.%Y')} {time.strftime(event.time, '%H:%M')}")
        await bot.send_message(chat_id=i.user_id, text=f'Рассылка по подписке на филиал {platforms[i.platform]}\n\nНазвание мероприятия: {event.name}\nДата и время проведения мероприятия: {date.strftime(event.date, "%d.%m.%Y")} {time.strftime(event.time, "%H:%M")}\nСвободных мест: {get_vacant_amount_by_event_id(session, event.id)}\nОписание мероприятия: {event.description}',
                              reply_markup=SubscribeKeyboard(event.id).markup)

def serialize_weekdays(weekdays, direction = 0) -> str:
    if not direction:
        readable = []
        for k, v in enumerate(weekdays):
            if v:
                readable.append(weekdays_arr[k])
        return ', '.join(readable)
    return ''.join(map(str, map(int, weekdays)))

def serialize_intervals(intervals, direction = 0) -> str:
    if not direction:
        readable = []
        for k, v in enumerate(intervals):
            if v:
                readable.append(intervals_arr[k])
        return ', '.join(readable)
    return ''.join(map(str, map(int, intervals)))


# async def schedule_class(session: Session, class_id: int, scheduler: AsyncIOScheduler, initial: bool) -> bool:
#     if initial:
#         ...
#         return
#     class_to_schedule = get_class_by_id(session, class_id)
#     if class_to_schedule is None:
#         return
#     for i in class_to_schedule.weekdays:
#         if int(i):
#             register_event()

#     # res = register_event()

#     scheduler.add_job(schedule_class, CronTrigger.from_crontab('0 11 * * MON'), coalesce=True, id=class_id)
    