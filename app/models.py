import ipaddress
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login

from sqlalchemy.dialects import postgresql, mysql, sqlite
from sqlalchemy import BigInteger, Integer

UnsignedIntType = Integer()
UnsignedIntType = UnsignedIntType.with_variant(mysql.INTEGER(unsigned=True), 'mysql')

BigIntegerType = BigInteger()
BigIntegerType = BigIntegerType.with_variant(postgresql.BIGINT(), 'postgresql')
BigIntegerType = BigIntegerType.with_variant(mysql.BIGINT(), 'mysql')
BigIntegerType = BigIntegerType.with_variant(sqlite.INTEGER(), 'sqlite')

# TO-DO: server_default=text('now()')
"""
from pytz import timezone
from datetime import datetime

UTC = timezone('UTC')

def time_now():
    return datetime.now(UTC)
    
Column(u'timestamp', TIMESTAMP(timezone=True), primary_key=False, nullable=False, default=time_now),
"""

# Place -----------------------------------------------------------------------
class City(db.Model):
    __tablename__ = 'city'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default='', index=True)
    streets = db.relationship('Street', backref='city', lazy='dynamic')

    def __repr__(self):
        return "<City: {}>".format(self.name)

    def as_dict(self):
        return {'id': self.id, 'text': self.name}


class Street(db.Model):
    __tablename__ = 'street'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default='', index=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    buildings = db.relationship('Building', backref='street', lazy='dynamic')

    def __repr__(self):
        return "<Street: {}>".format(self.name)

    def as_dict(self):
        return {'id': self.id, 'text': self.name}


class Building(db.Model):
    __tablename__ = 'building'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default='', index=True)
    street_id = db.Column(db.Integer, db.ForeignKey('street.id'))

    def __repr__(self):
        return "<Building: {}>".format(self.name)

    def as_dict(self):
        return {'id': self.id, 'text': self.name}


# Network ---------------------------------------------------------------------
class Network(db.Model):
    __tablename__ = 'network'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, default='')
    svlan = db.Column(db.Integer, nullable=False, default='')
    netlan = db.Column(UnsignedIntType, unique=True, nullable=False, default='')
    netmask = db.Column(db.Integer)
    gateway = db.Column(UnsignedIntType)
    dns = db.Column(UnsignedIntType)
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

    host = db.Column(UnsignedIntType, primary_key=True, autoincrement=True)
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
    name = db.Column(db.String(50), nullable=False, default='', index=True)
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
    name = db.Column(db.String(50), nullable=False, default='')
    building_id = db.Column(db.Integer, nullable=False, default='', index=True)
    ip = db.Column(UnsignedIntType, nullable=False, default='', index=True)
    serial = db.Column(db.String(50), nullable=False, default='')
    mac = db.Column(db.String(20), nullable=False, default='', index=True)
    note = db.Column(db.String(200))
    network_id = db.Column(db.Integer, nullable=False, default='', index=True)
    model_id = db.Column(db.Integer, db.ForeignKey('eqptmodel.id'))
    ports = db.relationship('EqptPort', backref='eqpt', lazy='dynamic')
    cvlan = db.Column(db.Integer, nullable=False, default='')

    @hybrid_property
    def ipv4(self):
        return str(ipaddress.IPv4Address(self.ip))

    @ipv4.setter
    def ipv4(self, value):
        self.ip = int(ipaddress.IPv4Address(value))

    def __repr__(self):
        return "<EqptModel: {}>".format(self.name)


PORT_STATUS = {
    'ok': 0,
    'failing': -1,
}


class EqptPort(db.Model):
    __tablename__ = 'eqptport'

    id = db.Column(db.Integer, primary_key=True)
    eqpt_id = db.Column(db.Integer, db.ForeignKey('eqpt.id'))
    ip = db.relationship('NetworkHost', uselist=False, backref='eqptport')
    client_on = db.relationship('Client', uselist=False, backref='eqptport')
    port = db.Column(db.Integer, nullable=False, default='')
    cvlan = db.Column(db.Integer, nullable=False, default='', index=True)
    status = db.Column(db.Integer, nullable=False, default='')
    radius_user = db.Column(db.String(64), nullable=False, default='', index=True)
    radius_pass = db.Column(db.String(64), nullable=False, default='')

    def __repr__(self):
        return "<EqptPort: {}>".format(self.port)


# Service ---------------------------------------------------------------------
class Service(db.Model):
    __tablename__ = 'service'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, default='', index=True)
    clients = db.relationship('Client', backref='service', lazy='dynamic')

    def __repr__(self):
        return "<Service: {}>".format(self.name)


# Client ----------------------------------------------------------------------
CLIENT_STATUS = {
    'off': 0,
    'on': 1,
    'debt': 2,
    'pause' : 3,
}


class Client(db.Model):
    __tablename__ = 'client'

    id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(db.Integer, nullable=False, default='', index=True)
    eqptport_id = db.Column(db.Integer, db.ForeignKey('eqptport.id'))
    fio = db.Column(db.String(100), nullable=False, default='', index=True)
    phone = db.Column(db.String(50), nullable=False, default='', index=True)
    apartment = db.Column(db.String(20), nullable=False, default='')
    status = db.Column(db.Integer, nullable=False, default='', index=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    create_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())
    last_updated = db.Column(db.DateTime(timezone=True),
                             default=datetime.utcnow(),
                             onupdate=datetime.utcnow(),)
    suspension_at = db.Column(db.DateTime(timezone=True))
    note = db.Column(db.String(250))

    def __repr__(self):
        return "<#{0}. Client: {1}>".format(self.id, self.fio)


# Log Client ----------------------------------------------------------------------
LOG_EVENT = {
    'info': 'i',
    'error': 'e',
    'warning': 'w',
}


class LogClient(db.Model):
    __tablename__ = 'log_client'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, nullable=False, default='', index=True)
    initiator_id = db.Column(db.Integer, nullable=False, default=0, index=True)
    username = db.Column(db.String(80))
    create_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())
    type = db.Column(db.String(1), default='i')
    event = db.Column(db.String(250))

    def __repr__(self):
        return "<Event: {}>".format(self.event)


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, default='')
    username = db.Column(db.String(80), unique=True, nullable=False, default='', index=True)
    password_hash = db.Column(db.String(200), nullable=False, default='')
    is_active = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<#{0} .User {1}>'.format(self.id, self.username)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# FreeRADIUS SQL Module ------------------------------------------------------
# Database schema for SQL rlm_sql module

class RadCheck(db.Model):
    __tablename__ = 'radcheck'

    id = db.Column(UnsignedIntType, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True, server_default='', index=True)
    attribute = db.Column(db.String(64), nullable=False, server_default='')
    op = db.Column(db.String(2), nullable=False, server_default='==')
    value = db.Column(db.String(253), nullable=False, server_default='')

    def __repr__(self):
        return '<#{0}. RadCheck username {1}>'.format(self.id, self.username)


class RadGroupCheck(db.Model):
    __tablename__ = 'radgroupcheck'

    id = db.Column(UnsignedIntType, primary_key=True)
    groupname = db.Column(db.String(64), nullable=False, server_default='', index=True)
    attribute = db.Column(db.String(64), nullable=False, server_default='')
    op = db.Column(db.String(2), nullable=False, server_default='==')
    value = db.Column(db.String(253), nullable=False, server_default='')

    def __repr__(self):
        return '<#{0}. RadGroupCheck groupname {1}>'.format(self.id, self.groupname)


class RadGroupReply(db.Model):
    __tablename__ = 'radgroupreply'

    id = db.Column(UnsignedIntType, primary_key=True)
    groupname = db.Column(db.String(64), nullable=False, server_default='', index=True)
    attribute = db.Column(db.String(64), nullable=False, server_default='')
    op = db.Column(db.String(2), nullable=False, server_default='==')
    value = db.Column(db.String(253), nullable=False, server_default='')

    def __repr__(self):
        return '<#{0}. RadGroupReply groupname {1}>'.format(self.id, self.groupname)


class RadReply(db.Model):
    __tablename__ = 'radreply'

    id = db.Column(UnsignedIntType, primary_key=True)
    username = db.Column(db.String(64), nullable=False, server_default='', index=True)
    attribute = db.Column(db.String(64), nullable=False, server_default='')
    op = db.Column(db.String(2), nullable=False, server_default='==')
    value = db.Column(db.String(253), nullable=False, server_default='')

    def __repr__(self):
        return '<#{0}. RadReply username {1}>'.format(self.id, self.username)


class RadUserGroup(db.Model):
    __tablename__ = 'radusergroup'

    id = db.Column(UnsignedIntType, primary_key=True)
    username = db.Column(db.String(64), nullable=False, server_default='', index=True)
    groupname = db.Column(db.String(64), nullable=False, server_default='')
    priority = db.Column(db.Integer, nullable=False, server_default='1')

    def __repr__(self):
        return '<#{0}. RadUserGroup groupname {1}>'.format(self.id, self.username)


class RadPostAuth(db.Model):
    __tablename__ = 'radpostauth'

    id = db.Column(UnsignedIntType, primary_key=True)
    username = db.Column(db.String(64), nullable=False, server_default='', index=True)
    radpass = db.Column('pass', db.String(64), nullable=False, server_default='')
    reply = db.Column(db.String(32), nullable=False, server_default='')
    authdate = db.Column(db.TIMESTAMP, nullable=False,
                         server_default=func.utc_timestamp(), server_onupdate=func.utc_timestamp()
                         # nullable=False, default=func.utc_timestamp(), onupdate=func.utc_timestamp()
                         # server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
                         )

    def __repr__(self):
        return '<#{0}. RadPostAuth username {1}>'.format(self.id, self.username)


class RadAcct(db.Model):
    __tablename__ = 'radacct'

    radacctid = db.Column(BigIntegerType, primary_key=True)
    acctsessionid = db.Column(db.String(64), nullable=False, server_default='', index=True)
    acctuniqueid = db.Column(db.String(32), nullable=False, unique=True, server_default='')
    username = db.Column(db.String(64), nullable=False, server_default='', index=True)
    realm = db.Column(db.String(64), server_default='')
    nasipaddress = db.Column(db.String(15), nullable=False, server_default='', index=True)
    nasportid = db.Column(db.String(15))
    nasporttype = db.Column(db.String(32))
    acctstarttime = db.Column(db.DateTime, index=True)
    acctupdatetime = db.Column(db.DateTime)
    acctstoptime = db.Column(db.DateTime, index=True)
    acctinterval = db.Column(BigIntegerType, index=True)
    acctsessiontime = db.Column(BigIntegerType, index=True)
    acctauthentic = db.Column(db.String(32), server_default='')
    connectinfo_start = db.Column(db.String(50), server_default='')
    connectinfo_stop = db.Column(db.String(50), server_default='')
    acctinputoctets = db.Column(BigIntegerType)
    acctoutputoctets = db.Column(BigIntegerType)
    calledstationid = db.Column(db.String(50), nullable=False, server_default='')
    callingstationid = db.Column(db.String(50), nullable=False, server_default='')
    acctterminatecause = db.Column(db.String(32), nullable=False, server_default='')
    servicetype = db.Column(db.String(32))

    framedprotocol = db.Column(db.String(32))
    framedipaddress = db.Column(db.String(15), nullable=False, server_default='', index=True)
    framedipv6address = db.Column(db.String(45), nullable=False, server_default='', index=True)
    framedipv6prefix = db.Column(db.String(45), nullable=False, server_default='', index=True)
    framedinterfaceid = db.Column(db.String(44), nullable=False, server_default='', index=True)
    delegatedipv6prefix = db.Column(db.String(45), nullable=False, server_default='', index=True)

    def __repr__(self):
        return '<RadAcct {0}>'.format(self.radacctid)


class RadNas(db.Model):
    __tablename__ = 'nas'

    id = db.Column(db.Integer, primary_key=True)
    nasname = db.Column(db.String(128), nullable=False, server_default='', index=True)
    shortname = db.Column(db.String(32), server_default='')
    nastype = db.Column('type', db.String(30), server_default='other')
    ports = db.Column(db.Integer())
    secret = db.Column(db.String(60), nullable=False, server_default='secret')
    server = db.Column(db.String(64))
    community = db.Column(db.String(50))
    description = db.Column(db.String(200), server_default='RADIUS Client')

    def __repr__(self):
        return '<Nas {0}>'.format(self.nasname)
