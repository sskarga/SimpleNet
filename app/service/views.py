from flask import render_template, redirect, flash, url_for
from app import db
from app.models import Service
from .forms import ServiceForm
from . import bp
from app.auth_helper import requires_admin


@bp.route('/')
def show_service():
    services = Service.query.order_by('name')
    return render_template('service/index.html', services=services)


@bp.route('/create', methods=['GET', 'POST'])
@requires_admin
def service_create():
    form = ServiceForm()

    if form.validate_on_submit():
        srv = Service(name=form.name.data)
        db.session.add(srv)
        db.session.commit()
        flash('Новый сервис добавлен.', 'success')
        return redirect(url_for('.show_service'))

    return render_template(
        'service/form.html',
        title='Добавления сервиса',
        form=form,
    )


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@requires_admin
def service_edit(id):
    srv = Service.query.get(id)
    form = ServiceForm()

    if form.validate_on_submit():
        srv.name = form.name.data
        db.session.commit()
        flash('Cервис обновлен.', 'success')
        return redirect(url_for('.show_service'))

    form.name.data = srv.name

    return render_template(
        'service/form.html',
        title='Обновление сервиса',
        form=form,
    )


@bp.route('/delete/<int:id>')
@requires_admin
def service_delete(id):
    srv = Service.query.get(id)
    db.session.delete(srv)
    db.session.commit()
    flash('Удален', 'success')
    return redirect(url_for('.show_service'))
