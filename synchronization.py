from requests import get
from data import db_session
from data.users import User
from data.activity import Activities
from data.records import Timetable
import datetime


def pars_str_to_date(date_str):
    days, time = date_str.split(' ')
    year, month, day = days.split('-')
    hours, minutes = time.split(':')

    date = datetime.datetime(int(year), int(month), int(day), int(hours),
                             int(minutes), 0)
    return date


way = 'https://vitamin-calculator.herokuapp.com/'
db_session.global_init("db/vitamin_calculator.sqlite")
session = db_session.create_session()


all_db = get(f'{way}/api/db').json()

users = all_db['db']['users']
timetables = all_db['db']['timetable']
activities = all_db['db']['activities']

for user in users:
    if not session.query(User).get(user['id']):
        user_db = User(
            surname=user['surname'],
            name=user['name'],
            age=user['age'],
            email=user['email'],
            hashed_password=user['hashed_password'],
            id=user['id'],
            modified_date=pars_str_to_date(user['modified_date']),
            is_varfarin=user['is_varfarin']
                        )
        session.add(user_db)

for activity in activities:
    if not session.query(Activities).get(activity['id']):
        activity_db = Activities(
            date=pars_str_to_date(activity['date']),
            name=activity['name'],
            id_user=activity['id_user'],
            id=activity['id']
                        )
        session.add(activity_db)


for timetable in timetables:
    if not session.query(Timetable).get(timetable['id']):
        timetable_db = Timetable(
            breakfast=timetable['breakfast'],
            dinner=timetable['dinner'],
            supper=timetable['supper'],
            master=timetable['master'],
            vitamin=timetable['vitamin'],
            id=timetable['id'],
            date=timetable['date'],
            is_varfarin=timetable['is_varfarin'],
            percent=timetable['percent'],
            ch_ch_date=timetable['ch_ch_date'],
            color=timetable['color'],
            summ=timetable['summ'],
            status=timetable['status']
                        )
        session.add(timetable_db)


session.commit()
