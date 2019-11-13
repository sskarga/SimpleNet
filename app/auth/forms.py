from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Вход')


class RegistrationForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
                            'Повторите пароль',
                            validators=[
                                    DataRequired(),
                                    EqualTo('password')
                                ]
                            )

    is_admin = BooleanField('Администратор')
    is_active = BooleanField('Активировать учетную запись')

    submit = SubmitField('Зарегистрировать')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Этот логин уже занят, выберите другой.')


class EditForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    username = StringField('Логин', validators=[DataRequired()])
    is_admin = BooleanField('Администратор')
    is_active = BooleanField('Активировать учетную запись')

    submit = SubmitField('Сохранить')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторите пароль',
        validators=[
            DataRequired(),
            EqualTo('password')
        ]
    )

    submit = SubmitField('Сменить пароль')
