from datetime import time

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import types, Bot

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from bot.keyboards import *
from db.crud import *

platforms = {'verh': 'Верхние Лихоборы', 'voyk': 'Войковская', 'zhiv': '\"Живописно\"', 'musm': 'Музей Света и Цвета', '': ''}
weekdays_arr = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
# intervals_arr = ['14:00 - 16:00', '16:00 - 18:00', '18:00 - 20:00']
intervals_arr = ['11:00 - 13:00', '12:00 - 14:00', '13:00 - 15:00', '14:00 - 16:00', '15:00 - 17:00', '16:00 - 18:00', '17:00 - 19:00', '18:00 - 20:00', '19:00 - 21:00']
intervals_numeric = [(11, 0), (12, 0), (13, 0), (14, 0), (15, 0), (16, 0), (17, 0), (18, 0), (19, 0)]


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
    logging.log(logging.ERROR, weekdays)
    if not direction:
        readable = []
        for k, v in enumerate(weekdays):
            if v:
                readable.append(weekdays_arr[k])
        logging.log(logging.ERROR, readable)
        return ', '.join(readable)
    
    return ''.join(map(str, map(int, weekdays)))


def serialize_intervals(intervals, direction = 0) -> str:
    logging.log(logging.ERROR, intervals)
    if not direction:

        readable = []
        for k, v in enumerate(intervals):
            if v:
                readable.append(intervals_arr[k])
        logging.log(logging.ERROR, readable)
        return ', '.join(readable)
    return ''.join(map(str, map(int, intervals)))


def get_week(date: date, initial: bool | None = None, weeksdelta: int = 0):
    res = []
    if initial == False:
        weeksdelta = 1
        
    if not initial:
        date = date - timedelta(days=date.weekday() + 1) + timedelta(weeks=weeksdelta)
        for _ in range(7):
            date += timedelta(days=1)
            res.append(date)    
    else:
        date = date - timedelta(days=date.weekday() + 1)
        for _ in range(14):
            date += timedelta(days=1)
            res.append(date)
    return res


def reschedule_on_startup(session: Session, scheduler: AsyncIOScheduler):
    all_classes = get_all_classes(db=session)
    for curr_class in all_classes:
        scheduler.add_job(schedule_class, CronTrigger.from_crontab('0 11 * * MON'), args=[session, curr_class.id, scheduler], coalesce=True, replace_existing=True, id=f'{curr_class.id}')


async def schedule_class(session: Session, class_id: int, scheduler: AsyncIOScheduler, initial: bool = False) -> bool:
    try:
        class_to_schedule = get_class_by_id(session, class_id)  
        if class_to_schedule is None:
            return
        today = datetime.utcnow().date()
        week = get_week(date=today, initial=initial)
        if initial:
            class_to_schedule.weekdays += class_to_schedule.weekdays
        for k_w, weekday in enumerate(class_to_schedule.weekdays):
            for k_i, interval in enumerate(class_to_schedule.intervals):
                if int(weekday) and int(interval):
                    if today - date(year=week[k_w].year, month=week[k_w].month, day=week[k_w].day) >= timedelta(days=1):
                        logging.log(logging.DEBUG, today - date(year=week[k_w].year, month=week[k_w].month, day=week[k_w].day))
                        continue
                    if not register_event(db=session,
                                        event_name=class_to_schedule.name,
                                        client_name='',
                                        event_platform=class_to_schedule.platform,
                                        event_quota=class_to_schedule.quota,
                                        event_description=class_to_schedule.description,
                                        event_datetime=datetime(year=week[k_w].year,
                                                                month=week[k_w].month, 
                                                                day=week[k_w].day, 
                                                                hour=intervals_numeric[k_i][0], 
                                                                minute=intervals_numeric[k_i][1]),
                                        event_isPublic=True,
                                        class_id=class_id
                                        ):
                        logging.log(logging.ERROR, class_id)
                    else:
                        logging.log(logging.DEBUG, "Добавил эвент")
        scheduler.add_job(schedule_class, CronTrigger.from_crontab('0 11 * * MON'), args=[session, class_id, scheduler], coalesce=True, replace_existing=True, id=f'{class_id}')
        return 1
    except Exception as e:
        logging.log(logging.ERROR, e)
        return 0
    

async def notify_clients_on_event_deletion(session: Session, bot: Bot, event_id: int | None = None, class_id: int | None = None):
    if class_id is None:
        applications = get_applications_by_event(db=session, event_id=event_id)
    else:
        applications = []
        events = get_events_by_class_id(db=session, class_id=class_id)
        for event in events:
            applications.extend(get_applications_by_event(db=session, event_id=event.id))
    if applications is None or not applications:
        logging.log(logging.ERROR, (applications, event_id, class_id))
        return
    for application in applications:
        logging.log(logging.ERROR, application[2])
        await bot.send_message(chat_id=application[2], text=f'Мероприятие, запланированное на {datetime.strftime(application[3], "%d.%m.%Y")} отменено или изменено, в связи с чем Ваша заявка обнулена.')
    