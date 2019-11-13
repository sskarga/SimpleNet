from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, InputRequired


class ClientCreateForm(FlaskForm):

    fio = StringField('Фамилия И.О.', [
        Length(min=5, max=100),
    ])

    phone = StringField('Телефон', [
        Length(min=5, max=50),
    ])

    apartment = StringField('Квартира/Офис', [
        Length(min=1, max=20),
    ])

    service_id = SelectField(u'Услуга', coerce=int)
    status = SelectField(u'Состояние', coerce=int)

    submit = SubmitField('Сохранить')


class ClientPersonalInfoForm(FlaskForm):
    fio = StringField('Фамилия И.О.', [
        Length(min=5, max=100),
    ])

    phone = StringField('Телефон', [
        Length(min=5, max=50),
    ])

    submit = SubmitField('Сохранить')


class ClientServiceInfoForm(FlaskForm):
    service_id = SelectField(u'Услуга', coerce=int)
    status = SelectField(u'Состояние', coerce=int)
    submit = SubmitField('Сохранить')


class ClientAddressForm(FlaskForm):

    building_id = HiddenField("building_id")

    apartment = StringField('Квартира/Офис', [
        Length(min=1, max=20),
    ])
    submit = SubmitField('Сохранить')


class ClientPersonalNoteForm(FlaskForm):
    note = StringField('Примечание', validators=[
        Length(min=0, max=249),
    ])
    submit = SubmitField('Сохранить')