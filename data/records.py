import sqlalchemy

from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


NORM = 72.5


def set_status(percent=100):

    if percent > 117.2:
        status = 'Норма сильно превышена, опасно тем, что кровь будет очень густой, опасно тромбозами!'
    elif percent > 110.75:
        status = 'Норма превышена, кровь будет густая, опасно тромбозами'
    elif percent > 104.4:
        status = 'Норма слегка превышена, возможно кровь будет густая, лучше уменьшить количество витамина К'
    elif percent < 82.8:
        status = 'Витамин К намного меньше нормы, кровь очень жидкая, крайне опасно внутреними и другими кровотечениями!'
    elif percent < 89.25:
        status = 'Витамин К меньше нормы, кровь будет жидкая, опасно внутреними и другими кровотечениями'
    elif percent < 95.6:
        status = 'Витамин К немного меньше нормы, кровь будет жиже чем обычно, возможно опасно кровотечениями'
    else:
        status = 'Данное расписание хорошое, если его соблюдать'
    return status


def set_color(percent=100):
    if percent > 117.2 or percent < 82.8:
        col = '#e66761'
    elif percent > 112.9 or percent < 87.1:
        col = '#ff9980 '
    elif percent > 108.6 or percent < 91.4:
        col = '#fcf0b3'
    elif percent > 104.3 or percent < 95.7:
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
    status = sqlalchemy.Column(sqlalchemy.String)

    color = sqlalchemy.Column(sqlalchemy.String, default='#ff6666')
