import threading
from requests import get

way = 'https://vitamin-calculator.herokuapp.com/monitoring'


def interrupt():
    try:
        x = get(way)
        print(x)
    except:
        print(f'ошибка в подключении по адресу {way}')

    threading.Timer(1, interrupt).start()   # запуск каждые 20 минут
