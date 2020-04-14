import threading

from requests import get

from data import db_session
from data.activity import Activities

way = 'https://vitamin-calculator.herokuapp.com/monitoring'


def interrupt():  # это сделаное, чтоб сервер не усыпал
    try:
        x = get(way)  # благодаря этому запросу создаётся видимость активности
        print(x)
    except:
        session = db_session.create_session()

        active = Activities(
            name=f'ERROR IN REQUEST ON {way}',
            id_user=0
        )
        session.add(active)  # сохранить факт ошибки
        session.commit()

    threading.Timer(1200, interrupt).start()  # запуск каждые 20 минут


def start_interrupt():
    threading.Timer(1200, interrupt).start()  # запуск interrupt через 20 минут
