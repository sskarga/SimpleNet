# -*- encoding: utf-8 -*-
import unittest
from app import create_app, db
from app.models import City, Street, Building, Network, NetworkHost, EqptModel, Eqpt, EqptPort,\
    PORT_STATUS, Service, CLIENT_STATUS, Client, LOG_EVENT, LogClient, User,\
    RadCheck, RadGroupCheck, RadGroupReply, RadReply, RadUserGroup
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class ModelCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user(self):
        """
        Testing Model User
        :return:
        """
        user = User(
            name='admin',
            username='admin',
            is_admin=True,
            is_active=True,
        )
        user.set_password('qwerty1235453admin')
        db.session.add(user)
        db.session.commit()

        user_db = User.query.filter_by(name='admin').first()

        self.assertIsNotNone(user_db, msg='User not found in db')
        self.assertFalse(user_db.check_password('password'), msg='Invalid password passed verification')
        self.assertTrue(user_db.check_password('qwerty1235453admin'), msg='Wrong password')


if __name__ == '__main__':
    unittest.main(verbosity=2)
