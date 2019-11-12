from flask import Blueprint

eqpt_bp = Blueprint('eqpt_bp', __name__,
                    url_prefix='/equipment')

from . import views
