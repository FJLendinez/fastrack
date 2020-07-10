from datetime import datetime

import databases
import sqlalchemy
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

import env

if env.DB_USING_YEAR:
    y = datetime.now().year
    DATABASE_URL = f"sqlite:///./fastrack-{y}.db"
else:
    DATABASE_URL = f"sqlite:///./fastrack.db"

database = databases.Database(DATABASE_URL)
Base = declarative_base()


class PageViewDB(Base):
    __tablename__ = 'pageviews'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    domain = sqlalchemy.Column(sqlalchemy.String)
    url = sqlalchemy.Column(sqlalchemy.Text)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime)
    title = sqlalchemy.Column(sqlalchemy.Text)
    ip = sqlalchemy.Column(sqlalchemy.String)
    referrer = sqlalchemy.Column(sqlalchemy.Text)
    headers = sqlalchemy.Column(sqlalchemy.JSON)
    params = sqlalchemy.Column(sqlalchemy.JSON)
    query = sqlalchemy.Column(sqlalchemy.JSON)
    session_uuid = sqlalchemy.Column(sqlalchemy.String)
    history_uuid = sqlalchemy.Column(sqlalchemy.String)

    user = relationship("UsersDB", backref="user")


pageviews = PageViewDB.__table__


class UsersDB(Base):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    email = sqlalchemy.Column(sqlalchemy.String)
    history_uuid = sqlalchemy.Column(sqlalchemy.ForeignKey('pageviews.history_uuid'))
    pageviews = relationship("pageviews", back_populates="user")


users = UsersDB.__table__

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

Base.metadata.create_all(engine)
