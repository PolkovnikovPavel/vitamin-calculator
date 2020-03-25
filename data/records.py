import sqlalchemy

from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


NORM = 50


def set_color(percent=100):
    if percent > 128 or percent < 72:
        col = '#e66761'
    elif percent > 121 or percent < 79:
        col = '#ff9980 '
    elif percent > 115 or percent < 85:
        col = '#fcf0b3'
    elif percent > 107 or percent < 93:
        col = '#c9dc87'
    else:
        col = '#a7d984'
    return col


class Timetable(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'timetable'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    date = sqlalchemy.Column(sqlalchemy.String)
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
    summ = sqlalchemy.Column(sqlalchemy.Integer)

    color = sqlalchemy.Column(sqlalchemy.String, default='#ff6666')
