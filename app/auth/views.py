from flask import render_template, url_for, redirect, request, flash
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User
from app.auth.forms import LoginForm, RegistrationForm, EditForm, ResetPasswordForm
from app import db
from app.auth_helper import requires_admin
from . import auth_bp


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неправильный логин или пароль')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home.index')

        flash('Доброго дня, {0}!'.format(user.name), 'success')
        return redirect(next_page)

    return render_template('auth/login.html', title='Sign In', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/')
@requires_admin
def show_user():
    users = User.query.all()
    return render_template('auth/index.html', users=users)


@auth_bp.route('/register', methods=['GET', 'POST'])
@requires_admin
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            username=form.username.data,
            is_admin=form.is_admin.data,
            is_active=form.is_active.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Новый пользователь зарегистрирован', 'success')
        return redirect(url_for('auth.show_user'))

    return render_template('auth/form.html', title='Регистрация нового пользователя',
                           form=form)


@auth_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@requires_admin
def user_edit(id):
    user = User.query.get(id)
    form = EditForm()

    if form.validate_on_submit():

        if user.username != 'admin':
            user.username = form.username.data
            user.is_admin = form.is_admin.data
            user.is_active = form.is_active.data

        user.name = form.name.data
        db.session.commit()
        flash('Данные пользователя обновлены', 'success')
        return redirect(url_for('auth.show_user'))

    form.name.data = user.name
    form.username.data = user.username
    form.is_admin.data = user.is_admin
    form.is_active.data = user.is_active

    return render_template('auth/form.html', title='Редактирование пользователя',
                           form=form)


@auth_bp.route('/password/<int:id>', methods=['GET', 'POST'])
@requires_admin
def user_password(id):
    user = User.query.get(id)

    form = ResetPasswordForm()

    if form.validate_on_submit():
        user.set_password('admin')
        db.session.commit()
        flash('Пароль пользователя изменен', 'success')
        return redirect(url_for('auth.show_user'))

    return render_template('auth/form.html', title='Новый пароль',
                           form=form)


@auth_bp.route('/delete/<int:id>', methods=['GET'])
@requires_admin
def user_delete(id):
    del_user = User.query.get(id)

    if del_user.username != 'admin':
        db.session.delete(del_user)
        db.session.commit()
        flash('Пользователь удален.', 'success')
    else:
        flash('Пользователя admin нельзя удалить.', 'danger')
    return redirect(url_for('auth.show_user'))
