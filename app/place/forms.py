from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class PlaceForm(FlaskForm):
    name = StringField('Название', [
        Length(min=5, max=100),
        DataRequired(),
    ])
    submit = SubmitField('Сохранить')
