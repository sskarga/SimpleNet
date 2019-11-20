# Copyright © 2019 Skarga Sergey. All rights reserved.

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_moment import Moment
from flask_debugtoolbar import DebugToolbarExtension

# db variable initialization
db = SQLAlchemy()
toolbar = DebugToolbarExtension()

login = LoginManager()
login.login_view = 'auth.login'


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    db.init_app(app)
    toolbar.init_app(app)

    login.init_app(app)
    moment = Moment(app)
    migrate = Migrate(app, db)

    from app import models
    from app.auth_helper import check_user_admin, auth_before_request

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import auth_bp as auth_route
    app.register_blueprint(auth_route)

    from app.home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    from app.api import api_bp as api_route
    app.register_blueprint(api_route)

    from app.place import place_bp as place_route
    app.register_blueprint(place_route)

    from app.client import client_bp as client_route
    app.register_blueprint(client_route)

    from app.eqpt import eqpt_bp as eqpt_route
    app.register_blueprint(eqpt_route)

    from app.lan import lan_bp as lan_route
    app.register_blueprint(lan_route)

    from app.service import bp as service_route
    app.register_blueprint(service_route)

    if not app.debug and not app.testing:

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/simplenet.log',
                                           maxBytes=1000000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('SimpleNet startup')

    app.before_first_request(check_user_admin)
    app.before_request(auth_before_request)

    return app


