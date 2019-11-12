from flask import render_template, request, redirect, flash, url_for, current_app
from app.models import Building, EqptPort, Eqpt, EqptModel, Network, NetworkHost, Client
from sqlalchemy.orm import load_only, joinedload
from .forms import EqptCreateForm, EqptEditForm, EqptPortCreateForm, EqptPortEditForm, EqptModelForm, EqptNoteForm
from app import db
from . import eqpt_bp
import ipaddress
from datetime import datetime
from app.auth_helper import requires_admin


port_status = [(0, 'Рабочий'), (-1, 'Неисправный')]


@eqpt_bp.route('/')
def eqpt_search_form():
    return render_template('equipment/search.html')


@eqpt_bp.route('/building/<int:building_id>')
def eqpt_search_by_building(building_id):
    building = Building.query.options(joinedload('street').joinedload('city')).get(building_id)
    eqpts = Eqpt.query.filter_by(building_id=building_id)
    return render_template('equipment/index.html', eqpts=eqpts, building=building)


@eqpt_bp.route('/create/building/<int:building_id>', methods=['GET', 'POST'])
def eqpt_create(building_id):
    form = EqptCreateForm()
    model = [(m.id, m.name) for m in EqptModel.query.all()]
    network = [(n.id, n.name) for n in Network.query.all()]

    form.model_id.choices = model
    form.network_id.choices = network

    if form.validate_on_submit():
        create_eqpt = Eqpt(
            name=form.name.data,
            building_id=building_id,
            serial=form.serial.data,
            mac=form.mac.data,
            network_id=form.network_id.data,
            model_id=form.model_id.data,
            cvlan=form.cvlan.data,
        )

        create_eqpt.ipv4 = form.ipv4.data

        db.session.add(create_eqpt)
        db.session.flush()
        db.session.refresh(create_eqpt)

        eqpt_id = create_eqpt.id

        db.session.commit()
        flash('Узел добавлен.', 'success')
        return redirect(url_for('.port_search_by_eqpt', eqpt_id=eqpt_id))

    return render_template('equipment/form.html', title='Добавление узла сети', form=form)


@eqpt_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def eqpt_edit(id):
    form = EqptEditForm()
    model = [(m.id, m.name) for m in EqptModel.query.all()]
    form.model_id.choices = model

    network = [(n.id, n.name) for n in Network.query.all()]
    form.network_id.choices = network

    eqpt = Eqpt.query.get(id)

    if form.validate_on_submit():
        eqpt.model_id = form.model_id.data
        eqpt.name = form.name.data
        eqpt.ipv4 = form.ipv4.data
        eqpt.serial = form.serial.data
        eqpt.ipv4 = form.ipv4.data
        eqpt.mac = form.mac.data

        cvlan = form.cvlan.data

        if eqpt.cvlan != cvlan:
            flash('Серверный vlan изменен. Обновите данные в созданных портах.', 'warning')

        eqpt.cvlan = form.cvlan.data

        if eqpt.network_id != form.network_id.data:
            port_count = EqptPort.query.filter_by(eqpt_id=eqpt.id).count()
            if port_count:
                flash('Изменить подсеть невозможно. Для изменения подсети удалите порты.', 'danger')
            else:
                eqpt.network_id = form.network_id.data

        db.session.commit()
        flash('Узел обновлен.', 'success')
        return redirect(url_for('.port_search_by_eqpt', eqpt_id=eqpt.id))

    form.model_id.data = eqpt.model_id
    form.name.data = eqpt.name
    form.ipv4.data = eqpt.ipv4
    form.serial.data = eqpt.serial
    form.mac.data = eqpt.mac
    form.network_id.data = eqpt.network_id
    form.cvlan.data = eqpt.cvlan

    return render_template('equipment/form.html', title='Обновление узла сети', form=form)


@eqpt_bp.route('/noteedit/<int:id>', methods=['GET', 'POST'])
def eqpt_note(id):
    form = EqptNoteForm()
    eqpt = Eqpt.query.get(id)

    if form.validate_on_submit():
        eqpt.note = form.note.data
        db.session.commit()
        flash('Примечание обновлено.', 'success')
        return redirect(url_for('.port_search_by_eqpt', eqpt_id=id))

    form.note.data = eqpt.note
    return render_template('equipment/form.html', title='Обновления примечания', form=form)


@eqpt_bp.route('/delete/<int:id>', methods=['GET'])
def eqpt_delete(id):
    del_eqpt = Eqpt.query.get(id)
    building_id = del_eqpt.building_id

    port_count = EqptPort.query.filter_by(eqpt_id=del_eqpt.id).count()
    if port_count:
        flash('Для удаления узла удалите все активные порты.', 'danger')
        return redirect(url_for('.port_search_by_eqpt', eqpt_id=del_eqpt.id))

    db.session.delete(del_eqpt)
    db.session.commit()
    flash('Узел удален.', 'success')
    return redirect(url_for('.eqpt_search_by_building', building_id=building_id))


# Ports
@eqpt_bp.route('/ports/<int:eqpt_id>')
def port_search_by_eqpt(eqpt_id):
    search_eqpt = Eqpt.query.options(load_only('name', 'mac', 'note')).get(eqpt_id)
    ports = EqptPort.query.options(
        joinedload('ip').load_only("host"),
        joinedload('client_on').load_only("apartment", "id")
    ).filter_by(eqpt_id=eqpt_id).order_by(EqptPort.port).all()

    return render_template('equipment/port/index.html', ports=ports, eqpt=search_eqpt)


@eqpt_bp.route('/ports/create/eqpt/<int:eqpt_id>', methods=['GET', 'POST'])
def port_create(eqpt_id):
    form = EqptPortCreateForm()
    head_eqpt = Eqpt.query.get(eqpt_id)
    eqpt_model = EqptModel.query.get(head_eqpt.model_id)
    network_lan = Network.query.get(head_eqpt.network_id)

    form.svlan.data = network_lan.svlan
    form.eqptcvlan.data = head_eqpt.cvlan
    form.mac.data = head_eqpt.mac

    all_port = range(1, eqpt_model.port_count+1)
    use_port = [p.port for p in EqptPort.query.filter_by(eqpt_id=eqpt_id)]
    free_port = sorted(list(set(all_port)-set(use_port)))
    form.port.choices = [(p, str(p)) for p in free_port]

    form.status.choices = port_status

    if form.validate_on_submit():
        check_ip = NetworkHost.query.filter_by(
            network_id=network_lan.id,
            host=int(ipaddress.IPv4Address(form.ipv4.data)),
            eqptport_id=None
        ).first()

        if check_ip:
            eqpt_port = EqptPort(
                eqpt_id=form.eqpt_id.data,
                port=form.port.data,
                cvlan=form.cvlan.data,
                status=form.status.data,
                radius_user=form.radius_user.data,
                radius_pass=form.radius_pass.data,
            )
            eqpt_port.ip = check_ip

            db.session.add(eqpt_port)
            db.session.commit()

            flash('Новый порт добавлен.', 'success')
            return redirect(url_for('.port_search_by_eqpt', eqpt_id=eqpt_id))
        else:
            flash('IP адрес недоступен или уже используется.', 'danger')

    form.eqpt_id.data = eqpt_id

    ip = NetworkHost.query.filter_by(network_id=network_lan.id, eqptport_id=None).first()
    if not ip:
        form.ipv4.data = '0.0.0.0'
    else:
        form.ipv4.data = ip.host_ipv4

    return render_template('equipment/port/form.html', title='Добавление порта', form=form)


@eqpt_bp.route('/ports/edit/<int:id>', methods=['GET', 'POST'])
def port_edit(id):
    form = EqptPortEditForm()
    edit_port = EqptPort.query.get(id)

    head_eqpt = Eqpt.query.get(edit_port.eqpt_id)
    network_lan = Network.query.get(head_eqpt.network_id)

    form.svlan.data = network_lan.svlan
    form.eqptcvlan.data = head_eqpt.cvlan
    form.mac.data = head_eqpt.mac

    form.status.choices = port_status

    if form.validate_on_submit():

        if edit_port.ip.host_ipv4 != form.ipv4.data:
            check_ip = NetworkHost.query.filter_by(
                network_id=network_lan.id,
                host=int(ipaddress.IPv4Address(form.ipv4.data)),
                eqptport_id=None
            ).first()

            if check_ip:
                edit_port.ip = check_ip
            else:
                flash('IP адрес недоступен или уже используется.', 'danger')
                return render_template('equipment/port/form.html', title='Добавление порта', form=form)

        edit_port.port = form.port.data
        edit_port.cvlan = form.cvlan.data
        edit_port.status = form.status.data
        edit_port.radius_user = form.radius_user.data
        edit_port.radius_pass = form.radius_pass.data
        db.session.commit()
        flash('Настройки порта обновлены.', 'success')
        return redirect(url_for('.port_search_by_eqpt', eqpt_id=edit_port.eqpt_id))

    form.port.data = edit_port.port
    form.cvlan.data = edit_port.cvlan
    form.ipv4.data = edit_port.ip.host_ipv4
    form.status.data = edit_port.status

    return render_template('equipment/port/form.html', title='Добавление порта', form=form)


@eqpt_bp.route('/ports/delete/<int:id>', methods=['GET', 'POST'])
def port_delete(id):
    del_port = EqptPort.query.get(id)
    eqpt_id = del_port.eqpt_id

    if del_port.client_on:
        find_client = Client.query.get(del_port.client_on.id)
        find_client.eqptport_id = None
        find_client.suspension_at = datetime.utcnow()
        db.session.flush()
        db.session.refresh(find_client)
        db.session.refresh(del_port)

        flash('Клиент #{0} был отключен.'.format(find_client.id), 'warning')

    db.session.delete(del_port)
    db.session.commit()
    flash('Порт удален.', 'success')
    return redirect(url_for('.port_search_by_eqpt', eqpt_id=eqpt_id))


# Ports
@eqpt_bp.route('/port/<int:port_id>')
def port_search_by_id(port_id):
    port = EqptPort.query.get(port_id)
    if port is not None:
        head_eqpt = Eqpt.query.options(load_only('name', 'mac')).get(port.eqpt_id)
        ports = EqptPort.query.options(
            joinedload('ip').load_only("host"),
            joinedload('client_on').load_only("apartment")
        ).filter_by(eqpt_id=port.eqpt_id).order_by(EqptPort.port).all()

        return render_template('equipment/port/index.html', ports=ports, eqpt=head_eqpt, search_id=port.id)
    else:
        return render_template('equipment/port/index.html', ports=None, eqpt=None, search_id=None)

# Model
@eqpt_bp.route('/model')
def show_model():
    models = EqptModel.query.all()
    return render_template('equipment/model/index.html', models=models)


@eqpt_bp.route('/model/create', methods=['GET', 'POST'])
@requires_admin
def model_create():
    form = EqptModelForm()
    if form.validate_on_submit():
        model = EqptModel(
            name=form.name.data,
            port_count=form.port_count.data,
        )

        db.session.add(model)
        db.session.commit()

        flash('Новая модель оборудования добавлена.', 'success')
        return redirect(url_for('.show_model'))

    return render_template('equipment/model/form.html', title='Добавление модели', form=form)


@eqpt_bp.route('/model/edit/<int:id>', methods=['GET', 'POST'])
@requires_admin
def model_edit(id):
    form = EqptModelForm()
    model = EqptModel.query.get(id)

    if form.validate_on_submit():

        model.name = form.name.data

        if model.port_count > form.port_count.data:
            flash('Количество портов у модели уменьшилось. Проверьте количество портов на конечном оборудовании.', 'warning')

        model.port_count = form.port_count.data

        db.session.commit()

        flash('Модель оборудования обновлена.', 'success')
        return redirect(url_for('.show_model'))

    form.name.data = model.name
    form.port_count.data = model.port_count

    return render_template('equipment/model/form.html', title='Редактирование модели', form=form)


@eqpt_bp.route('/model/delete/<int:id>')
@requires_admin
def model_delete(id):
    model = EqptModel.query.get(id)
    count_eqpt = Eqpt.query.filter_by(model_id=model.id).count()

    if count_eqpt == 0:
        db.session.delete(model)
        db.session.commit()
        flash('Модель удалена.', 'success')
    else:
        flash('Модель не удается удалить. Сначало удалите все оборудование этой модели - {0} шт.'.format(count_eqpt), 'danger')

    return redirect(url_for('.show_model'))


@eqpt_bp.route('/search')
def eqpt_search():
    search_by = request.args.get('p', None)
    search_q = request.args.get('q', None)
    page = request.args.get('page', 1, type=int)

    find_eqpt = None
    title = ''

    if search_by == 'name':
        find_eqpt = Eqpt.query.filter(Eqpt.name.ilike("%{0}%".format(search_q))).paginate(
            page, current_app.config['PAGINATE_PAGE'], False)
        title = "Результаты поиска по имени: {0}".format(search_q)

    if search_by == 'serial':
        find_eqpt = Eqpt.query.filter(Eqpt.serial.ilike("%{0}%".format(search_q))).paginate(
            page, current_app.config['PAGINATE_PAGE'], False)
        title = "Результаты поиска по серийному номеру: {0}".format(search_q)

    if search_by == 'mac':
        find_eqpt = Eqpt.query.filter_by(mac=search_q).paginate(
            page, current_app.config['PAGINATE_PAGE'], False)
        title = "Результаты поиска по MAC: {0}".format(search_q)

    if search_by == 'model':
        find_eqpt = Eqpt.query.filter_by(model_id=int(search_q)).paginate(
            page, current_app.config['PAGINATE_PAGE'], False)
        model = EqptModel.query.get(int(search_q))
        title = "Результаты поиска по модели: {0}".format(model.name)

    if search_by == 'network':
        find_eqpt = Eqpt.query.filter_by(network_id=int(search_q)).paginate(
            page, current_app.config['PAGINATE_PAGE'], False)
        network = Network.query.get(int(search_q))
        title = "Результаты поиска по подсети: {0} ({1}/{2})".format(network.name, network.netlan_ipv4, network.netmask)

    if search_by == 'ip':
        try:
            host = int(ipaddress.IPv4Address(search_q))
            find_eqpt = Eqpt.query.filter_by(ip=host).all()
            title = "Результаты поиска по IP: {0}".format(search_q)

        except Exception:
            find_eqpt = None
            flash("Ошибка выполнения запроса. Ошибка IP адреса: {0}".format(search_q), 'danger')

        return render_template(
            'equipment/search-custom.html',
            title=title,
            eqpts=find_eqpt,
            next_url=None,
            prev_url=None,
        )

    if find_eqpt is not None:
        next_url = url_for('.eqpt_search', page=find_eqpt.next_num) \
            if find_eqpt.has_next else None
        prev_url = url_for('.eqpt_search', page=find_eqpt.prev_num) \
            if find_eqpt.has_prev else None

        return render_template(
            'equipment/search-custom.html',
            title=title,
            eqpts=find_eqpt.items,
            next_url=next_url,
            prev_url=prev_url,
        )

    else:
        return render_template(
            'equipment/search-custom.html',
            title="",
            eqpts=None,
            next_url=None,
            prev_url=None,
        )
