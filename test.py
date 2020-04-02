from requests import get, post, put, delete
from data import db_session
import json


x = get('http://127.0.0.1:5000/api/users/1',
           json={'master': 1,
                 'password': '1',
                 'date': '2020-03-30',
                 'breakfast': '[["Гречневая каша рассыпчатая (0.0мл.гр/100гр)", "25"],["Чеснок (1,7мл.гр/100гр)", "15"]]',
                 'dinner': '[["Абрикосы сушеные с косточкой (урюк) (0.0мл.гр/100гр)", "777"]]',
                 'supper': '[["Гречневая каша рассыпчатая (0.0мл.гр/100гр)", "300"]]'}).json()

print(json.dumps(x, sort_keys=True, indent=4, ensure_ascii=False))
