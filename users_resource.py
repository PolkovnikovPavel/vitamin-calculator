from flask_restful import abort, Resource, reqparse
from flask import jsonify
from data import db_session
from data.users import User
from data.records import Timetable
from data.activity import Activities

import os

list_of_parameters_users = ['name', 'surname', 'age',
                                    'id', 'position', 'speciality',
                                    'address', 'email', 'modified_date']

parser_change = reqparse.RequestParser()
parser_change.add_argument('surname', required=True)
parser_change.add_argument('name', required=True)
parser_change.add_argument('age', required=True, type=int)
parser_change.add_argument('position', required=True)
parser_change.add_argument('speciality', required=True)
parser_change.add_argument('address', required=True)
parser_change.add_argument('email', required=True)

parser_add = reqparse.RequestParser()
parser_add.add_argument('surname', required=True)
parser_add.add_argument('name', required=True)
parser_add.add_argument('age', required=True, type=int)
parser_add.add_argument('position', required=True)
parser_add.add_argument('speciality', required=True)
parser_add.add_argument('address', required=True)
parser_add.add_argument('email', required=True)
parser_add.add_argument('hashed_password', required=True)


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        news = session.query(User).get(user_id)
        return jsonify({'user': news.to_dict(only=(list_of_parameters_users))})

    def put(self, user_id):
        args = parser_change.parse_args()
        session = db_session.create_session()
        news = session.query(User).get(user_id)

        news.surname = args['surname']
        news.name = args['name']
        news.age = args['age']
        news.position = args['position']
        news.speciality = args['speciality']
        news.address = args['address']
        news.email = args['email']

        session.commit()
        return jsonify({'success': 'OK'})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()

        jobs = session.query(Jobs).filter(Jobs.team_leader == user_id).all()
        for job in jobs:
            session.delete(job)

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
        user = User(
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            position=args['position'],
            speciality=args['speciality'],
            address=args['address'],
            email=args['email'],
            hashed_password=args['hashed_password']
                   )
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})


class DBResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        activities = session.query(Activities).all()
        timetables = session.query(Timetable).all()

        return jsonify({ 'db':{'users': [user.to_dict() for user in users],
                               'timetable': [timetable.to_dict() for timetable in timetables],
                               'activities': [activity.to_dict() for activity in activities]}})


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    users = session.query(User).get(user_id)
    if not users:
        abort(404, message=f"User {user_id} not found")
