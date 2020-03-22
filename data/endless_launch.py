import schedule
from requests import get


def launch():
    get('http://vitamin-calculator.herokuapp.com/')


schedule.every(20).minutes.do(launch)

while True:
    schedule.run_pending()

