from flask import Blueprint

bp = Blueprint('service', __name__,
               url_prefix='/service')

from . import views
