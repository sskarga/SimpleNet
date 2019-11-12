from flask import Blueprint

client_bp = Blueprint('client_bp', __name__,
                      url_prefix='/client')

"""
client_bp = Blueprint('client_bp', __name__,
                      template_folder='templates',
                      static_folder='static',
                      url_prefix='/client')
"""

from . import views
