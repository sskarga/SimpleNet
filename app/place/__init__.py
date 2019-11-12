from flask import Blueprint

place_bp = Blueprint('place_bp', __name__,
                     url_prefix='/place')

from . import views
