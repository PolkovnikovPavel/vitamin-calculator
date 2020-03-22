from requests import get
from data import db_session
from data.users import User
from data.Jobs import Jobs
import datetime


def pars_str_to_date(date_str):
    days, time = date_str.split(' ')
    year, month, day = days.split('-')
    hours, minutes = time.split(':')

    date = datetime.datetime(int(year), int(month), int(day), int(hours),
                             int(minutes), 0)
    return date


way = 'https://colonization-mars.herokuapp.com/'
db_session.global_init("db/mars_explorer.sqlite")
session = db_session.create_session()


all_db = get(f'{way}/api/v2/db').json()

users = all_db['db']['users']
jobs = all_db['db']['jobs']

for user in users:
    if not session.query(User).get(user['id']):
        user_db = User(
            surname=user['surname'],
            name=user['name'],
            age=user['age'],
            position=user['position'],
            speciality=user['speciality'],
            address=user['address'],
            email=user['email'],
            hashed_password=user['hashed_password'],
            id=user['id'],
            modified_date=pars_str_to_date(user['modified_date'])
                        )
        session.add(user_db)

for job in jobs:
    if not session.query(Jobs).get(job['id']):
        job_db = Jobs(
            job=job['job'],
            team_leader=job['team_leader'],
            work_size=job['work_size'],
            collaborators=job['collaborators'],
            start_date=pars_str_to_date(job['start_date']),
            end_date=pars_str_to_date(job['end_date']),
            is_finished=job['is_finished'],
            creator=job['creator'],
            id=job['id']
                        )
        session.add(job_db)


session.commit()
