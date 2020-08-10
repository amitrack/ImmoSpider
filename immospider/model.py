from sqlalchemy import (
    Integer, String, DateTime, Float, Boolean, Numeric)
from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def db_connect(connection_string):
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(connection_string)


def create_table(engine):
    Base.metadata.create_all(engine)


class Listing(Base):
    __tablename__ = "listing"

    id = Column(Integer, primary_key=True, autoincrement=True)
    immo_id = Column(String, primary_key=True, unique=True)
    url = Column(String)
    title = Column(String)
    address = Column(String)
    city = Column(String)
    zip_code = Column(String)
    district = Column(String)
    contact_name = Column(String)
    media_count = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    sqm = Column(Numeric)
    rent = Column(Numeric)
    rooms = Column(Numeric)
    extra_costs = Column(Numeric)
    kitchen = Column(String)
    balcony = Column(String)
    garden = Column(String)
    private = Column(Boolean)
    area = Column(Numeric)
    cellar = Column(Boolean)
    time_dest = Column(Numeric)  # time to destination using transit or driving
    time_dest2 = Column(Numeric)
    time_dest3 = Column(Numeric)
    creation_date = Column(DateTime)
    modification_date = Column(DateTime)
    publish_date = Column(DateTime)
    first_found= Column(DateTime)
    found_last = Column(DateTime)
    type = Column(String)
