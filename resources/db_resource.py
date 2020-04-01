from flask_restful import Resource
from flask import jsonify
from data import db_session
from data.users import User
from data.records import Timetable
from data.activity import Activities


class DBResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        activities = session.query(Activities).all()
        timetables = session.query(Timetable).all()

        return jsonify({ 'db':{'users': [user.to_dict() for user in users],
                               'timetable': [timetable.to_dict() for timetable in timetables],
                               'activities': [activity.to_dict() for activity in activities]}})
