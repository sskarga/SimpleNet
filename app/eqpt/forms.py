from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, HiddenField, SubmitField
from wtforms.validators import Length, IPAddress, NumberRange, MacAddress, ValidationError


class EqptCreateForm(FlaskForm):

    model_id = SelectField(u'Модель', coerce=int)

    name = StringField('Имя узла', default='Узел 1', validators=[
        Length(min=2, max=50),
    ])

    ipv4 = StringField('IP адрес узла', default='0.0.0.0', validators=[
        IPAddress(ipv4=True, ipv6=False, message='Неверный IP адрес'),
    ],)

    def validate_ipv4(form, field):
        if field.data == "0.0.0.0":
            raise ValidationError('Неверный IP адрес')

    serial = StringField('Серийный номер', default='1234', validators=[
        Length(min=5, max=50),
    ])

    mac = StringField('MAC адресс', default='00:00:00:00:00:00', validators=[
        MacAddress(message='Неверный MAC адрес'),
    ],)

    def validate_mac(form, field):
        if field.data == "00:00:00:00:00:00":
            raise ValidationError('Неверный MAC адрес')

    network_id = SelectField(u'IP сеть', coerce=int)

    cvlan = IntegerField(u'Клиентский vlan',
                         default=1,
                         validators=[
                             NumberRange(min=1,
                                         max=3999,
                                         message=u'Vlan в не диапазона (1-4000)')
                         ])

    submit = SubmitField('Сохранить')


class EqptEditForm(FlaskForm):

    model_id = SelectField(u'Модель', coerce=int)
    name = StringField('Имя узла', default='Узел 1', validators=[
        Length(min=2, max=50),
    ])

    ipv4 = StringField('IP адрес узла', default='0.0.0.0', validators=[
        IPAddress(ipv4=True, ipv6=False, message='Неверный IP адрес'),
    ], )

    def validate_ipv4(form, field):
        if field.data == "0.0.0.0":
            raise ValidationError('Неверный IP адрес')

    serial = StringField('Серийный номер', default='1234', validators=[
        Length(min=5, max=50),
    ])

    mac = StringField('MAC адресс', default='00:00:00:00:00:00', validators=[
        MacAddress(message='Неверный MAC адрес'),
    ], )

    def validate_mac(form, field):
        if field.data == "00:00:00:00:00:00":
            raise ValidationError('Неверный MAC адрес')

    network_id = SelectField(u'IP сеть', coerce=int)

    cvlan = IntegerField(u'Клиентский vlan',
                         default=1,
                         validators=[
                             NumberRange(min=1,
                                         max=3999,
                                         message=u'Vlan в не диапазона (1-4000)')
                         ])

    submit = SubmitField('Сохранить')


class EqptPortCreateForm(FlaskForm):

    eqpt_id = HiddenField("eqptId")
    svlan = HiddenField("svlan")
    eqptcvlan = HiddenField("eqptcvlan")
    mac = HiddenField("mac")

    ipv4 = StringField('IP адрес узла', default='0.0.0.0', validators=[
        IPAddress(ipv4=True, ipv6=False, message='Неверный IP адрес'),
    ], )

    def validate_ipv4(form, field):
        if field.data == "0.0.0.0":
            raise ValidationError('Неверный IP адрес')

    port = SelectField(u'№ порта', coerce=int)

    cvlan = IntegerField(u'Клиентский vlan',
                         default=1,
                         validators=[
                             NumberRange(min=1,
                                         max=4000,
                                         message=u'Vlan в не диапазона (1-4000)')
                         ])

    status = SelectField(u'Состояние порта', coerce=int)

    radius_user = StringField('Radius-User', validators=[
        Length(min=3, max=20),
    ])
    radius_pass = StringField('Radius-Password', validators=[
        Length(min=3, max=20),
    ])

    submit = SubmitField('Сохранить')


class EqptPortEditForm(FlaskForm):

    svlan = HiddenField("svlan")
    eqptcvlan = HiddenField("eqptcvlan")
    mac = HiddenField("mac")
    port = HiddenField("port")

    ipv4 = StringField('IP адрес узла', default='0.0.0.0', validators=[
        IPAddress(ipv4=True, ipv6=False, message='Неверный IP адрес'),
    ], )

    def validate_ipv4(form, field):
        if field.data == "0.0.0.0":
            raise ValidationError('Неверный IP адрес')

    cvlan = IntegerField(u'Клиентский vlan',
                         default=1,
                         validators=[
                             NumberRange(min=1,
                                         max=4000,
                                         message=u'Vlan в не диапазона (1-4000)')
                         ])

    status = SelectField(u'Состояние порта', coerce=int)

    radius_user = StringField('Radius-User', validators=[
        Length(min=3, max=20),
    ])
    radius_pass = StringField('Radius-Password', validators=[
        Length(min=3, max=20),
    ])

    submit = SubmitField('Сохранить')


class EqptNoteForm(FlaskForm):
    note = StringField('Примечание', validators=[
        Length(min=0, max=199),
    ])

    submit = SubmitField('Сохранить')


class EqptModelForm(FlaskForm):
    name = StringField('Модель', validators=[
        Length(min=5, max=50),
    ])

    port_count = IntegerField(u'Кол. портов для клиентов',
                         default=1,
                         validators=[
                             NumberRange(min=1,
                                         max=50,
                                         message=u'Количество портов для абонентов в не диапазона (1-50)')
                         ])

    submit = SubmitField('Сохранить')
