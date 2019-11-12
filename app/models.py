from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import ipaddress
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func


# Place -----------------------------------------------------------------------
class City(db.Model):
    """
    Create an City table
    """
    __tablename__ = 'city'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)
    streets = db.relationship('Street', backref='city', lazy='dynamic')

    def __repr__(self):
        return "<City: {}>".format(self.name)

    def as_dict(self):
        return {self.id: self.name}


class Street(db.Model):
    """
    Create an Street table
    """
    __tablename__ = 'street'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    buildings = db.relationship('Building', backref='street', lazy='dynamic')

    def __repr__(self):
        return "<Street: {}>".format(self.name)

    def as_dict(self):
        return {self.id: self.name}


class Building(db.Model):
    """
    Create an Building table
    """
    __tablename__ = 'building'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    street_id = db.Column(db.Integer, db.ForeignKey('street.id'))

    def __repr__(self):
        return "<Building: {}>".format(self.name)

    def as_dict(self):
        return {self.id: self.name}


# Network ---------------------------------------------------------------------
class Network(db.Model):
    """
    Create an Network table
    """
    __tablename__ = 'network'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    svlan = db.Column(db.Integer)
    netlan = db.Column(db.Integer, unique=True)
    netmask = db.Column(db.Integer)
    gateway = db.Column(db.Integer)
    dns = db.Column(db.Integer)

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
    """
    Create an NetworkHost table
    """
    __tablename__ = 'networkhost'

    host = db.Column(db.Integer, primary_key=True)
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
    """
    Create an Eqpt model table
    """
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
    ip = db.Column(db.Integer)
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


class EqptPort(db.Model):
    """
    Create an Eqpt model table
    """
    __tablename__ = 'eqptport'

    id = db.Column(db.Integer, primary_key=True)
    eqpt_id = db.Column(db.Integer, db.ForeignKey('eqpt.id'))
    ip = db.relationship('NetworkHost', uselist=False, backref='eqptport')
    client_on = db.relationship('Client', uselist=False, backref='eqptport')
    port = db.Column(db.Integer)
    cvlan = db.Column(db.Integer)
    """
    status:
        not_work = -1
        not_use = 0
        client = 1
        line = 2
    """
    status = db.Column(db.Integer)

    radius_user = db.Column(db.String(20))
    radius_pass = db.Column(db.String(20))

    def __repr__(self):
        return "<EqptPort: {}>".format(self.port)


# Service ---------------------------------------------------------------------
class Service(db.Model):
    __tablename__ = 'service'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    radius_grup_name = db.Column(db.String(20))

    clients = db.relationship('Client', backref='service', lazy='dynamic')

    def __repr__(self):
        return "<Service: {}>".format(self.name)


# Client ----------------------------------------------------------------------
class Client(db.Model):
    __tablename__ = 'client'

    id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(db.Integer)
    eqptport_id = db.Column(db.Integer, db.ForeignKey('eqptport.id'))

    fio = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    apartment = db.Column(db.String(20))

    """
    status:
        off = 0
        on = 1
        credit = 2
        freeze = 3
    """
    status = db.Column(db.Integer)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))

    create_at = db.Column(db.DateTime(timezone=True), default=func.now())
    last_updated = db.Column(db.DateTime(timezone=True),
                             default=func.now(),
                             onupdate=func.now(),)
    suspension_at = db.Column(db.DateTime)
    note = db.Column(db.String(250))

    def __repr__(self):
        return "<Client: {}>".format(self.fio)


# Log Client ----------------------------------------------------------------------
class LogClient(db.Model):
    __tablename__ = 'log_client'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer)
    initiator_id = db.Column(db.Integer, default=0)
    username = db.Column(db.String(80))
    create_at = db.Column(db.DateTime(timezone=True), default=func.now())
    """
        i - info
        e - error
        w - warning
    """
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
    last_seen = db.Column(db.DateTime, default=func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
