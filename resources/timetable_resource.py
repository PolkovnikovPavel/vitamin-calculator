from flask_restful import abort, Resource, reqparse
from flask import jsonify
from data import db_session
from data.users import User
from data.records import Timetable, set_color, set_status
from data.products import Products
import json
import datetime

NORM = 72.5


def get_ch_ch_date(date):
    year, month, day = date.split('-')
    return f"{day}.{month}.{year}"


list_of_parameters_timetable = ['id', 'date', 'breakfast', 'summ', 'status',
                                    'dinner', 'supper', 'master', 'all_products',
                                'is_varfarin', 'vitamin', 'percent',
                                'all_products_varfarin', 'color', 'ch_ch_date']

parser_delete = reqparse.RequestParser()
parser_delete.add_argument('password', required=True)
parser_delete.add_argument('master', required=True, type=int)

parser_change = reqparse.RequestParser()
parser_change.add_argument('password', required=True)
parser_change.add_argument('master', required=True, type=int)
parser_change.add_argument('date', required=True)
parser_change.add_argument('breakfast', required=True)
parser_change.add_argument('dinner', required=True)
parser_change.add_argument('supper', required=True)

parser_add = reqparse.RequestParser()
parser_add.add_argument('password', required=True)
parser_add.add_argument('date', required=True)
parser_add.add_argument('breakfast', required=True)
parser_add.add_argument('dinner', required=True)
parser_add.add_argument('supper', required=True)
parser_add.add_argument('master', required=True, type=int)


class TimetablesResource(Resource):
    def get(self, timetable_id):
        abort_if_timetable_not_found(timetable_id)
        session = db_session.create_session()
        timetable = session.query(Timetable).get(timetable_id)
        return jsonify({'timetable': timetable.to_dict(only=(list_of_parameters_timetable))})

    def put(self, timetable_id):
        args = parser_change.parse_args()
        abort_if_timetable_not_found(timetable_id)
        if not check_password(args['master'], args['password']):
            abort(404, message=f"incorrect password")

        breakfast, dinner, supper, vitamin, \
        percent, is_varfarin, summ, all_products, \
        list_of_prod_varf = get_all_data(args['breakfast'], args['dinner'], args['supper'])

        session = db_session.create_session()
        timetable = session.query(Timetable).get(timetable_id)
        if timetable.master != args['master']:
            abort(404, message=f"incorrect master, mast be {timetable.master}")

        timetable.date = args['date']
        timetable.breakfast = breakfast
        timetable.dinner = dinner
        timetable.supper = supper
        timetable.is_varfarin = is_varfarin
        timetable.vitamin = vitamin
        timetable.percent = percent
        timetable.summ = summ
        timetable.ch_ch_date = get_ch_ch_date(args['date'])
        timetable.status = set_status(percent)
        timetable.all_products = all_products
        timetable.all_products_varfarin = list_of_prod_varf
        timetable.color = set_color(percent)

        session.commit()
        return jsonify({'success': 'OK'})

    def delete(self, timetable_id):
        args = parser_delete.parse_args()
        abort_if_timetable_not_found(timetable_id)
        if not check_password(args['master'], args['password']):
            abort(404, message=f"incorrect password")

        session = db_session.create_session()

        timetable = session.query(Timetable).get(timetable_id)
        session.delete(timetable)
        session.commit()
        return jsonify({'success': 'OK'})


class TimetablesListResource(Resource):
    def get(self):
        session = db_session.create_session()
        timetables = session.query(Timetable).all()
        return jsonify({'timetables': [timetable.to_dict(
            only=(list_of_parameters_timetable)) for timetable in timetables]})

    def post(self):
        args = parser_add.parse_args()

        if not check_password(args['master'], args['password']):
            abort(404, message=f"incorrect password")
        breakfast, dinner, supper, vitamin,\
        percent, is_varfarin, summ, all_products,\
        list_of_prod_varf = get_all_data(args['breakfast'], args['dinner'], args['supper'])

        session = db_session.create_session()
        timetable = Timetable(
            date=args['date'],
            breakfast=breakfast,
            dinner=dinner,
            supper=supper,
            master=args['master'],
            is_varfarin=is_varfarin,
            vitamin=vitamin,
            percent=percent,
            ch_ch_date=get_ch_ch_date(args['date']),
            summ=summ,
            status=set_status(percent),
            all_products=all_products,
            all_products_varfarin=list_of_prod_varf,
            color=set_color(percent)
                   )
        session.add(timetable)
        session.commit()
        return jsonify({'success': 'OK'})


class TimetablesDuplicate(Resource):
    def put(self, timetable_id):
        args = parser_delete.parse_args()

        if not check_password(args['master'], args['password']):
            abort(404, message=f"incorrect password")
        abort_if_timetable_not_found(timetable_id)

        session = db_session.create_session()
        timetable_old = session.query(Timetable).get(timetable_id)

        if timetable_old.master != args['master']:
            abort(404, message=f"incorrect master, mast be {timetable_old.master}")

        date = datetime.datetime.now()
        date = f'{date.year}-{str(date.month).rjust(2, "0")}-{date.day}'
        ch_ch_date = get_ch_ch_date(date)

        timetable = Timetable(
            date=date,
            breakfast=timetable_old.breakfast,
            dinner=timetable_old.dinner,
            supper=timetable_old.supper,
            master=timetable_old.master,
            is_varfarin=timetable_old.is_varfarin,
            vitamin=timetable_old.vitamin,
            percent=timetable_old.percent,
            ch_ch_date=ch_ch_date,
            summ=timetable_old.summ,
            status=timetable_old.status,
            all_products=timetable_old.all_products,
            all_products_varfarin=timetable_old.all_products_varfarin,
            color=timetable_old.color
        )
        session.add(timetable)
        session.commit()

        return jsonify({'success': 'OK'})


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    users = session.query(User).get(user_id)
    if not users:
        abort(404, message=f"User {user_id} not found")


def abort_if_timetable_not_found(timetable_id):
    session = db_session.create_session()
    timetable = session.query(Timetable).get(timetable_id)
    if not timetable:
        abort(404, message=f"Timetable {timetable_id} not found")


def check_password(user_id, password):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if user:
        return user.check_password(password)
    abort(404, message=f"User {user_id} not found")


def is_json(string):
    try:
        json_object = json.loads(string)
    except ValueError:
        abort(404, message=f"{string} is not json")
    return True


def get_all_data(breakfast, dinner, supper):
    is_json(breakfast)
    is_json(dinner)
    is_json(supper)
    breakfast = json.loads(breakfast)
    dinner = json.loads(dinner)
    supper = json.loads(supper)

    session = db_session.create_session()
    list_of_products_with_varfarin = session.query(Products).filter(
        Products.is_varfarin == True).all()
    list_of_products_with_varfarin = list(
        map(lambda x: x.name, list_of_products_with_varfarin))

    result_breakfast = []
    result_dinner = []
    result_supper = []

    is_varfarin = False
    all_products = []
    list_of_prod_varf = []
    summ = 0

    for i in range(len(breakfast)):
        try:
            data = breakfast[i]
            x, y = data
            vitamin = float(str(session.query(Products).filter(
                Products.name == ' ('.join(data[0].split(' (')[:-1])
                ).first().vitamin).replace(',', '.'))
        except:
            abort(404, message=f"breakfast - incorrect format")

        data = breakfast[i]
        vitamin = float(str(session.query(Products).filter(
            Products.name == ' ('.join(data[0].split(' (')[:-1])
            ).first().vitamin).replace(',', '.'))

        if ' ('.join(data[0].split(' (')[:-1]) in list_of_products_with_varfarin:
            is_varfarin = True
            list_of_prod_varf.append(' ('.join(data[0].split(' (')[:-1]))

        result_breakfast.append(data)
        all_products.append(
            f"{' ('.join(data[0].split(' (')[:-1])}({data[1]}гр - {round(vitamin * int(data[1]) / 100, 1)}мк.г)")
        summ += int(data[1])

    for i in range(len(dinner)):
        try:
            data = dinner[i]
            x, y = data
            vitamin = float(str(session.query(Products).filter(
                Products.name == ' ('.join(data[0].split(' (')[:-1])
                ).first().vitamin).replace(',', '.'))
        except:
            abort(404, message=f"breakfast - incorrect format")

        data = dinner[i]
        vitamin = float(str(session.query(Products).filter(
            Products.name == ' ('.join(data[0].split(' (')[:-1])
            ).first().vitamin).replace(',', '.'))

        if ' ('.join(data[0].split(' (')[:-1]) in list_of_products_with_varfarin:
            is_varfarin = True
            list_of_prod_varf.append(' ('.join(data[0].split(' (')[:-1]))

        result_dinner.append(data)
        all_products.append(
            f"{' ('.join(data[0].split(' (')[:-1])}({data[1]}гр - {round(vitamin * int(data[1]) / 100, 1)}мк.г)")
        summ += int(data[1])

    for i in range(len(supper)):
        try:
            data = supper[i]
            x, y = data
            vitamin = float(str(session.query(Products).filter(
                Products.name == ' ('.join(data[0].split(' (')[:-1])
                ).first().vitamin).replace(',', '.'))
        except:
            abort(404, message=f"supper - incorrect format")

        data = supper[i]
        vitamin = float(str(session.query(Products).filter(
            Products.name == ' ('.join(data[0].split(' (')[:-1])
            ).first().vitamin).replace(',', '.'))

        if ' ('.join(data[0].split(' (')[:-1]) in list_of_products_with_varfarin:
            is_varfarin = True
            list_of_prod_varf.append(' ('.join(data[0].split(' (')[:-1]))

        result_supper.append(data)
        all_products.append(
            f"{' ('.join(data[0].split(' (')[:-1])}({data[1]}гр - {round(vitamin * int(data[1]) / 100, 1)}мк.г)")
        summ += int(data[1])

    vitamin = sum(map(lambda x: float(str(session.query(Products).filter(
        Products.name == ' ('.join(x[0].split(' (')[:-1])
        ).first().vitamin).replace(',', '.')) / 100 * int(x[1]), result_breakfast))

    vitamin += sum(map(lambda x: float(str(session.query(Products).filter(
        Products.name == ' ('.join(x[0].split(' (')[:-1])
        ).first().vitamin).replace(',', '.')) / 100 * int(x[1]), result_dinner))

    vitamin += sum(map(lambda x: float(str(session.query(Products).filter(
        Products.name == ' ('.join(x[0].split(' (')[:-1])
        ).first().vitamin).replace(',', '.')) / 100 * int(x[1]), result_supper))

    vitamin = round(vitamin, 3)
    percent = round(vitamin / NORM * 100, 2)

    all_products = ', '.join(all_products)
    list_of_prod_varf = ', '.join(list_of_prod_varf)

    return breakfast, dinner, supper, vitamin, percent, is_varfarin, summ, all_products, list_of_prod_varf
