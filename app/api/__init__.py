from flask import Blueprint

api_bp = Blueprint('api_bp', __name__,
                   url_prefix='/api/v1.0')

from . import views
