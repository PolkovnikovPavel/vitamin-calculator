import sqlalchemy
import datetime

from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Activities(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'activities'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, default='')
    id_user = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    date=sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now)
