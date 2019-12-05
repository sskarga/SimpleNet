"""App configuration."""
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config(object):
    """Set Flask configuration vars from .env file."""

    # General Config
    SECRET_KEY = environ.get('SECRET_KEY')
    FLASK_ENV = environ.get('FLASK_ENV')

    # Debug
    DEBUG = environ.get('DEBUG', False)

    CSRF_ENABLED = environ.get('CSRF_ENABLED', True)
    WTF_CSRF_SECRET_KEY = environ.get('WTF_CSRF_SECRET_KEY')

    # SQL ALCHEMY
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URI') or \
        'sqlite:///' + path.join(basedir, 'app.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BOOTSTRAP_SERVE_LOCAL = True

    PAGINATE_PAGE = 25

    # Radius config
    RADIUS_ADDRESS = environ.get('RADIUS_ADDRESS', '127.0.0.1')
    RADIUS_SECRET = environ.get('RADIUS_SECRET', b"Kah3choteereethiejeimaeziecumi")
    RADIUS_TIMEOUT = 30

    # Static Assets
    # STATIC_FOLDER = environ.get('STATIC_FOLDER')
    # TEMPLATES_FOLDER = environ.get('TEMPLATES_FOLDER')
