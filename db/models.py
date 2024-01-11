from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Time, Date, SmallInteger, Text, VARCHAR
from sqlalchemy.sql import func

from db.database import Base
# from database import Base


# class Manager(Base):
#     __tablename__ = "managers"

#     id = Column(String, autoincrement=False, primary_key=True, index=True)
#     role = Column(String, index=True, nullable=False)
#     name = Column(String, index=True, nullable=False)


# class Application(Base):
#     __tablename__ = "applications"

#     id = Column(Integer, primary_key=True, index=True)
#     kind = Column(String, index=True)
#     client_name = Column(String, index=True)
#     phone = Column(String, unique=True, index=True)
#     email = Column(String, unique=True, index=True, nullable=True)
#     client_comment = Column(String, nullable=True)
#     manager_comment = Column(String, nullable=True)
#     selected_apartment = Column(String, nullable=True)
#     manager_id = Column(Integer, ForeignKey(Manager.id, ondelete="CASCADE"))
#     time_created = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(String, autoincrement=False, primary_key=True, index=True)
    role = Column(VARCHAR(3), nullable=False)
    name = Column(String, index=False, nullable=False)
    phone = Column(String, index=False, nullable=True)

class ClassEvent(Base):
    __tablename__ = "classes"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, index=False, nullable=True)
    platform = Column(VARCHAR(4), index=False, nullable=False)
    quota = Column(SmallInteger, index=False, nullable=True)
    description = Column(Text, nullable=True, index=False)
    weekdays = Column(VARCHAR(7), index=False, nullable=False)
    intervals = Column(VARCHAR(3), index=False, nullable=False)

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, index=False, nullable=True)
    client_name = Column(String, index=False, nullable=True)
    platform = Column(VARCHAR(4), index=False, nullable=False)
    quota = Column(SmallInteger, index=False, nullable=True)
    description = Column(Text, nullable=True, index=False)
    # timestamp = Column(DateTime, nullable=False)
    time = Column(Time, nullable=True)
    date = Column(Date, nullable=True)
    isPublic = Column(Boolean, nullable=False)
    class_id = Column(Integer, ForeignKey(ClassEvent.id, ondelete="CASCADE"), nullable=True, index=False)

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey(Event.id, ondelete="CASCADE"))
    user_id = Column(String, ForeignKey(User.id, ondelete="CASCADE"))
    children_name = Column(String, index=False, nullable=True)
    phone_number = Column(String, index=False, nullable=True)
    guests_amount = Column(SmallInteger, index=False, nullable=False)
    confirmed = Column(Boolean, server_default="false")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id = Column(String, ForeignKey(User.id, ondelete="CASCADE"))
    platform = Column(VARCHAR(4), index=False, nullable=False)