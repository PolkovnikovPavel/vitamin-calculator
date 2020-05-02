import sqlalchemy
import datetime

from .db_session import SqlAlchemyBase
from data import db_session
from sqlalchemy_serializer import SerializerMixin
from flask_login import current_user


def activity(name=''):   # создаёт новую запись в активности
    session = db_session.create_session()
    if current_user.is_authenticated:   # кто сделал это действие
        user = current_user.id
    else:
        user = 0

    active = Activities(
        name=name,
        id_user=user
    )
    session.add(active)
    session.commit()


class Activities(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'activities'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, default='')
    id_user = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    date=sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now)
