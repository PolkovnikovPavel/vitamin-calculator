import sqlalchemy

from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


NORM = 72.5


def set_status(percent=100):

    if percent > 117.2:
        status = f'''Норма сильно превышена, опасно тем, что кровь будет очень густой, чревато тромбозами!
Нужно уменьшить потребление витамина К на {round(percent + 0.5 - 117, 2)}%'''
    elif percent > 110.75:
        status = 'Количистов витамина К находится в максимальной граници нормы'
    elif percent > 104.4:
        status = 'Содержание витамина К близко к идеальному'
    elif percent < 82.8:
        status = f'''Витамин К намного меньше нормы, кровь очень жидкая, крайне опасно внутренними и другими кровотечениями!
Необходимо увеличить потребление витамина К на {round(82.8 - percent, 2)}%'''
    elif percent < 89.25:
        status = 'Количество витамина К близко к минимальным значениям нормы, можно увеличить потребление продуктов с витамином К'
    elif percent < 95.6:
        status = 'Содержание витамина К близко к идеальному'
    else:
        status = 'Идеальное содержание витамина К'
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
    all_products = sqlalchemy.Column(sqlalchemy.String,
                                     default='Не выбрано или ошибка')
    all_products_varfarin = sqlalchemy.Column(sqlalchemy.String)

    color = sqlalchemy.Column(sqlalchemy.String, default='#ff6666')
