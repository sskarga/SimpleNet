from flask import render_template, url_for, redirect, request, flash, current_app
from app import db
from app.models import Building, Client, Service, Eqpt, LogClient, NetworkHost, EqptPort, RadPostAuth, RadAcct, CLIENT_STATUS
from . import client_bp
from sqlalchemy.orm import load_only, joinedload
from flask_login import current_user
from datetime import datetime
from .forms import ClientCreateForm, ClientPersonalInfoForm, ClientServiceInfoForm, ClientAddressForm, \
    ClientPersonalNoteForm
import ipaddress
from app.freeradius import rad_add, rad_delete, rad_update_group, rad_disconnect

client_status = ('Отключен', 'Подключен', 'Долг', 'Пауза')


@client_bp.route('/building/<int:building_id>')
def client_search_by_building(building_id):
    """
    Render the index template on the / route
    """
    building = Building.query.options(joinedload('street').joinedload('city')).get(building_id)
    clients = Client.query.options(joinedload('service')).filter_by(building_id=building_id)
    return render_template('client/index.html', clients=clients, building=building, client_status=client_status)


@client_bp.route('/port/<int:eqptport_id>')
def client_search_by_port(eqptport_id):
    """
    Render the index template on the / route
    """
    building = []
    clients = None

    if Client.query.filter_by(eqptport_id=eqptport_id).scalar() is not None:
        clients = Client.query.filter_by(eqptport_id=eqptport_id)
        building = Building.query.options(joinedload('street').joinedload('city')).get(clients[0].building_id)

    return render_template('client/index.html', clients=clients, building=building, client_status=client_status)


@client_bp.route('/')
def client_search_form():
    return render_template('client/search.html')


@client_bp.route('/building/<int:building_id>/create', methods=['GET', 'POST'])
def client_create(building_id):
    form = ClientCreateForm()

    available_services = Service.query.order_by('name')
    groups_list = [(i.id, '{0} - {1:d} руб./мес'.format(i.name, 0)) for i in available_services]
    form.service_id.choices = groups_list
    form.status.choices = [(client_status.index(st), st) for st in client_status]

    if form.validate_on_submit():

        find_client = Client.query.filter_by(building_id=building_id, apartment=form.apartment.data.strip()).first()
        if find_client is not None:
            flash('Клиент с таким адресом уже добавлен.', 'danger')
            return redirect(url_for('.client_search_by_building', building_id=building_id))

        client = Client(
            building_id=building_id,
            fio=form.fio.data,
            phone=form.phone.data,
            apartment=form.apartment.data,
            status=form.status.data,
            service_id=form.service_id.data,
        )

        # if disconnet
        # TODO: get rid of the "magic" numbers in the condition
        if form.status.data != 1:
            client.suspension_at = datetime.utcnow()
        # else:
        #    client.suspension_at = None

        db.session.add(client)
        db.session.flush()
        db.session.refresh(client)
        log = LogClient(
            client_id=client.id,
            initiator_id=current_user.id,
            username=current_user.name,
            event='Добавлен новый клиент. ФИО: {0}. Статус - {1}, сервис {2}'.format(
                client.fio,
                client_status[client.status],
                Service.query.get(client.service_id).name,
            )
        )

        db.session.add(log)
        db.session.commit()

        flash('Новый клиент добавлен', 'success')
        return redirect(url_for('.client_search_by_building', building_id=building_id))

    building = Building.query.options(joinedload('street').joinedload('city')).get(building_id)

    return render_template('client/form/client.html', form=form, building=building, title='Добавление клиента')


@client_bp.route('<int:client_id>/details', methods=['GET', 'POST'])
def client_details(client_id):
    client = Client.query.options(joinedload('service')).get(client_id)
    building = Building.query.options(joinedload('street').joinedload('city')).get(client.building_id)
    services = Service.query.order_by('name')

    personal_form = ClientPersonalInfoForm()
    personal_form.fio.data = client.fio
    personal_form.phone.data = client.phone

    service_form = ClientServiceInfoForm()
    service_form.service_id.choices = [(i.id, '{0} - {1:d} руб./мес'.format(i.name, 0)) for i in services]
    service_form.service_id.data = client.service_id
    service_form.status.choices = [(client_status.index(st), st) for st in client_status]
    service_form.status.data = client.status

    address_form = ClientAddressForm()
    address_form.building_id.data = client.building_id
    address_form.apartment.data = client.apartment

    return render_template('client/details.html',
                           client=client,
                           building=building,
                           client_status=client_status,
                           services=services,
                           personal_form=personal_form,
                           service_form=service_form,
                           address_form=address_form, )


@client_bp.route('personal_info/edit/<int:client_id>', methods=['GET', 'POST'])
def client_edit_personal(client_id):
    find_client = Client.query.get(client_id)
    form = ClientPersonalInfoForm()

    if form.validate_on_submit():
        find_client.fio = form.fio.data
        find_client.phone = form.phone.data
        db.session.commit()

        flash('Изменения сохранены', 'success')
        return redirect(url_for('.client_details', client_id=client_id))

    form.fio.data = find_client.fio
    form.phone.data = find_client.phone
    return render_template('client/form/default.html', form=form, title='Редактировать')


@client_bp.route('personal_info/note/<int:client_id>', methods=['GET', 'POST'])
def client_edit_note(client_id):
    find_client = Client.query.get(client_id)
    form = ClientPersonalNoteForm()

    if form.validate_on_submit():
        find_client.note = form.note.data
        db.session.commit()

        flash('Изменения сохранены', 'success')
        return redirect(url_for('.client_details', client_id=client_id))

    form.note.data = find_client.note
    return render_template('client/form/default.html', form=form, title='Редактировать')


@client_bp.route('service/edit/<int:client_id>', methods=['GET', 'POST'])
def client_edit_service(client_id):
    find_client = Client.query.get(client_id)
    services = Service.query.order_by('name')

    form = ClientServiceInfoForm()
    form.service_id.choices = [(i.id, '{0} - {1:d} руб./мес'.format(i.name, 0)) for i in services]
    form.status.choices = [(client_status.index(st), st) for st in client_status]

    if form.validate_on_submit():
        find_client.service_id = form.service_id.data
        find_client.status = form.status.data

        if form.status.data != CLIENT_STATUS['on']:
            find_client.suspension_at = datetime.utcnow()
        else:
            find_client.suspension_at = None

        # Radius
        msg = rad_disconnect(find_client.eqptport_id)
        flash(msg, 'warning')
        rad_update_group(find_client.eqptport_id)

        log = LogClient(
            client_id=find_client.id,
            initiator_id=current_user.id,
            username=current_user.name,
            event='Изменения. Статус - {0}, сервис - {1}'.format(
                client_status[form.status.data],
                Service.query.get(find_client.service_id).name,
            )
        )

        db.session.add(log)
        db.session.commit()

        flash('Изменения сохранены', 'success')
        return redirect(url_for('.client_details', client_id=client_id))

    form.service_id.data = find_client.service_id
    form.status.data = find_client.status
    return render_template('client/form/default.html', form=form, title='Редактировать')


@client_bp.route('address/edit/<int:client_id>', methods=['GET', 'POST'])
def client_edit_address(client_id):
    find_client = Client.query.get(client_id)

    form = ClientAddressForm()

    if form.validate_on_submit():
        find_client.building_id = form.building_id.data
        find_client.apartment = form.apartment.data
        db.session.commit()

        flash('Изменения сохранены', 'success')
        return redirect(url_for('.client_details', client_id=client_id))

    form.building_id.data = find_client.building_id
    form.apartment.data = find_client.apartment
    return render_template('client/form/address.html', form=form, title='Редактировать')


@client_bp.route('<int:client_id>/relation/eqpt-building/<int:building_id>', methods=['GET'])
def client_relation_eqpt_building(client_id, building_id):
    find_client = Client.query.get(client_id)
    building = Building.query.options(joinedload('street').joinedload('city')).get(building_id)
    eqpts = Eqpt.query.filter_by(building_id=building_id)
    return render_template(
        'client/relation/eqpt.html',
        client=find_client,
        eqpts=eqpts,
        building=building
    )


@client_bp.route('<int:client_id>/relation/eqpt/<int:eqpt_id>/ports', methods=['GET'])
def client_relation_eqpt_ports(client_id, eqpt_id):
    find_client = Client.query.get(client_id)
    eqpt = Eqpt.query.options(load_only('name', 'mac')).get(eqpt_id)
    ports = EqptPort.query.filter_by(eqpt_id=eqpt_id, status=0)
    return render_template(
        'client/relation/ports.html',
        client=find_client,
        eqpt=eqpt,
        ports=ports
    )


@client_bp.route('<int:client_id>/relation/eqpt/port/<int:port_id>/create', methods=['GET'])
def client_relation_create(client_id, port_id):
    find_client = Client.query.get(client_id)

    if find_client.eqptport_id is not None:
        port = EqptPort.query.get(find_client.eqptport_id)
        port.status = 0

        # Radius
        msg = rad_disconnect(port.id)
        flash(msg, 'warning')
        rad_delete(port.id)

    find_client.eqptport_id = port_id
    find_client.suspension_at = None
    client_port = EqptPort.query.get(port_id)
    client_port.status = 1

    # Radius
    rad_update_group(client_port.id)
    msg = rad_disconnect(client_port.id)
    flash(msg, 'warning')

    log = LogClient(
        client_id=find_client.id,
        initiator_id=current_user.id,
        username=current_user.name,
        type='w',
        event='Клиент подключен к оборудованию port_id={0}.'.format(
            port_id,
        )
    )

    db.session.add(log)
    db.session.commit()

    flash('Клиент подключен к оборудованию.', 'success')
    return redirect(url_for('.client_details', client_id=client_id))


@client_bp.route('<int:client_id>/relation/delete', methods=['GET'])
def client_relation_delete(client_id):
    find_client = Client.query.get(client_id)

    if find_client.eqptport_id is not None:
        port = EqptPort.query.get(find_client.eqptport_id)
        port.status = 0

        # Radius
        msg = rad_disconnect(port.id)
        flash(msg, 'warning')
        rad_delete(port.id)

    find_client.eqptport_id = None
    find_client.suspension_at = datetime.utcnow()
    log = LogClient(
        client_id=find_client.id,
        initiator_id=current_user.id,
        username=current_user.name,
        type='w',
        event='Клиент отключен от оборудования.',
    )

    db.session.add(log)
    db.session.commit()

    flash('Клиент отключен от оборудования.', 'success')
    return redirect(url_for('.client_details', client_id=client_id))


@client_bp.route('delete/<int:client_id>', methods=['GET'])
def client_delete(client_id):
    find_client = Client.query.get(client_id)
    log = LogClient.query.filter_by(client_id=find_client.id)

    building_id = find_client.building_id

    if find_client.eqptport_id is not None:
        port = EqptPort.query.get(find_client.eqptport_id)
        port.status = 0

        # Radius
        msg = rad_disconnect(port.id)
        flash(msg, 'warning')
        rad_delete(port.id)

    find_client.eqptport_id = None
    db.session.flush()
    db.session.refresh(find_client)
    db.session.delete(find_client)
    db.session.delete(log)
    db.session.commit()

    flash('Клиент удален.', 'success')
    return redirect(url_for('.client_search_by_building', building_id=building_id))


@client_bp.route('/<int:client_id>/log', methods=['GET'])
def client_log(client_id):
    page = request.args.get('page', 1, type=int)

    logs = LogClient.query.filter_by(client_id=client_id).order_by(LogClient.id.desc()).paginate(
        page, current_app.config['PAGINATE_PAGE'], False)

    next_url = url_for('.client_log', client_id=client_id, page=logs.next_num) \
        if logs.has_next else None
    prev_url = url_for('.client_log', client_id=client_id, page=logs.prev_num) \
        if logs.has_prev else None

    return render_template(
        'client/log.html',
        client_id=client_id,
        logs=logs.items,
        next_url=next_url,
        prev_url=prev_url
    )


@client_bp.route('/<int:client_id>/radauth', methods=['GET'])
def client_radauth(client_id):
    page = request.args.get('page', 1, type=int)

    cl = Client.query.get(client_id)
    port = EqptPort.query.get(cl.eqptport_id)

    logs = RadPostAuth.query\
        .filter_by(username=port.radius_user)\
        .order_by(RadPostAuth.id.desc())\
        .paginate(page, current_app.config['PAGINATE_PAGE'], False)

    next_url = url_for('.client_log', client_id=client_id, page=logs.next_num) \
        if logs.has_next else None
    prev_url = url_for('.client_log', client_id=client_id, page=logs.prev_num) \
        if logs.has_prev else None

    return render_template(
        'client/radius/radpostauth.html',
        client_id=client_id,
        items=logs.items,
        next_url=next_url,
        prev_url=prev_url
    )


@client_bp.route('/<int:client_id>/radacct', methods=['GET'])
def client_radacct(client_id):
    page = request.args.get('page', 1, type=int)

    cl = Client.query.get(client_id)
    port = EqptPort.query.get(cl.eqptport_id)

    logs = RadAcct.query\
        .filter_by(username=port.radius_user)\
        .order_by(RadAcct.radacctid.desc())\
        .paginate(page, current_app.config['PAGINATE_PAGE'], False)

    next_url = url_for('.client_log', client_id=client_id, page=logs.next_num) \
        if logs.has_next else None
    prev_url = url_for('.client_log', client_id=client_id, page=logs.prev_num) \
        if logs.has_prev else None

    return render_template(
        'client/radius/radacct.html',
        client_id=client_id,
        items=logs.items,
        port_id=cl.eqptport_id,
        next_url=next_url,
        prev_url=prev_url
    )

@client_bp.route('/<int:client_id>/reset-session/<int:port_id>', methods=['GET'])
def client_session_disconnect(client_id, port_id):
    msg = rad_disconnect(port_id)
    flash(msg, 'warning')
    return redirect(url_for('.client_radacct', client_id=client_id))


@client_bp.route('/stat')
def client_stat():
    cl_connect = Client.query.filter_by(status=CLIENT_STATUS['on']).count()
    cl_off = Client.query.filter_by(status=CLIENT_STATUS['off']).count()
    cl_debt = Client.query.filter_by(status=CLIENT_STATUS['debt']).count()
    cl_pause = Client.query.filter_by(status=CLIENT_STATUS['pause']).count()

    return render_template(
        'client/stat.html',
        cl_connect=cl_connect,
        cl_off=cl_off,
        cl_debt=cl_debt,
        cl_pause=cl_pause,
    )


@client_bp.route('/search', methods=['GET'])
def client_search():
    search_by = request.args.get('p', None)
    search_q = request.args.get('q', None)
    page = request.args.get('page', 1, type=int)

    find_client = None
    title = None

    if search_by == 'wait':
        find_client = Client.query.filter_by(status=1, eqptport_id=None).paginate(
        page, current_app.config['PAGINATE_PAGE'], False)
        title = "Результат поиска: клиенты ожидающие подключения"

    if search_by == 'fio':
        find_client = Client.query.filter(Client.fio.ilike("%{0}%".format(search_q))).paginate(
        page, current_app.config['PAGINATE_PAGE'], False)
        title = "Результаты поиска по имени: {0}".format(search_q)

    if search_by == 'phone':
        find_client = Client.query.filter(Client.phone.like("%{0}%".format(search_q))).paginate(
        page, current_app.config['PAGINATE_PAGE'], False)
        title = "Результаты поиска по телефону: {0}".format(search_q)

    if search_by == 'ip':
        try:
            host = int(ipaddress.IPv4Address(search_q))
            net_host = NetworkHost.query.get(host)
            if net_host is not None:
                if net_host.eqptport_id is not None:
                    port = EqptPort.query.get(net_host.eqptport_id)
                    find_client = Client.query.filter_by(eqptport_id=port.id)
                    title = "Результаты поиска по ip: {0}".format(search_q)
                else:
                    flash("IP адрес свободен: {0}".format(search_q), 'warning')

            else:
                flash("IP адрес вне диапазона: {0}".format(search_q), 'warning')

        except Exception:
            find_client = None
            flash("Ошибка выполнения запроса. Ошибка IP адреса: {0}".format(search_q), 'danger')

        return render_template(
            'client/search-custom.html',
            title=title,
            clients=find_client,
            next_url=None,
            prev_url=None,
        )

    if find_client is not None:
        next_url = url_for('.client_search', page=find_client.next_num) \
            if find_client.has_next else None
        prev_url = url_for('.client_search', page=find_client.prev_num) \
            if find_client.has_prev else None

        return render_template(
            'client/search-custom.html',
            title=title,
            clients=find_client.items,
            next_url=next_url,
            prev_url=prev_url,
        )

    else:
        return render_template(
            'client/search-custom.html',
            title="",
            clients=None,
            next_url=None,
            prev_url=None,
        )
