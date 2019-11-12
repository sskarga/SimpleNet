from flask import render_template
from . import home


@home.route('/')
def index():
    """
    Render the index template on the / route
    """
    return render_template('home/dashboard.html', title="Welcome")


@home.route('/about')
def about():
    """
    Render the about template on the / route
    """
    return render_template('home/index.html', title="Welcome")
