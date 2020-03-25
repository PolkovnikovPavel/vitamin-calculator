NORM = 50


from flask import Flask, render_template, redirect, request, abort, jsonify, make_response, url_for
from data import db_session
from data.users import User
from data.products import Products
from data.activity import Activities
from data.records import Timetable, set_color
import users_resource


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DecimalField, BooleanField
from wtforms.validators import DataRequired, NumberRange
from wtforms.fields.html5 import EmailField
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_restful import reqparse, abort, Api

import os
import datetime


class TimetableForm(FlaskForm):
    submit = SubmitField('Завершить')


class RegisterForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    surname = StringField('фамилия пользователя', validators=[DataRequired()])
    age = DecimalField('возрост', validators=[
        NumberRange(min=16, max=199, message='Должно быть записанно цыфрами от 16 до 199')])
    email = EmailField('Почта', validators=[DataRequired()])
    is_varfarin = BooleanField('Вы принимаете Варфарин')
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Завершить')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


def get_ch_ch_date(date):
    year, month, day = date.split('-')
    return f"{day}.{month}.{year}"


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
    global list_of_products, list_of_products_with_varfarin
    db_session.global_init("db/vitamin_calculator.sqlite")
    # api.add_resource(users_resource.UsersListResource, '/api/v2/users')
    # api.add_resource(users_resource.UsersResource, '/api/v2/users/<int:user_id>')
    # api.add_resource(jobs_resource.JobsListResource, '/api/v2/jobs')
    # api.add_resource(jobs_resource.JobsResource, '/api/v2/jobs/<int:job_id>')
    api.add_resource(users_resource.DBResource, '/api/db')

    session = db_session.create_session()
    list_of_products = session.query(Products).filter(
            Products.id != 0).all()
    list_of_products_with_varfarin = session.query(Products).filter(
            Products.is_varfarin == True).all()
    list_of_products_with_varfarin = list(map(lambda x: x.name, list_of_products_with_varfarin))

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
    activity('main menu')
    return render_template("index.html", timetable=timetable,
                           current_user=current_user, title='Журнал')


@app.route('/timetable_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def timetable_delete(id):
    session = db_session.create_session()
    timetable = session.query(Timetable).filter(Timetable.id == id,
                        (Timetable.master == current_user.id)).first()
    if timetable:
        session.delete(timetable)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/timetable/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_timetable(id):
    if not current_user.is_authenticated:
        return redirect('/')

    session = db_session.create_session()
    timetable = session.query(Timetable).filter(Timetable.id == id,
                                (Timetable.master == current_user.id)).first()
    if request.method == "GET":
        result_breakfast = timetable.breakfast
        result_dinner = timetable.dinner
        result_supper = timetable.supper
        date=timetable.date

        values = [result_breakfast, result_dinner, result_supper]
        products = list(map(lambda x: f'{x.name} ({x.vitamin}мл.гр/100гр)', list_of_products))
        products.sort()

        return render_template("timetable.html", values=values,
                               title='Внесение блюд', date=date)

    else:
        result_breakfast = []
        result_dinner = []
        result_supper = []
        is_varfarin = False

        for i in range(1, 101):
            try:
                data = (request.form[
                            f'product_1_{i}'],
                        request.form[f'count_1_{i}'])
            except:
                break
            if ''.join(data[0].split(' (')[:-1]) in list_of_products_with_varfarin:
                is_varfarin = True
            result_breakfast.append(data)

        for i in range(1, 101):
            try:
                data = (request.form[
                            f'product_2_{i}'],
                        request.form[f'count_2_{i}'])
            except:
                break
            if ''.join(data[0].split(' (')[:-1]) in list_of_products_with_varfarin:
                is_varfarin = True
            result_dinner.append(data)

        for i in range(1, 101):
            try:
                data = (request.form[
                            f'product_3_{i}'],
                        request.form[f'count_3_{i}'])
            except:
                break
            if ''.join(data[0].split(' (')[:-1]) in list_of_products_with_varfarin:
                is_varfarin = True
            result_supper.append(data)

        vitamin = sum(map(lambda x: float(str(session.query(Products).filter(
            Products.name == ''.join(x[0].split(' (')[:-1])
                    ).first().vitamin).replace(',', '.')) / 100 * int(x[1]), result_breakfast))

        vitamin += sum(map(lambda x: float(str(session.query(Products).filter(
            Products.name == ''.join(x[0].split(' (')[:-1])
                    ).first().vitamin).replace(',', '.')) / 100 * int(x[1]), result_dinner))

        vitamin += sum(map(lambda x: float(str(session.query(Products).filter(
            Products.name == ''.join(x[0].split(' (')[:-1])
                    ).first().vitamin).replace(',', '.')) / 100 * int(x[1]), result_supper))

        vitamin = int(vitamin * 1000) / 1000
        percent = int((vitamin / NORM * 10000) + 0.5) / 100
        color = set_color(percent)

        date = request.form['date']
        if date == '':
            date = datetime.datetime.now()
            date = f'{date.year}-{str(date.month).rjust(2, "0")}-{date.day}'
        ch_ch_date = get_ch_ch_date(date)

        timetable.date = date
        timetable.ch_ch_date = ch_ch_date
        timetable.percent = percent
        timetable.vitamin = vitamin
        timetable.is_varfarin = is_varfarin
        timetable.color = color
        timetable.breakfast = result_breakfast
        timetable.dinner = result_dinner
        timetable.supper = result_supper

        session.commit()

        if 'complete' in request.form:
            activity(f'chang timetable id - {timetable.id}')
            return redirect('/')

        if 'add_button_1' in request.form:
            result_breakfast.append(('Выбрать', 0))
        if 'add_button_2' in request.form:
            result_dinner.append(('Выбрать', 0))
        if 'add_button_3' in request.form:
            result_supper.append(('Выбрать', 0))

        values = [result_breakfast, result_dinner, result_supper]
        products = list(map(lambda x: f'{x.name} ({x.vitamin}мл.гр/100гр)', list_of_products))
        products.sort()

        return render_template("timetable.html", values=values, title='Внесение блюд',
                               date=date, products=products)


@app.route('/timetable',  methods=['GET', 'POST'])
@login_required
def add_timetable():
    if not current_user.is_authenticated:
        return redirect('/')

    session = db_session.create_session()
    if request.method == 'GET':
        values = [[], [], []]
        activity('main timetable')

        date = datetime.datetime.now()
        date = f'{date.year}-{str(date.month).rjust(2, "0")}-{date.day}'
        ch_ch_date = get_ch_ch_date(date)
        color = set_color(0)

        timetable = Timetable(
            date=date,
            ch_ch_date=ch_ch_date,
            percent=0,
            vitamin=0,
            is_varfarin=False,
            master=current_user.id,
            color=color,
            breakfast=[],
            dinner=[],
            supper=[]
        )

        session.add(timetable)
        session.commit()

        return render_template("timetable.html", values=values, title='Внесение блюд', date=date)
    else:
        result_breakfast = []
        result_dinner = []
        result_supper = []
        is_varfarin = False

        for i in range(1, 101):
            try:
                data = (request.form[
                            f'product_1_{i}'],
                        request.form[f'count_1_{i}'])
            except:
                break
            if ''.join(data[0].split(' (')[:-1]) in list_of_products_with_varfarin:
                is_varfarin = True
            result_breakfast.append(data)

        for i in range(1, 101):
            try:
                data = (request.form[
                            f'product_2_{i}'],
                        request.form[f'count_2_{i}'])
            except:
                break
            if ''.join(data[0].split(' (')[:-1]) in list_of_products_with_varfarin:
                is_varfarin = True
            result_dinner.append(data)

        for i in range(1, 101):
            try:
                data = (request.form[
                            f'product_3_{i}'],
                        request.form[f'count_3_{i}'])
            except:
                break
            if ''.join(data[0].split(' (')[:-1]) in list_of_products_with_varfarin:
                is_varfarin = True
            result_supper.append(data)

        vitamin = sum(map(lambda x: float(str(session.query(Products).filter(
                    Products.name == ''.join(x[0].split(' (')[:-1])
                        ).first().vitamin).replace(',', '.')) / 100 * int(x[1]), result_breakfast))

        vitamin += sum(map(lambda x: float(str(session.query(Products).filter(
            Products.name == ''.join(x[0].split(' (')[:-1])

                        ).first().vitamin).replace(',', '.')) / 100 * int(x[1]), result_dinner))
        vitamin += sum(map(lambda x: float(str(session.query(Products).filter(
            Products.name == ''.join(x[0].split(' (')[:-1])
                        ).first().vitamin).replace(',', '.')) / 100 * int(x[1]), result_supper))

        vitamin = int(vitamin * 1000) / 1000
        percent = int((vitamin / NORM * 10000) + 0.5) / 100
        color = set_color(percent)

        date = request.form['date']
        if date == '':
            date = datetime.datetime.now()
            date = f'{date.year}-{str(date.month).rjust(2, "0")}-{date.day}'
        ch_ch_date = get_ch_ch_date(date)

        timetable = session.query(Timetable).filter(Timetable.master == current_user.id).all()
        timetable = timetable[-1]

        timetable.date = date
        timetable.ch_ch_date = ch_ch_date
        timetable.percent = percent
        timetable.vitamin = vitamin
        timetable.is_varfarin = is_varfarin
        timetable.color = color
        timetable.breakfast = result_breakfast
        timetable.dinner = result_dinner
        timetable.supper = result_supper

        session.commit()

        if 'complete' in request.form:
            activity(f'add new timetable id - {timetable.id}')
            return redirect('/')

        if 'add_button_1' in request.form:
            result_breakfast.append(('Выбрать', 0))
        if 'add_button_2' in request.form:
            result_dinner.append(('Выбрать', 0))
        if 'add_button_3' in request.form:
            result_supper.append(('Выбрать', 0))

        values = [result_breakfast, result_dinner, result_supper]
        products = list(map(lambda x: f'{x.name} ({x.vitamin}мл.гр/100гр)', list_of_products))
        products.sort()

        return render_template("timetable.html", values=values, title='Внесение блюд',
                               date=date, products=products)


@app.route('/logout')
@login_required
def logout():
    activity(f'Sign Out')
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

            activity(f'logging in with email="{form.email.data}"')
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

        activity(f'new register email"{form.email.data}" name="{form.name.data} {form.surname.data}"')
        return redirect('/')   # возврат на главное меню
    return render_template('register.html', title='Регистрация', form=form)


def activity(name=''):
    session = db_session.create_session()
    if current_user.is_authenticated:
        user = current_user.id
    else:
        user = 0

    active = Activities(
        name=name,
        id_user=user
    )
    session.add(active)
    session.commit()


if __name__ == '__main__':
    main()
