from requests import get, post, put, delete

print('1)смотрим все работы')
print(get('http://127.0.0.1:8080/api/v2/jobs').json())


print('\n2)посмотрим все данные первой работы')
print(get('http://127.0.0.1:8080/api/v2/jobs/1').json())


print('\n3)добавим новую работу')
print(post('http://127.0.0.1:8080/api/v2/jobs',
           json={'job': 'очередная работа',
                 'collaborators': '1, 2, 3',
                 'work_size': 48,
                 'team_leader': 1,
                 'is_finished': False}).json())


print('\n4)посмотрим изменения')
all_jobs = get('http://127.0.0.1:8080/api/v2/jobs').json()
print(all_jobs)


id = all_jobs['jobs'][-1]['id']
print('\n5)посмотрим все данные новой работы')
print(get(f'http://127.0.0.1:8080/api/v2/jobs/{id}').json())


print('\n6)попробуем удалить несуществующую работу')
print(delete('http://127.0.0.1:8080/api/v2/jobs/99999999999').json())


print('\n7)теперь удалим правельно недавно созданную работу')
print(delete(f'http://127.0.0.1:8080/api/v2/jobs/{id}').json())


print('\n8)попробуем теперь посмотреть все данные о новой работе')
print(get(f'http://127.0.0.1:8080/api/v2/jobs/{id}').json())


print('\n9)попробуем создать новое задание, но не передадим work_size')
print(post('http://127.0.0.1:8080/api/v2/jobs',
           json={'job': 'очередная работа',
                 'collaborators': '1, 2, 3',
                 'team_leader': 1,
                 'is_finished': False}).json())


print('\n10)изменем самую первую работу')
print(put('http://127.0.0.1:8080/api/v2/jobs/1',
           json={'job': 'первая работа(изменённая)',
                 'collaborators': '1, 2',
                 'work_size': 20,
                 'team_leader': 1,
                 'is_finished': False}).json())


print('\n11)попробуем изменить самую первую работу, но team_leader будет строкой')
print(put('http://127.0.0.1:8080/api/v2/jobs/1',
           json={'job': 'первая работа(неверная)',
                 'collaborators': '1, 2',
                 'work_size': 20,
                 'team_leader': 'капитан',
                 'is_finished': False}).json())


print('\n11)попробуем изменить самую первую работу, но team_leader будет указан неверно')
print(put('http://127.0.0.1:8080/api/v2/jobs/1',
           json={'job': 'первая работа(неверная)',
                 'collaborators': '1, 2',
                 'work_size': 20,
                 'team_leader': 999999999999,
                 'is_finished': False}).json())
