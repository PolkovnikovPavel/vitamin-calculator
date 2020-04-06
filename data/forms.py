from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DecimalField, BooleanField
from wtforms.validators import DataRequired, NumberRange
from wtforms.fields.html5 import EmailField


class RegisterForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    surname = StringField('фамилия пользователя', validators=[DataRequired()])
    age = DecimalField('возраст', validators=[
        NumberRange(min=16, max=199, message='Должно быть записанно цифрами от 16 до 199')])
    email = EmailField('Почта', validators=[DataRequired()])
    is_varfarin = BooleanField('Вы принимаете Варфарин')
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Продолжить')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')