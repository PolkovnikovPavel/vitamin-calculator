from requests import get, post, put, delete
from data import db_session


print(get('http://127.0.0.1:5000/api/db/products',
           json={'master': 1,
                 'password': '1'}).json())

