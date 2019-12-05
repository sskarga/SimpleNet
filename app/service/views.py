from flask import render_template, redirect, flash, url_for
from app import db
from app.models import Service, RadGroupReply
from .forms import ServiceForm, RadGpForm
from . import bp
from app.auth_helper import requires_admin
from app.freeradius import DEFAULT_SERVICE

SERVICE_RADGROUP_PREFIX = 'service'

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


@bp.route('<int:service_id>/radgroupreply')
def radgpreply_list(service_id):
    if service_id is not 0:
        name_gp = '{0}_{1}'.format(SERVICE_RADGROUP_PREFIX, service_id)
    else:
        name_gp = DEFAULT_SERVICE
    rad_gp = RadGroupReply.query.filter_by(groupname=name_gp)
    return render_template(
        'service/radgroup/index.html',
        category=name_gp,
        service_id=service_id,
        items=rad_gp
    )


@bp.route('<int:service_id>/radgroupreply/create', methods=['GET', 'POST'])
def radgpreply_create(service_id):
    form = RadGpForm()

    if form.validate_on_submit():
        if service_id is not 0:
            name_gp = '{0}_{1}'.format(SERVICE_RADGROUP_PREFIX, service_id)
        else:
            name_gp = DEFAULT_SERVICE
        rad_gp = RadGroupReply(
            groupname=name_gp,
            attribute=form.attribute.data,
            op=form.op.data,
            value=form.value.data,
        )
        db.session.add(rad_gp)
        db.session.commit()
        flash('Новый атрибут добавлен.', 'success')
        return redirect(url_for('.radgpreply_list', service_id=service_id))

    return render_template(
        'service/radgroup/form.html',
        title='Добавления атрибута',
        form=form,
    )


@bp.route('<int:service_id>/radgroupreply/edit/<int:id>', methods=['GET', 'POST'])
def radgpreply_edit(service_id, id):
    rad_gp = RadGroupReply.query.get(id)
    form = RadGpForm()

    if form.validate_on_submit():
        rad_gp.attribute = form.attribute.data
        rad_gp.op = form.op.data
        rad_gp.value = form.value.data
        db.session.commit()
        flash('Атрибут обновлен.', 'success')
        return redirect(url_for('.radgpreply_list', service_id=service_id))

    form.attribute.data =rad_gp.attribute
    form.op.data = rad_gp.op
    form.value.data = rad_gp.value

    return render_template(
        'service/radgroup/form.html',
        title='Изменения атрибута',
        form=form,
    )


@bp.route('<int:service_id>/radgroupreply/delete/<int:id>')
def radgpreply_delete(service_id, id):
    rad_gp = RadGroupReply.query.get(id)
    db.session.delete(rad_gp)
    db.session.commit()
    flash('Удален', 'success')
    return redirect(url_for('.radgpreply_list', service_id=service_id))
