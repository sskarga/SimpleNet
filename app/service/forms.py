from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ServiceForm(FlaskForm):
    name = StringField('Название', [
        Length(min=5, max=50),
        DataRequired(),
    ])
    submit = SubmitField('Сохранить')
