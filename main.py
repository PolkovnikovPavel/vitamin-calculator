NORM = 72.5


from flask import Flask, render_template, redirect, request, abort
from data import db_session
from data.users import User
from data.products import Products
from data.activity import Activities
from data.records import Timetable, set_color, set_status
from data.forms import RegisterForm, LoginForm
import resources.db_resource as db_resource
import resources.users_resource as users_resource
import resources.timetable_resource as timetable_resource
import interrupt

from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_restful import reqparse, abort, Api

import os
import datetime


def get_ch_ch_date(date):
    year, month, day = date.split('-')
    return f"{day}.{month}.{year}"


def get_num_of_day(date):
    year, month, day = date.split('-')
    num = int(year) * 365
    num += int(month) * 30
    if int(day) == 30:
        num += 29.5
    elif int(day) == 31:
        num += 29.9
    else:
        num += int(day)
    return num


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

    api.add_resource(timetable_resource.TimetablesResource, '/api/timetable/<int:timetable_id>')
    api.add_resource(timetable_resource.TimetablesDuplicate, '/api/timetable_duplicate/<int:timetable_id>')
    api.add_resource(timetable_resource.TimetablesListResource, '/api/timetable')

    api.add_resource(users_resource.UsersResource, '/api/users/<int:user_id>')
    api.add_resource(users_resource.UsersListResource, '/api/users')

    api.add_resource(db_resource.DBResource, '/api/db')
    api.add_resource(db_resource.DBProducts, '/api/db/products')

    session = db_session.create_session()
    list_of_products = session.query(Products).filter(
            Products.id != 0).all()
    list_of_products_with_varfarin = session.query(Products).filter(
            Products.is_varfarin == True).all()
    list_of_products_with_varfarin = list(map(lambda x: x.name, list_of_products_with_varfarin))

    port = int(os.environ.get("PORT", 5000))
    #interrupt.interrupt()   # для мониторинга сайта, чтоб не усыпал
    app.run(host='0.0.0.0', port=port)


@app.route("/")
def index():
    session = db_session.create_session()
    if current_user.is_authenticated:
        timetable = session.query(Timetable).filter(Timetable.master == current_user.id).all()
    else:
        timetable = []

    timetable.sort(key=lambda x: get_num_of_day(x.date), reverse=True)
    if len(timetable) > 7:
        timetable = timetable[:7]

    activity('main menu')
    return render_template("index.html", timetable=timetable,
                           current_user=current_user, title='Журнал')


@app.route('/timetable_delete/<int:id>')
@login_required
def timetable_delete(id):
    session = db_session.create_session()
    timetable = session.query(Timetable).filter(Timetable.id == id,
                        (Timetable.master == current_user.id)).first()
    if timetable:
        session.delete(timetable)
        session.commit()
        activity(f'delete timetable, id - {timetable.id}')
    else:
        abort(404)
    return redirect('/')


@app.route('/password-change')
def password_change():
    return render_template("in_developing.html")


@app.route('/timetable_duplicate/<int:id>')
@login_required
def duplicate_timetable(id):
    if not current_user.is_authenticated:
        return redirect('/')

    session = db_session.create_session()
    timetable_old = session.query(Timetable).filter(Timetable.id == id,
                                (Timetable.master == current_user.id)).first()

    if not timetable_old:
        abort(404)

    date = datetime.datetime.now()
    date = f'{date.year}-{str(date.month).rjust(2, "0")}-{date.day}'
    ch_ch_date = get_ch_ch_date(date)

    timetable_new = Timetable(
        date=date,
        ch_ch_date=ch_ch_date,
        percent=timetable_old.percent,
        vitamin=timetable_old.vitamin,
        is_varfarin=timetable_old.is_varfarin,
        master=timetable_old.master,
        color=timetable_old.color,
        summ=timetable_old.summ,
        breakfast=timetable_old.breakfast,
        dinner=timetable_old.dinner,
        supper=timetable_old.supper,
        status=timetable_old.status,
        all_products=timetable_old.all_products,
        all_products_varfarin=timetable_old.all_products_varfarin
    )

    session.add(timetable_new)
    session.commit()
    activity(f'duplicate timetable with id={timetable_old.id} to id={timetable_new.id}')

    return redirect('/')


@app.route('/look_timetable/<int:id>', methods=['GET', 'POST'])
@login_required
def look_timetable(id):
    if not current_user.is_authenticated:
        return redirect('/')

    session = db_session.create_session()
    timetable = session.query(Timetable).filter(Timetable.id == id,
                                (Timetable.master == current_user.id)).first()
    if request.method == "GET":
        result_breakfast = timetable.breakfast
        result_dinner = timetable.dinner
        result_supper = timetable.supper
        result_breakfast_varfarin = []
        result_dinner_varfarin = []
        result_supper_varfarin = []
        percents_breakfast = []
        percents_dinner = []
        percents_supper = []

        list_of_prod_varf = []
        date = timetable.date

        for result in result_breakfast:
            text = ' ('.join(result[0].split(' (')[:-1])

            if text in list_of_products_with_varfarin:
                result_breakfast_varfarin.append(True)
                list_of_prod_varf.append(text)
            else:
                result_breakfast_varfarin.append(False)
            product = session.query(Products).filter(
                Products.name == text).first()
            num = float(str(product.vitamin).replace(',', '.')) / 100 * int(
                result[1]) * 100 / NORM
            percents_breakfast.append(int(num * 100) / 100)

        for result in result_dinner:
            text = ' ('.join(result[0].split(' (')[:-1])

            if text in list_of_products_with_varfarin:
                result_dinner_varfarin.append(True)
                list_of_prod_varf.append(text)
            else:
                result_dinner_varfarin.append(False)
            product = session.query(Products).filter(
                Products.name == text).first()
            num = float(str(product.vitamin).replace(',', '.')) / 100 * int(
                result[1]) * 100 / NORM
            percents_dinner.append(int(num * 100) / 100)

        for result in result_supper:
            text = ' ('.join(result[0].split(' (')[:-1])

            if text in list_of_products_with_varfarin:
                result_dinner_varfarin.append(True)
                list_of_prod_varf.append(text)
            else:
                result_dinner_varfarin.append(False)
            product = session.query(Products).filter(
                Products.name == text).first()
            num = float(str(product.vitamin).replace(',', '.')) / 100 * int(
                result[1]) * 100 / NORM
            percents_supper.append(int(num * 100) / 100)

        values = [result_breakfast, result_dinner, result_supper,
                  len(result_breakfast), len(result_dinner), len(result_supper),
                  result_breakfast_varfarin, result_dinner_varfarin, result_supper_varfarin,
                  percents_breakfast, percents_dinner, percents_supper]

        result = (True, timetable.color, timetable.percent, timetable.vitamin,
                  timetable.status, timetable.is_varfarin,
                  list_of_prod_varf, timetable.summ)

        return render_template("look_timetable.html", values=values, result=result,
                               title='Просмотр расписания продуктов', date=date)

    else:
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
        result_breakfast_varfarin = []
        result_dinner_varfarin = []
        result_supper_varfarin = []
        list_of_prod_varf = []

        for result in result_breakfast:
            if ' ('.join(result[0].split(' (')[:-1]) in list_of_products_with_varfarin:
                result_breakfast_varfarin.append(True)
                list_of_prod_varf.append(' ('.join(result[0].split(' (')[:-1]))
            else:
                result_breakfast_varfarin.append(False)
        for result in result_dinner:
            if ' ('.join(result[0].split(' (')[:-1]) in list_of_products_with_varfarin:
                result_dinner_varfarin.append(True)
                list_of_prod_varf.append(' ('.join(result[0].split(' (')[:-1]))
            else:
                result_dinner_varfarin.append(False)
        for result in result_supper:
            if ' ('.join(result[0].split(' (')[:-1]) in list_of_products_with_varfarin:
                result_supper_varfarin.append(True)
                list_of_prod_varf.append(' ('.join(result[0].split(' (')[:-1]))
            else:
                result_supper_varfarin.append(False)

        date=timetable.date

        values = [result_breakfast, result_dinner, result_supper,
                  result_breakfast_varfarin, result_dinner_varfarin,
                  result_supper_varfarin]
        products = list(map(lambda x: (f'{x.name} ({x.vitamin}мк.гр/100гр)',
                                       x.name in list_of_products_with_varfarin),
                            list_of_products))
        products.sort()

        result = (True, timetable.color, timetable.percent, timetable.vitamin,
                  timetable.status, timetable.is_varfarin,
                  list_of_prod_varf, timetable.summ)

        return render_template("timetable.html", values=values, products=products,
                               title='Внесение продуктов', date=date, result=result)

    else:
        result_breakfast = []
        result_dinner = []
        result_supper = []
        result_breakfast_varfarin = []
        result_dinner_varfarin = []
        result_supper_varfarin = []
        is_varfarin = False
        all_products = []
        list_of_prod_varf = []
        summ = 0

        for i in range(1, 101):
            try:
                data = (request.form[
                            f'product_1_{i}'],
                        request.form[f'count_1_{i}'])
            except:
                break
            name = ' ('.join(data[0].split(' (')[:-1])
            vitamin = float(str(session.query(Products).filter(
                Products.name == name).first().vitamin).replace(',', '.'))

            if name in list_of_products_with_varfarin:
                is_varfarin = True
                list_of_prod_varf.append(name)
                result_breakfast_varfarin.append(True)
            else:
                result_breakfast_varfarin.append(False)

            result_breakfast.append(data)
            all_products.append(f"{name}({data[1]}гр - {round(vitamin*int(data[1])/100, 1)}мк.г)")
            summ += int(data[1])

        for i in range(1, 101):
            try:
                data = (request.form[
                            f'product_2_{i}'],
                        request.form[f'count_2_{i}'])
            except:
                break
            name = ' ('.join(data[0].split(' (')[:-1])
            vitamin = float(str(session.query(Products).filter(
                Products.name == name).first().vitamin).replace(',', '.'))

            if name in list_of_products_with_varfarin:
                is_varfarin = True
                list_of_prod_varf.append(name)
                result_dinner_varfarin.append(True)
            else:
                result_dinner_varfarin.append(False)

            result_dinner.append(data)
            all_products.append(f"{name}({data[1]}гр - {round(vitamin*int(data[1])/100, 1)}мк.г)")
            summ += int(data[1])

        for i in range(1, 101):
            try:
                data = (request.form[
                            f'product_3_{i}'],
                        request.form[f'count_3_{i}'])
            except:
                break
            name = ' ('.join(data[0].split(' (')[:-1])
            vitamin = float(str(session.query(Products).filter(
                Products.name == name).first().vitamin).replace(',', '.'))

            if name in list_of_products_with_varfarin:
                is_varfarin = True
                list_of_prod_varf.append(name)
                result_supper_varfarin.append(True)
            else:
                result_supper_varfarin.append(False)

            result_supper.append(data)
            all_products.append(f"{name}({data[1]}гр - {round(vitamin*int(data[1])/100, 1)}мк.г)")
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
        color = set_color(percent)
        status = set_status(percent)

        mno = request.form['mno']
        varfarin = request.form['varf']

        date = request.form['date']
        if date == '':
            date = datetime.datetime.now()
            date = f'{date.year}-{str(date.month).rjust(2, "0")}-{str(date.day).rjust(2, "0")}'
        ch_ch_date = get_ch_ch_date(date)

        timetable.date = date
        timetable.ch_ch_date = ch_ch_date
        timetable.percent = percent
        timetable.vitamin = vitamin
        timetable.is_varfarin = is_varfarin
        timetable.color = color
        timetable.status = status
        timetable.summ = summ
        timetable.breakfast = result_breakfast
        timetable.dinner = result_dinner
        timetable.supper = result_supper
        timetable.all_products = ', '.join(all_products)
        timetable.all_products_varfarin = ',  '.join(list_of_prod_varf)
        timetable.mno = mno
        timetable.varfarin = varfarin

        session.commit()

        if 'complete' in request.form:
            activity(f'chang timetable id - {timetable.id}')
            return redirect('/')

        if 'add_button_1' in request.form:
            result_breakfast.append(('Выбрать ()', 0))
        if 'add_button_2' in request.form:
            result_dinner.append(('Выбрать ()', 0))
        if 'add_button_3' in request.form:
            result_supper.append(('Выбрать ()', 0))

        values = [result_breakfast, result_dinner, result_supper,
                  result_breakfast_varfarin, result_dinner_varfarin, result_supper_varfarin]
        products = list(map(lambda x: (f'{x.name} ({x.vitamin}мк.гр/100гр)',
                                       x.name in list_of_products_with_varfarin),
                            list_of_products))
        products.sort()
        result = (True, color, percent, vitamin, status, is_varfarin, list_of_prod_varf, summ)

        return render_template("timetable.html", values=values, title='Внесение продуктов',
                               date=date, products=products, result=result)


@app.route('/timetable')
@login_required
def add_timetable():
    if not current_user.is_authenticated:
        return redirect('/')

    session = db_session.create_session()

    activity('main timetable')

    date = datetime.datetime.now()
    date = f'{date.year}-{str(date.month).rjust(2, "0")}-{date.day}'
    ch_ch_date = get_ch_ch_date(date)
    color = set_color(0)
    status = set_status(0)

    timetable = Timetable(
        date=date,
        ch_ch_date=ch_ch_date,
        percent=0,
        vitamin=0,
        is_varfarin=False,
        master=current_user.id,
        color=color,
        status=status,
        summ=0,
        breakfast=[],
        dinner=[],
        supper=[],
        all_products='Не выбрано',
        all_products_varfarin='',
        mno='0',
        varfarin='0'
    )

    session.add(timetable)
    session.commit()

    return redirect(f'/timetable/{timetable.id}')


@app.route('/timetable_without_regist', methods=['GET', 'POST'])
def timetable_without_regist():
    session = db_session.create_session()
    result = False

    if request.method == "GET":
        activity('calculation used without registration')
        result_breakfast = []
        result_dinner = []
        result_supper = []
        result_breakfast_varfarin = []
        result_dinner_varfarin = []
        result_supper_varfarin = []

        for result in result_breakfast:
            if ' ('.join(result[0].split(' (')[:-1]) in list_of_products_with_varfarin:
                result_breakfast_varfarin.append(True)
            else:
                result_breakfast_varfarin.append(False)
        for result in result_dinner:
            if ' ('.join(result[0].split(' (')[:-1]) in list_of_products_with_varfarin:
                result_dinner_varfarin.append(True)
            else:
                result_dinner_varfarin.append(False)
        for result in result_supper:
            if ' ('.join(result[0].split(' (')[:-1]) in list_of_products_with_varfarin:
                result_supper_varfarin.append(True)
            else:
                result_supper_varfarin.append(False)

        values = [result_breakfast, result_dinner, result_supper,
                  result_breakfast_varfarin, result_dinner_varfarin,
                  result_supper_varfarin]
        products = list(map(lambda x: (f'{x.name} ({x.vitamin}мк.гр/100гр)',
                                       x.name in list_of_products_with_varfarin),
                            list_of_products))
        products.sort()

        return render_template("timetable_without_regist.html", values=values, products=products,
                               title='Подсчёт витамина К', result=result)

    else:
        result_breakfast = []
        result_dinner = []
        result_supper = []
        result_breakfast_varfarin = []
        result_dinner_varfarin = []
        result_supper_varfarin = []
        is_varfarin = False
        list_of_prod_varf = []
        summ = 0

        for i in range(1, 101):
            try:
                data = (request.form[
                            f'product_1_{i}'],
                        request.form[f'count_1_{i}'])
            except:
                break
            if ' ('.join(data[0].split(' (')[:-1]) in list_of_products_with_varfarin:
                is_varfarin = True
                list_of_prod_varf.append(' ('.join(data[0].split(' (')[:-1]))
                result_breakfast_varfarin.append(True)
            else:
                result_breakfast_varfarin.append(False)

            result_breakfast.append(data)
            summ += int(data[1])

        for i in range(1, 101):
            try:
                data = (request.form[
                            f'product_2_{i}'],
                        request.form[f'count_2_{i}'])
            except:
                break
            if ' ('.join(data[0].split(' (')[:-1]) in list_of_products_with_varfarin:
                is_varfarin = True
                list_of_prod_varf.append(' ('.join(data[0].split(' (')[:-1]))
                result_dinner_varfarin.append(True)
            else:
                result_dinner_varfarin.append(False)

            result_dinner.append(data)
            summ += int(data[1])

        for i in range(1, 101):
            try:
                data = (request.form[
                            f'product_3_{i}'],
                        request.form[f'count_3_{i}'])
            except:
                break
            if ' ('.join(data[0].split(' (')[:-1]) in list_of_products_with_varfarin:
                is_varfarin = True
                list_of_prod_varf.append(' ('.join(data[0].split(' (')[:-1]))
                result_supper_varfarin.append(True)
            else:
                result_supper_varfarin.append(False)

            result_supper.append(data)
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

        vitamin = int(vitamin * 1000) / 1000
        percent = int((vitamin / NORM * 10000) + 0.5) / 100
        color = set_color(percent)
        status = set_status(percent)
        result = (True, color, percent, vitamin, status, is_varfarin, list_of_prod_varf, summ)

        if 'add_button_1' in request.form:
            result_breakfast.append(('Выбрать ()', 0))
        if 'add_button_2' in request.form:
            result_dinner.append(('Выбрать ()', 0))
        if 'add_button_3' in request.form:
            result_supper.append(('Выбрать ()', 0))

        values = [result_breakfast, result_dinner, result_supper,
                  result_breakfast_varfarin, result_dinner_varfarin, result_supper_varfarin]
        products = list(map(lambda x: (f'{x.name} ({x.vitamin}мк.гр/100гр)',
                                       x.name in list_of_products_with_varfarin),
                            list_of_products))
        products.sort()

        return render_template("timetable_without_regist.html", values=values, title='Подсчёт витамина К',
                               products=products, result=result)


@app.route('/what_is_the_calculator')
def what_is_the_calculator():
    activity(f'What is the calculator')
    return render_template('what_is_the_calculator.html', title='Калькулятор для чего нужен')


@app.route('/about_the_project')
def about_the_project():
    activity(f'About the project')
    return render_template('about_the_project.html', title='О проекте')


@app.route("/developers")
def developers():
    activity(f'To developers')
    return render_template('to_developers.html', title='To developers')


@app.route("/monitoring")
def monitoring():
    return render_template("in_developing.html")


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
def register():
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
