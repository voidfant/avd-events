import logging

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete

from db import models
from db.database import engine


import os
import csv
from typing import Union
from datetime import datetime, date, time, timedelta


def dump_table(db: Session, table: str, filename: str) -> bool:
    try:
        basedir = os.path.abspath(os.path.dirname(__file__))
        results = pd.read_sql_query(f'select * from {table}', engine)
        results.to_csv(os.path.join(basedir, f'{filename}.csv'), index=False, sep=";")
        return 1
    except Exception as e:
        logging.log(e, logging.ERROR)
        return 0


def check_if_up_to_date(db: Session) -> list:
    events = [x.Event for x in db.execute(select(models.Event))]
    today = date.today()
    result = []
    for i in events:
        if today - i.date == timedelta(days=1):
            result.append([i, 0])
        elif today - i.date == timedelta(days=-1):
            result.append([i, 2])
        else:
            result.append([i, 1])
    
    return result


def get_all_events(db: Session) -> list:
    result = [x.Event for x in db.execute(select(models.Event))]

    return result 


def get_all_classes(db: Session) -> list:
    result = [x.ClassEvent for x in db.execute(select(models.ClassEvent))]

    return result


def get_all_public_events(db: Session) -> list:
    result = [x.Event for x in db.execute(select(models.Event)
                                          .where(models.Event.isPublic))]

    return result 

def get_event_by_id(db: Session, event_id: int) -> models.Event:
    result = db.execute(select(models.Event)
                        .where(models.Event.id == event_id)).one()
    
    return result.Event


def get_class_by_id(db: Session, class_id: int) -> models.ClassEvent | None:
    try:
        result = db.execute(select(models.ClassEvent)
                            .where(models.ClassEvent.id == class_id)).one()    
        return result.ClassEvent
    except Exception as e:
        return None

def get_events_by_date(db: Session, event_date: date) -> list:
    result = [x.Event for x in db.execute(select(models.Event)
                                          .filter_by(date=event_date))]

    return result

def get_events_by_date_and_platform(db: Session, event_date: date, platform: str) -> list:
    result = [x.Event for x in db.execute(select(models.Event)
                                          .filter_by(date=event_date)
                                          .filter_by(platform=platform))]

    return result

def get_public_events_by_date_and_platform(db: Session, event_date: date, platform: str) -> list:
    result = [x.Event for x in db.execute(select(models.Event)
                                          .filter_by(date=event_date)
                                          .filter_by(platform=platform)
                                          .where(models.Event.isPublic == True))]

    return result

def get_all_admins(db: Session) -> list:
    result = [x.User for x in db.execute(select(models.User)
                                          .where(models.User.role == 'adm'))]

    return result

def get_all_emps(db: Session) -> list:
    result = [x.User for x in db.execute(select(models.User)
                                          .where(models.User.role == 'emp'))]

    return result

def get_user_by_id(db: Session, user_id: str) -> models.User | None:
    try:    
        result = db.execute(select(models.User)
                            .where(models.User.id == user_id)).one()
        return result.User
    except Exception as e:
        logging.log(logging.ERROR, e)
        return None
    

def get_application_by_id(db: Session, application_id: int) -> models.Application | None:
    try:
        result = db.execute(select(models.Application)
                            .where(models.Application.id == application_id)).one()
        return result.Application
    except Exception as e:
        logging.log(logging.ERROR, e)
        return None


def get_applications_by_applicant(db: Session, user_id: str) -> list | None:
    try:
        result = [x.Application for x in db.execute(select(models.Application)
                                        .where(models.Application.user_id == user_id))]
        return result
    except Exception as e:
        logging.log(logging.ERROR, e)
        return None

def get_users_by_event(db: Session, event_id: int) -> list | None:
    try:
        applications = [x.Application for x in db.execute(select(models.Application)
                                .where(models.Application.id == id))]
        result = []
        for i in applications:
            result.append([i.id, i.user_id, db.execute(select(models.Event)
                                                    .where(models.Event.id == event_id)).one().Event.date])
        
        return result
    except Exception as e:
        logging.log(logging.ERROR, e)
        return None


def get_not_confirmed_applications_by_event(db: Session, event_id: int) -> list | None:
    try:
        applications = [x.Application for x in db.execute(select(models.Application)
                                .where(models.Application.event_id == event_id)
                                .where(models.Application.confirmed == False))]
        result = []
        for i in applications:
            result.append([i.id, db.execute(select(models.User)
                                            .where(models.User.id == i.user_id)).one().User.name,
                                            i.user_id,
                                            db.execute(select(models.Event)
                                                    .where(models.Event.id == event_id)).one().Event.date])
        return result    
    except Exception as e:
        logging.log(logging.ERROR, e)
        return None


def get_applications_by_event(db: Session, event_id: int) -> list | None:
    try:
        applications = [x.Application for x in db.execute(select(models.Application)
                                .where(models.Application.event_id == event_id))]
        result = []
        for i in applications:
            result.append([i.id, db.execute(select(models.User)
                                            .where(models.User.id == i.user_id)).one().User.name,
                                            i.user_id,
                                            db.execute(select(models.Event)
                                                    .where(models.Event.id == event_id)).one().Event.date])
        return result
    except Exception as e:
        logging.log(logging.ERROR, e)
        return None


def get_events_by_applications(db: Session, user_id: str) -> list | None:
    try:
        events = [x.Event for x in db.execute(select(models.Event)
                                    .where(models.Application.user_id == user_id)
                                    .where(models.Application.event_id == models.Event.id))]
        return events
    except Exception as e:
        logging.log(logging.ERROR, e)
        return None

def get_latest_event_record(db: Session) -> models.Event:
    result = db.query(models.Event).order_by(models.Event.id.desc()).first()

    return result
    
def get_subscriptions_by_platform(db: Session, platform: str) -> list | None:
    try:
        result = [x.Subscription for x in db.execute(select(models.Subscription)
                                                    .where(models.Subscription.platform == platform))]
        return result
    except Exception as e:
        logging.log(logging.ERROR, e)
        return None

def get_subscriptions_by_id(db: Session, user_id: str) -> list | None:
    try:
        result = [x.Subscription for x in db.execute(select(models.Subscription)
                                                    .where(models.Subscription.user_id == user_id))]
        return result
    except Exception as e:
        logging.log(logging.ERROR, e)
        return None


def get_vacant_amount_by_event_id(db: Session, event_id: int) -> int | None:
    try:
        quota = db.execute(select(models.Event)
                            .where(models.Event.id == event_id)).one().Event.quota
        occupied = sum([x.Application.guests_amount for x in db.execute(select(models.Application)
                                                                        .where(models.Application.event_id == event_id))])
        return quota - occupied
    except Exception as e:
        logging.log(logging.ERROR, e)
        return None

def edit_event(db: Session, event_id: int, event_name: str, client_name: str, event_platform: int, event_quota: int, event_description: str, event_datetime: datetime, event_isPublic: bool) -> bool:
    try:
        db.execute(update(models.Event)
                   .values(
                       name=event_name,
                       client_name=client_name,
                       platform=event_platform,
                       quota=event_quota,
                       description=event_description,
                       time=event_datetime.time(),
                       date=event_datetime.date(),
                       isPublic=event_isPublic
                       )
                    .where(models.Event.id == event_id))
        db.commit()
        return 1
    except Exception as e:
        logging.log(logging.ERROR, e)
        db.rollback()
        return 0
    finally:
        db.close()

def edit_class (db: Session, class_id: int, class_name: str, class_platform: int, class_quota: int, class_description: str, class_intervals: str, class_weekdays: str):
    try:
        db.execute(update(models.ClassEvent)
                   .values(
                        name=class_name,
                        platform=class_platform,
                        quota=class_quota,
                        description=class_description,
                        weekdays=class_weekdays,
                        intervals=class_intervals
                   )
                   .where(models.ClassEvent.id == class_id))
        db.commit()
        return 1
    except Exception as e:
        logging.log(logging.ERROR, e)
        db.rollback()
        return 0
    finally:
        db.close()


def confirm_application(db: Session, application_id: int):
    try:
        db.execute(update(models.Application)
                   .values(
                        confirmed=True
                       )
                    .where(models.Application.id == application_id))
        db.commit()
        return 1
    except Exception as e:
        logging.log(logging.ERROR, e)
        db.rollback()
        return 0
    finally:
        db.close()


def register_user(db: Session, id: str, name: str, phone: str, role: str) -> bool:
    try:
        db.add(models.User(
            id=id,
            name=name,
            phone=phone,
            role=role
        ))
        db.commit()
        return 1
    except Exception as e:
        logging.log(logging.ERROR, e)
        db.rollback()
        return 0
    finally:
        db.close()

def register_event(db: Session, event_name: str, client_name: str, event_platform: int, event_quota: int, event_description: str, event_datetime: datetime, event_isPublic: bool) -> bool:
    try:
        db.add(models.Event(
            name=event_name,
            client_name=client_name,
            platform=event_platform,
            quota=event_quota,
            description=event_description,
            # timestamp=event_datetime,
            time=event_datetime.time(),
            date=event_datetime.date(),
            isPublic=event_isPublic
        ))
        db.commit()
        return 1
    except Exception as e:
        logging.log(logging.ERROR, e)
        db.rollback()
        return 0
    finally:
        db.close()

def register_class(db: Session, class_name: str, class_platform: int, class_quota: int, class_description: str, class_intervals: str, class_weekdays: str) -> bool:
    try:
        db.add(models.ClassEvent(
            name=class_name,
            platform=class_platform,
            quota=class_quota,
            description=class_description,
            weekdays=class_weekdays,
            intervals=class_intervals
        ))
        db.commit()
        return 1
    except Exception as e:
        logging.log(logging.ERROR, e)
        db.rollback()
        return 0
    finally:
        db.close()

def register_application(db: Session, user_id: str, event_id: int, children_name: str, phone_number: str, guests_amount: int) -> bool:
    try:
        integrity_check = db.execute(select(models.Application)
                                        .where(models.Application.user_id == user_id)
                                        .where(models.Application.event_id == event_id)).first()
        if integrity_check is None:
            db.add(models.Application(
                event_id=event_id,
                user_id=user_id,
                children_name=children_name,
                phone_number=phone_number,
                guests_amount=guests_amount
            ))
            db.commit()
            return 1
        else:
            return 0
    except Exception as e:
        logging.log(logging.ERROR, e)
        db.rollback()
        return 0
    finally:
        db.close()


def toggle_subscription(db: Session, user_id: str, platform: str) -> bool:
    try:    
        result = [(x.Subscription.id, x.Subscription.platform) for x in db.execute(select(models.Subscription).where(models.Subscription.user_id == user_id))]
        sub_id = -1
        for i in result:
            if i[1] == platform:
                sub_id = i[0]
                break
        if sub_id != -1:
            db.execute(delete(models.Subscription)
                       .where(models.Subscription.id == sub_id))
        else:
            db.add(models.Subscription(
                user_id=user_id,
                platform=platform
            ))
        db.commit()
        return 1
    except Exception as e:
        logging.log(logging.ERROR, e)
        db.rollback()
        return 0
    finally:
        db.close()


def delete_event(db: Session, event_id: int) -> bool:
    try:
        db.execute(delete(models.Event)
                   .where(models.Event.id == event_id))
        db.commit()
        return 1
    except Exception as e:
        logging.log(logging.ERROR, e)
        db.rollback()
        return 0
    finally:
        db.close()

def delete_class(db: Session, class_id: int) -> bool:
    try:
        db.execute(delete(models.ClassEvent)
                   .where(models.ClassEvent.id == class_id))
        db.commit()
        return 1
    except Exception as e:
        logging.log(logging.ERROR, e)
        db.rollback()
        return 0
    finally:
        db.close()

def delete_employee(db: Session, emp_id: str) -> bool:
    try:
        db.execute(delete(models.User)
                   .where(models.User.id == emp_id))
        db.commit()
        return 1
    except Exception as e:
        logging.log(logging.ERROR, e)
        db.rollback()
        return 0
    finally:
        db.close()


def delete_application_by_id(db: Session, application_id: id) -> bool:
    try:
        db.execute(delete(models.Application)
                   .where(models.Application.id == application_id))
        db.commit()
        return 1
    except Exception as e:
        logging.log(logging.ERROR, e)
        db.rollback()
        return 0
    finally:
        db.close()   


def delete_application(db: Session, event_id: int, user_id: str) -> bool:
    try:
        db.execute(delete(models.Application)
                   .where(models.Application.event_id == event_id) 
                   .where(models.Application.user_id == user_id))
        db.commit()
        return 1
    except Exception as e:
        logging.log(logging.ERROR, e)
        db.rollback()
        return 0
    finally:
        db.close()

