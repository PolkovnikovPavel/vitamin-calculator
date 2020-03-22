import sqlalchemy

from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


NORM = 50


def set_color(percent=100):
    if percent > 122 or percent < 78:
        col = '#ff6666'
    elif percent > 113 or percent < 87:
        col = '#fcf18d'
    else:
        col = '#a7d984'
    return col


class Timetable(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'timetable'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    date = sqlalchemy.Column(sqlalchemy.DateTime)
    breakfast = sqlalchemy.Column(sqlalchemy.JSON)
    dinner = sqlalchemy.Column(sqlalchemy.JSON)
    supper = sqlalchemy.Column(sqlalchemy.JSON)
    master = sqlalchemy.Column(sqlalchemy.Integer,
                               sqlalchemy.ForeignKey("users.id"))
    is_varfarin = sqlalchemy.Column(sqlalchemy.Boolean)
    vitamin = sqlalchemy.Column(sqlalchemy.Float)
    percent = sqlalchemy.Column(sqlalchemy.Integer,
                                default=vitamin / NORM * 100)
    ch_ch_date = sqlalchemy.Column(sqlalchemy.String)

    color = sqlalchemy.Column(sqlalchemy.String, default='#ff6666')
