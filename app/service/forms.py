from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length


class ServiceForm(FlaskForm):
    name = StringField('Название', [
        Length(min=5, max=50),
        DataRequired(),
    ])
    submit = SubmitField('Сохранить')


class RadGpForm(FlaskForm):
    attribute = StringField('Атрибут', [
        Length(min=1, max=64),
        DataRequired(),
    ])

    op = SelectField(
        u'Оператор',
        default='=',
        choices=[
            ('=', '='),
            ('==', '=='),
            (':=', ':='),
            ('+=', '+='),
            ('!=', '!='),
            ('>', '>'),
            ('>=', '>='),
            ('<', '<'),
            ('<=', '<='),
            ('=~', '=~'),
            ('!~', '!~'),
            ('=*', '=*'),
            ('!*', '!*'),
        ])

    value = StringField('Значение', [
        Length(min=1, max=253),
        DataRequired(),
    ])

    submit = SubmitField('Сохранить')
