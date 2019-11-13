from functools import wraps
from flask import url_for, redirect, request, flash, session
from datetime import datetime
from flask_login import current_user
from app.models import User
from app import db


def check_user_admin():
    if User.query.filter_by(username='admin').first() is None:
        user = User(
            name='admin',
            username='admin',
            is_admin=True,
            is_active=True)
        user.set_password('admin')
        db.session.add(user)
        db.session.commit()


def auth_before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    else:
        if request.endpoint != 'auth.login' \
                and request.endpoint != 'static' \
                and request.endpoint != '_debug_toolbar.static':
            return redirect(url_for('auth.login'))


def requires_admin(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin:
            flash('У вас нет доступа к этой странице. Сожалею!', 'danger')
            return_url = request.referrer or '/'
            return redirect(return_url)
        return func(*args, **kwargs)
    return decorated_view
