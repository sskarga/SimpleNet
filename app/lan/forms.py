from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import Length, IPAddress, NumberRange


class LanCreateForm(FlaskForm):
    name = StringField('Название сети', default='Сеть 1', validators=[
        Length(min=5, max=50),
    ])

    svlan = IntegerField(
        'S-Vlan',
        default=1,
        validators=[
            NumberRange(
                min=1,
                max=3999,
                message=u'Вне диапазона доступных VLAN (1-3999)',
            ),
        ])

    netlan_ipv4 = StringField('Сеть', default='192.168.0.0', validators=[
        IPAddress(ipv4=True, ipv6=False, message='Неверный IP адрес'),
    ],)

    netmask = SelectField(
        u'Маска',
        default=24,
        coerce=int,
        choices=[
            (24, u'/24 (255.255.255.0) - 254 Хоста'),
            (23, u'/23 (255.255.254.0) - 510 Хостов'),
            (22, u'/22 (255.255.252.0) - 1022 Хоста'),
            (21, u'/21 (255.255.248.0) - 2046 Хоста'),
            (20, u'/20 (255.255.240.0) - 4094 Хоста'),
        ])

    gateway_ipv4 = StringField('Шлюз', default='192.168.0.1', validators=[
        IPAddress(ipv4=True, ipv6=False, message='Неверный IP адрес'),
    ])

    dns_ipv4 = StringField('DNS', default='192.168.0.1', validators=[
        IPAddress(ipv4=True, ipv6=False, message='Неверный IP адрес'),
    ])

    submit = SubmitField('Сохранить')
