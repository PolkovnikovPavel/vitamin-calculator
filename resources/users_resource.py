from flask_restful import abort, Resource, reqparse
from flask import jsonify
from data import db_session
from data.users import User
from data.records import Timetable
from data.activity import Activities

import os

list_of_parameters_users = ['name', 'surname', 'age', 'id', 'is_varfarin',
                            'email', 'modified_date']

parser_change = reqparse.RequestParser()
parser_change.add_argument('surname', required=False)
parser_change.add_argument('name', required=False)
parser_change.add_argument('age', required=False, type=int)
parser_change.add_argument('password', required=True)
parser_change.add_argument('is_varfarin', required=False)

parser_add = reqparse.RequestParser()
parser_add.add_argument('surname', required=True)
parser_add.add_argument('name', required=True)
parser_add.add_argument('age', required=True, type=int)
parser_add.add_argument('password', required=True)
parser_add.add_argument('is_varfarin', required=True, type=bool)
parser_add.add_argument('email', required=True)


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(only=(list_of_parameters_users))})

    def put(self, user_id):
        args = parser_change.parse_args()
        if not check_password(user_id, args['password']):
            abort(404, message=f"incorrect password")

        session = db_session.create_session()
        user = session.query(User).get(user_id)

        if args['surname']:
            user.surname = args['surname']
        if args['name']:
            user.surname = args['name']
        if args['age']:
            user.surname = args['age']
        if args['is_varfarin']:
            user.surname = args['is_varfarin']

        session.commit()
        return jsonify({'success': 'OK'})

    def delete(self, user_id):
        args = parser_change.parse_args()
        if not check_password(user_id, args['password']):
            abort(404, message=f"incorrect password")

        session = db_session.create_session()

        timetables = session.query(Timetable).filter(Timetable.master == user_id).all()
        for timetable in timetables:
            session.delete(timetable)

        user = session.query(User).get(user_id)
        session.delete(user)

        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [user.to_dict(
            only=(list_of_parameters_users)) for user in users]})

    def post(self):
        args = parser_add.parse_args()
        session = db_session.create_session()
        if session.query(User).filter(User.email == args['email']).first():
            abort(404, message='This user already exists')

        user = User(
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            email=args['email'],
            is_varfarin=args['is_varfarin']
        )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    users = session.query(User).get(user_id)
    if not users:
        abort(404, message=f"User {user_id} not found")


def check_password(user_id, password):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if user:
        return user.check_password(password)
    abort(404, message=f"User {user_id} not found")

