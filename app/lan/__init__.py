from flask import Blueprint

lan_bp = Blueprint('lan_bp', __name__,
                   url_prefix='/lan')

from . import views
