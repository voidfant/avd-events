import logging

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from db import models
# import models
from db.database import engine

import os
import csv
from typing import Union
from datetime import datetime, date, time, timedelta

# from bot.utils import build_application_info

def dump_table(db: Session, table: str, filename: str) -> bool:
    try:
        basedir = os.path.abspath(os.path.dirname(__file__))
        results = pd.read_sql_query(f'select * from {table}', engine)
        results.to_csv(os.path.join(basedir, f'{filename}.csv'), index=False, sep=";")
        # or maybe use outcsv.writerows(records)
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

def get_all_public_events(db: Session) -> list:
    result = [x.Event for x in db.execute(select(models.Event)
                                          .where(models.Event.isPublic))]

    return result 

def get_event_by_id(db: Session, event_id: int) -> models.Event:
    result = db.execute(select(models.Event)
                        .where(models.Event.id == event_id)).one()
    
    return result.Event



def get_events_by_date(db: Session, event_date: date) -> list:
    # exact_day = lambda x, y: x > date
    # result = [x.Event for x in db.execute(select(models.Event)
    #                                       .where(models.Event.timestamp.date() == date.date()))]
    # result = [x.Event for x in models.Event.query.filter_by(date=date).all()]
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

def get_user_by_id(db: Session, user_id: str) -> models.User | int:
    try:    
        result = db.execute(select(models.User)
                            .where(models.User.id == user_id)).one()
        return result.User
    except Exception as e:
        return 0
    

def get_application_by_id(db: Session, application_id: int) -> models.Application:
    result = db.execute(select(models.Application)
                        .where(models.Application.id == application_id)).one()
    
    return result.Application


def get_applications_by_applicant(db: Session, user_id: str) -> list:
    result = [x.Application for x in db.execute(select(models.Application)
                                    .where(models.Application.user_id == user_id))]
    
    return result

def get_users_by_event(db: Session, event_id: int) -> list:
    applications = [x.Application for x in db.execute(select(models.Application)
                            .where(models.Application.id == id))]
    result = []
    for i in applications:
        result.append([i.id, i.user_id, db.execute(select(models.Event)
                                                   .where(models.Event.id == event_id)).one().Event.date])
    
    return result


def get_not_confirmed_applications_by_event(db: Session, event_id: int) -> list:
    applications = [x.Application for x in db.execute(select(models.Application)
                            .where(models.Application.event_id == event_id)
                            .where(models.Application.confirmed == False))]
    result = []
    print(f"\n\n\n\n{event_id}{applications}\n\n\n\n")
    for i in applications:
        result.append([i.id, db.execute(select(models.User)
                                        .where(models.User.id == i.user_id)).one().User.name,
                                        i.user_id,
                                        db.execute(select(models.Event)
                                                   .where(models.Event.id == event_id)).one().Event.date])

    return result    


def get_applications_by_event(db: Session, event_id: int) -> list:
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


def get_events_by_applications(db: Session, user_id: str) -> list:
    # applications = [x.Application.event_id for x in db.execute(select(models.Application)
    #                                                .where(models.Application.user_id == user_id))]
    
    # events = [x.Event for x in db.execute(select(models.Event)
    #                                       .where(models.Event.id == models.Application.event_id)
    #                                       .where(models.Application.user_id == md))]
    events = [x.Event for x in db.execute(select(models.Event)
                                .where(models.Application.user_id == user_id)
                                .where(models.Application.event_id == models.Event.id))]
    print(f"\n\n\n\n\n{events}\n\n\n\n\n")
    return events

def get_latest_event_record(db: Session) -> models.Event:
    result = db.query(models.Event).order_by(models.Event.id.desc()).first()

    return result
    
def get_subscriptions_by_platform(db: Session, platform: str) -> list:
    result = [x.Subscription for x in db.execute(select(models.Subscription)
                                                 .where(models.Subscription.platform == platform))]
    
    return result

def get_subscriptions_by_id(db: Session, user_id: str) -> list:
    result = [x.Subscription for x in db.execute(select(models.Subscription)
                                                 .where(models.Subscription.user_id == user_id))]

    return result


def get_vacant_amount_by_event_id(db: Session, event_id: int) -> int:
    quota = db.execute(select(models.Event)
                        .where(models.Event.id == event_id)).one().Event.quota
    occupied = sum([x.Application.guests_amount for x in db.execute(select(models.Application)
                                                                    .where(models.Application.event_id == event_id))])
    
    return quota - occupied


# def set_admin_status(db: Session, user_id: str, role: bool = 0):
#     try: 
#         db.execute(update(models.User)
#                    .where(models.User.id == user_id)
#                    .values(role = role))
#         db.commit()
#     except Exception as e:
#         logging.log(logging.ERROR, e)
#         db.rollback()
#     finally:
#         db.close()


# def get_users(db: Session) -> list:
#     result = [[x.Manager.id, x.Manager.role] for x in db.execute(select(models.Manager))]

#     return result


# def get_managers(db: Session) -> list:
#     result = [[x.Manager.id, x.Manager.name] for x in db.execute(select(models.Manager)
#                                                                  .where(models.Manager.role == 'manager'))]
#     return result


# def get_admins(db: Session) -> list:
#     result = [x.Manager.id for x in db.execute(select(models.Manager)
#                                                .where(models.Manager.role == 'admin'))]
#     return result


# def get_manager_by_id(db: Session, manager_id: str) -> list:
#     data = db.execute(select(models.Manager)
#                       .where(models.Manager.id == str(manager_id))).one()
#     return [data.Manager.name, data.Manager.id]


# def get_available_applications(db: Session) -> list:
#     result = [' - '.join([str(x.Application.id), x.Application.kind])
#               for x in db.execute(select(models.Application)
#                                   .where(models.Application.manager_id == None))]
#     logging.log(logging.INFO, result)
#     return list(result)


# def get_all_applications(db: Session) -> Union[list, bool]:
#     try:
#         result = [' - '.join([str(x.Application.id), x.Application.kind]) for x in
#                   db.execute(select(models.Application))]
#     except Exception as e:
#         logging.log(logging.ERROR, e)
#         return False
#     return result


# def get_all_applications_ids(db: Session) -> list:
#     result = [x.Application.id for x in db.execute(select(models.Application))]
#     return result


# def get_application_by_id(db: Session, application_id: str) -> models.Application:
#     result = db.execute(select(models.Application)
#                         .where(models.Application.id == application_id)).one()
#     return result.Application


# def get_application_info_by_id(db: Session, application_id: str) -> str:
#     return build_application_info(get_application_by_id(db, application_id))


# def assign_application(db: Session, application_id: int, manager_id: str) -> bool:
#     try:
#         db.execute(update(models.Application).values(manager_id=manager_id)
#                    .where(models.Application.id == application_id))
#         db.commit()
#         return True
#     except Exception as e:
#         logging.log(logging.ERROR, e)
#         return False


# def get_taken_applications(db: Session, manager_id: str) -> Union[list, bool]:
#     try:
#         result = [' - '.join([str(x.Application.id), x.Application.kind]) for x in
#                   db.execute(select(models.Application)
#                              .where(models.Application.manager_id == str(manager_id)))]
#     except Exception as e:
#         logging.log(logging.ERROR, e)
#         return False
#     return result


# def register_application(db: Session, client_name: str, kind: str, phone: str, selected_apartment: str = None,
#                          email: str = None, client_comment: str = None, manager_comment: str = None) -> bool:
#     try:
#         db.add(models.Application(
#             client_name=client_name,
#             kind=kind,
#             phone=phone,
#             email=email,
#             client_comment=client_comment,
#             manager_comment=manager_comment,
#             selected_apartment=selected_apartment
#         ))
#         db.commit()
#         return True
#     except Exception as e:
#         logging.log(logging.ERROR, e)
#         return False


# def close_application(db: Session, application_id: int) -> bool:
#     try:
#         db.execute(delete(models.Application).where(models.Application.id == application_id))
#         db.commit()
#         return True
#     except Exception as e:
#         logging.log(logging.ERROR, e)
#         return False


# def retract_application(db: Session, application_id: int) -> bool:
#     try:
#         db.execute(update(models.Application)
#                    .values(manager_id=None)
#                    .where(models.Application.id == application_id))
#         db.commit()
#         return True
#     except Exception as e:
#         logging.log(logging.ERROR, e)
#         return False


# def retract_all_applications(db: Session, manager_id: str) -> bool:
#     try:
#         db.execute(update(models.Application)
#                    .values(manager_id=None)
#                    .where(models.Application.manager_id == manager_id))
#         db.commit()

#         return True
#     except Exception as e:
#         logging.log(logging.ERROR, e)
#         return False


# def add_comment_to_application(db: Session, application_id: int, manager_comment: str) -> bool:
#     try:
#         db.execute(update(models.Application)
#                    .values(manager_comment=manager_comment)
#                    .where(models.Application.id == application_id))
#         db.commit()
#         return True
#     except Exception as e:
#         logging.log(logging.ERROR, e)
#         return False


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


# def add_manager(db: Session, manager_id: str, name: str) -> bool:
#     try:
#         db.add(models.Manager(
#             name=name,
#             id=manager_id,
#             role='manager',
#         ))
#         db.commit()
#         return True
#     except Exception as e:
#         logging.log(logging.ERROR, e)
#         return False

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
# def delete_manager(db: Session, manager_id: str) -> bool:
#     try:
#         if not retract_all_applications(db, manager_id):
#             raise Exception

#         db.execute(delete(models.Manager)
#                    .where(models.Manager.id == manager_id))
#         db.commit()
#         return True
#     except Exception as e:
#         logging.log(logging.ERROR, e)
#         return False
