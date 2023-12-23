from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from sqlalchemy_utils import create_database, database_exists

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://konstantin:7786@localhost:5432/avd-events"

if not database_exists(SQLALCHEMY_DATABASE_URL):
    create_database(SQLALCHEMY_DATABASE_URL)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

session = Session(bind=engine)

Base = declarative_base()