"""App configuration."""
from os import environ, path

basedir = path.abspath(path.dirname(__file__))


class Config:
    """Set Flask configuration vars from .env file."""

    # General Config
    SECRET_KEY = environ.get('SECRET_KEY')
    FLASK_ENV = environ.get('FLASK_ENV')

    # Debug
    DEBUG = environ.get('DEBUG', False)

    CSRF_ENABLED = environ.get('CSRF_ENABLED', True)
    WTF_CSRF_SECRET_KEY = environ.get('WTF_CSRF_SECRET_KEY')

    # SQL ALCHEMY
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI') or \
        'sqlite:///' + path.join(basedir, 'app.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BOOTSTRAP_SERVE_LOCAL = True

    PAGINATE_PAGE = int(environ.get('PAGINATE_PAGE', 25))

    # Static Assets
    # STATIC_FOLDER = environ.get('STATIC_FOLDER')
    # TEMPLATES_FOLDER = environ.get('TEMPLATES_FOLDER')
