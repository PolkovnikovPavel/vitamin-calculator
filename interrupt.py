import threading
from requests import get
from data import db_session
from data.activity import Activities

way = 'https://vitamin-calculator.herokuapp.com/monitoring'


def interrupt():
    try:
        x = get(way)
        print(x)
    except:
        session = db_session.create_session()
        user = 0

        active = Activities(
            name=f'ERROR IN REQUEST ON {way}',
            id_user=user
        )
        session.add(active)
        session.commit()

    threading.Timer(1200, interrupt).start()   # запуск каждые 20 минут
