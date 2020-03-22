NORM = 50


from flask import Flask, render_template, redirect, request, abort, jsonify, make_response
from data import db_session
from data.users import User
from data.products import Products
from data.records import Timetable, set_color
# import users_resource


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DecimalField, BooleanField
from wtforms.validators import DataRequired, NumberRange
from wtforms.fields.html5 import EmailField
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_restful import reqparse, abort, Api

import os
import datetime


class JobsForm(FlaskForm):   # изменить под рассписание
    title = StringField('Заголовок задания', validators=[DataRequired()])
    team_leader = DecimalField('Коммандир команды id', validators=[
        NumberRange(min=1, message='Должн быть записан id цыфрами')])
    work_size = DecimalField('Объем работы в часах', validators=[
        NumberRange(min=1, message='Должно быть записанно цыфрами в часах')])
    collaborators = StringField('Участники', validators=[DataRequired()])
    is_finished = BooleanField("Завершино")
    submit = SubmitField('Применить')


class RegisterForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    surname = StringField('фамилия пользователя', validators=[DataRequired()])
    age = DecimalField('возрост', validators=[
        NumberRange(min=16, max=199, message='Должно быть записанно цыфрами от 16 до 199')])
    email = EmailField('Почта', validators=[DataRequired()])
    is_varfarin = BooleanField('Вы принимаете Варфарин')
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('завершить')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=1)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


def main():
    db_session.global_init("db/vitamin_calculator.sqlite")
    # api.add_resource(users_resource.UsersListResource, '/api/v2/users')
    # api.add_resource(users_resource.UsersResource, '/api/v2/users/<int:user_id>')
    # api.add_resource(jobs_resource.JobsListResource, '/api/v2/jobs')
    # api.add_resource(jobs_resource.JobsResource, '/api/v2/jobs/<int:job_id>')
    # api.add_resource(users_resource.DBResource, '/api/v2/db')

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


@app.route("/")
def index():
    session = db_session.create_session()
    if current_user.is_authenticated:
        timetable = session.query(Timetable).filter(Timetable.master == current_user.id).all()
    else:
        timetable = []
    if len(timetable) > 7:
        timetable = timetable[-7:]
    users = session.query(User).all()
    return render_template("index.html", timetable=timetable,
                           current_user=current_user, title='Журнал')


@app.route('/jobs_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def jobs_delete(id):
    session = db_session.create_session()
    jobs = session.query(Jobs).filter(Jobs.id == id,
                        ((Jobs.creator == current_user.id) | (current_user.id == 1))).first()
    if jobs:
        session.delete(jobs)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/jobs/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_jobs(id):
    form = JobsForm()
    if request.method == "GET":
        session = db_session.create_session()
        jobs = session.query(Jobs).filter(Jobs.id == id,
                    ((Jobs.creator == current_user.id) | (current_user.id == 1))).first()
        if jobs:
            form.title.data = jobs.job
            form.team_leader.data = jobs.team_leader
            form.work_size.data = int(jobs.work_size)
            form.collaborators.data = jobs.collaborators
            form.is_finished.data = jobs.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()

        if not session.query(User).filter(User.id == int(form.team_leader.data)).first():
            return render_template('jobs.html', title='Редактирование работы',
                                   form=form,
                                   message='несуществующий id коммандира')

        job = session.query(Jobs).filter(Jobs.id == id,
                    ((Jobs.creator == current_user.id) | (current_user.id == 1))).first()
        if job:
            job.job = form.title.data
            job.team_leader = int(form.team_leader.data)
            job.work_size = int(form.work_size.data)
            job.collaborators = form.collaborators.data
            job.is_finished = form.is_finished.data

            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('jobs.html', title='Редактирование работы', form=form)


@app.route('/jobs',  methods=['GET', 'POST'])
@login_required
def add_jobs():
    form = JobsForm()
    if form.validate_on_submit():
        session = db_session.create_session()

        if not session.query(User).filter(User.id == int(form.team_leader.data)).first():
            return render_template('jobs.html', title='Добавление работы',
                                   form=form,
                                   message='несуществующий id коммандира')
        job = Jobs()
        job.job = form.title.data
        job.team_leader = int(form.team_leader.data)
        job.work_size = int(form.work_size.data)
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data
        job.creator = current_user.id

        date_start = datetime.datetime.now()
        date_end = datetime.datetime.now() + datetime.timedelta(hours=int(form.work_size.data))
        job.start_date = date_start
        job.end_date = date_end

        session.add(job)
        session.commit()
        return redirect('/')
    return render_template('jobs.html', title='Добавление работы',
                           form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            user.is_active = True
            login_user(user, remember=form.remember_me.data)
            current_user.is_active = True
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            age=int(form.age.data),
            email=form.email.data,
            is_varfarin=form.is_varfarin.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        # сразу войти в систему
        user.is_active = True
        login_user(user, remember=False)
        current_user.is_active = True
        return redirect('/')   # возврат на главное меню
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    main()
