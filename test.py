from requests import get, post, put, delete
from data import db_session


print(put('http://127.0.0.1:5000/api/timetable_duplicate/8',
           json={'master': 1,
                 'password': '1'}).json())

