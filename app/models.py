from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import ipaddress
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime


# Place -----------------------------------------------------------------------
class City(db.Model):
    __tablename__ = 'city'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)
    streets = db.relationship('Street', backref='city', lazy='dynamic')

    def __repr__(self):
        return "<City: {}>".format(self.name)

    def as_dict(self):
        return {'id': self.id, 'text': self.name}


class Street(db.Model):
    __tablename__ = 'street'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    buildings = db.relationship('Building', backref='street', lazy='dynamic')

    def __repr__(self):
        return "<Street: {}>".format(self.name)

    def as_dict(self):
        return {'id': self.id, 'text': self.name}


class Building(db.Model):
    __tablename__ = 'building'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    street_id = db.Column(db.Integer, db.ForeignKey('street.id'))

    def __repr__(self):
        return "<Building: {}>".format(self.name)

    def as_dict(self):
        return {'id': self.id, 'text': self.name}


# Network ---------------------------------------------------------------------
class Network(db.Model):
    __tablename__ = 'network'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(50))
    svlan = db.Column(db.Integer)
    netlan = db.Column(db.BigInteger, unique=True)
    netmask = db.Column(db.Integer)
    gateway = db.Column(db.BigInteger)
    dns = db.Column(db.BigInteger)
    hosts = db.relationship('NetworkHost', backref='network', lazy='dynamic')

    @hybrid_property
    def netlan_ipv4(self):
        return str(ipaddress.IPv4Address(self.netlan))

    @netlan_ipv4.setter
    def netlan_ipv4(self, value):
        self.netlan = int(ipaddress.IPv4Address(value))

    @hybrid_property
    def gateway_ipv4(self):
        return str(ipaddress.IPv4Address(self.gateway))

    @gateway_ipv4.setter
    def gateway_ipv4(self, value):
        self.gateway = int(ipaddress.IPv4Address(value))

    @hybrid_property
    def dns_ipv4(self):
        return str(ipaddress.IPv4Address(self.dns))

    @dns_ipv4.setter
    def dns_ipv4(self, value):
        self.dns = int(ipaddress.IPv4Address(value))

    def __repr__(self):
        return "<Network: {}>".format(self.name)


class NetworkHost(db.Model):
    __tablename__ = 'networkhost'

    host = db.Column(db.BigInteger, primary_key=True)
    network_id = db.Column(db.Integer, db.ForeignKey('network.id'))
    eqptport_id = db.Column(db.Integer, db.ForeignKey('eqptport.id'))

    @hybrid_property
    def host_ipv4(self):
        return str(ipaddress.IPv4Address(self.host))

    @host_ipv4.setter
    def host_ipv4(self, value):
        self.host = int(ipaddress.IPv4Address(value))

    def __repr__(self):
        return "<Network host: {}>".format(str(ipaddress.IPv4Address(self.host)))


# Eqpt ------------------------------------------------------------------------
class EqptModel(db.Model):
    __tablename__ = 'eqptmodel'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    port_count = db.Column(db.Integer)

    eqpts = db.relationship('Eqpt', backref='eqptmodel', lazy='dynamic')

    def __repr__(self):
        return "<EqptModel: {}>".format(self.name)


class Eqpt(db.Model):
    """
    Create an Eqpt model table
    """
    __tablename__ = 'eqpt'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    building_id = db.Column(db.Integer)
    ip = db.Column(db.BigInteger)
    serial = db.Column(db.String(50))
    mac = db.Column(db.String(20))
    note = db.Column(db.String(200))
    network_id = db.Column(db.Integer)
    model_id = db.Column(db.Integer, db.ForeignKey('eqptmodel.id'))
    ports = db.relationship('EqptPort', backref='eqpt', lazy='dynamic')
    cvlan = db.Column(db.Integer)

    @hybrid_property
    def ipv4(self):
        return str(ipaddress.IPv4Address(self.ip))

    @ipv4.setter
    def ipv4(self, value):
        self.ip = int(ipaddress.IPv4Address(value))

    def __repr__(self):
        return "<EqptModel: {}>".format(self.name)


PORT_STATUS = {
    0: 'ok',
    -1: 'failing',
}


class EqptPort(db.Model):
    __tablename__ = 'eqptport'

    id = db.Column(db.Integer, primary_key=True)
    eqpt_id = db.Column(db.Integer, db.ForeignKey('eqpt.id'))
    ip = db.relationship('NetworkHost', uselist=False, backref='eqptport')
    client_on = db.relationship('Client', uselist=False, backref='eqptport')
    port = db.Column(db.Integer)
    cvlan = db.Column(db.Integer)
    status = db.Column(db.Integer)
    radius_user = db.Column(db.String(20))
    radius_pass = db.Column(db.String(20))

    def __repr__(self):
        return "<EqptPort: {}>".format(self.port)


# Service ---------------------------------------------------------------------
class Service(db.Model):
    __tablename__ = 'service'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    clients = db.relationship('Client', backref='service', lazy='dynamic')

    def __repr__(self):
        return "<Service: {}>".format(self.name)


# Client ----------------------------------------------------------------------
CLIENT_STATUS = {
    0: 'off',
    1: 'on',
    2: 'debt',
    3: 'pause',
}


class Client(db.Model):
    __tablename__ = 'client'

    id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(db.Integer)
    eqptport_id = db.Column(db.Integer, db.ForeignKey('eqptport.id'))
    fio = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    apartment = db.Column(db.String(20))
    status = db.Column(db.Integer)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    create_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())
    last_updated = db.Column(db.DateTime(timezone=True),
                             default=datetime.utcnow(),
                             onupdate=datetime.utcnow(),)
    suspension_at = db.Column(db.DateTime)
    note = db.Column(db.String(250))

    def __repr__(self):
        return "<#{0}. Client: {1}>".format(self.id, self.fio)


# Log Client ----------------------------------------------------------------------
LOG_EVENT = {
    'i': 'info',
    'e': 'error',
    'w': 'error',
}


class LogClient(db.Model):
    __tablename__ = 'log_client'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer)
    initiator_id = db.Column(db.Integer, default=0)
    username = db.Column(db.String(80))
    create_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())
    type = db.Column(db.String(1), default='i')
    event = db.Column(db.String(250))

    def __repr__(self):
        return "<Event: {}>".format(self.event)


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<#{0} .User {1}>'.format(self.id, self.username)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
