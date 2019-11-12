from flask import render_template, flash, url_for, redirect, request, current_app, Markup
from app.models import City, Street, Building, Client, Eqpt
from app import db
from sqlalchemy.orm import joinedload

from . import place_bp
from .forms import PlaceForm


# City ------------------------------------------------------------------------
@place_bp.route('/')
@place_bp.route('/city/')
def city_view():
    places = City.query.order_by('name')
    return render_template('place/city.html', places=places)


@place_bp.route('/city/create', methods=['GET', 'POST'])
def city_create():
    form = PlaceForm()
    if form.validate_on_submit():

        find_city = City.query.filter_by(name=form.name.data).first()
        if find_city is not None:
            flash('Город с таким именем уже существует', 'danger')
            return redirect(url_for('.city_view'))

        city = City(name=form.name.data)
        db.session.add(city)
        db.session.commit()

        flash('Новый город добавлен', 'success')
        return redirect(url_for('.city_view'))

    return render_template('place/form.html', form=form, title='Добавление города')


@place_bp.route('/city/edit/<int:city_id>', methods=['GET', 'POST'])
def city_edit(city_id):
    find_city = City.query.filter_by(id=city_id).first()

    form = PlaceForm()
    if form.validate_on_submit():
        find_city.name = form.name.data
        db.session.commit()

        flash('Изменения сохранены', 'success')
        return redirect(url_for('.city_view'))

    form.name.data = find_city.name
    return render_template('place/form.html', form=form, title='Редактировать название города')


@place_bp.route('/city/delete/<int:city_id>')
def city_delete(city_id):
    find_city = City.query.filter_by(id=city_id).first()
    count_street = Street.query.filter_by(city_id=city_id).count()

    if count_street > 0:
        flash(
            Markup(
                'Невозможно удалить город. Удалите сначала <a href="{0}" class="alert-link">улицы/дома - {1}</a>.'.format(
                    url_for('.street_view', city_id=city_id), count_street,
            )), 'danger')
    else:
        db.session.delete(find_city)
        db.session.commit()

        flash('Удален', 'success')

    return redirect(url_for('.city_view'))


# Street ----------------------------------------------------------------------
@place_bp.route('/city/<int:city_id>')
def street_view(city_id):
    page = request.args.get('page', 1, type=int)
    places = Street.query.filter_by(city_id=city_id).order_by('name').paginate(
        page, current_app.config['PAGINATE_PAGE'], False)

    next_url = url_for('.street_view', city_id=city_id, page=places.next_num) \
        if places.has_next else None
    prev_url = url_for('.street_view', city_id=city_id, page=places.prev_num) \
        if places.has_prev else None

    city = City.query.get(city_id)
    parent_place = {
        'city': city.name,
        'city_id': city.id,
    }

    return render_template(
        'place/street.html',
        places=places.items,
        parent_place=parent_place,
        next_url=next_url,
        prev_url=prev_url,
    )


@place_bp.route('/street/create/<int:city_id>', methods=['GET', 'POST'])
def street_create(city_id):
    form = PlaceForm()
    if form.validate_on_submit():

        find_street = Street.query.filter_by(name=form.name.data, city_id=city_id).first()
        if find_street is not None:
            flash('Улица/район с таким именем уже существует', 'danger')
            return redirect(url_for('.street_view', city_id=city_id))

        street = Street(name=form.name.data, city_id=city_id)
        db.session.add(street)
        db.session.commit()

        flash('Новая улица/район добавлен', 'success')
        return redirect(url_for('.street_view', city_id=city_id))

    city = City.query.get(city_id)
    title = 'Добавление улицы/района в {}'.format(city.name)

    return render_template('place/form.html', form=form, title=title)


@place_bp.route('/street/edit/<int:street_id>', methods=['GET', 'POST'])
def street_edit(street_id):
    find_street = Street.query.filter_by(id=street_id).first()

    form = PlaceForm()
    if form.validate_on_submit():
        find_street.name = form.name.data
        city_id = find_street.city_id
        db.session.commit()

        flash('Изменения сохранены', 'success')
        return redirect(url_for('.street_view', city_id=city_id))

    form.name.data = find_street.name
    return render_template('place/form.html', form=form, title='Редактировать название улицы/район')


@place_bp.route('/street/delete/<int:street_id>')
def street_delete(street_id):
    find_street = Street.query.filter_by(id=street_id).first()
    count_building = Building.query.filter_by(street_id=street_id).count()
    city_id = find_street.city_id

    if count_building > 0:
        flash(
            Markup(
                'Невозможно удалить улицу/район. Удалите сначала <a href="{0}" class="alert-link">дома - {1}</a>.'.format(
                    url_for('.building_view', street_id=street_id), count_building,
            )), 'danger')
    else:
        db.session.delete(find_street)
        db.session.commit()

        flash('Удален', 'success')

    return redirect(url_for('.street_view', city_id=city_id))


# Building --------------------------------------------------------------------
@place_bp.route('/street/<int:street_id>', methods=['GET'])
def building_view(street_id):
    page = request.args.get('page', 1, type=int)
    places = Building.query.filter_by(street_id=street_id).order_by('name').paginate(
        page, current_app.config['PAGINATE_PAGE'], False)

    next_url = url_for('.building_view', street_id=street_id, page=places.next_num) \
        if places.has_next else None
    prev_url = url_for('.building_view', street_id=street_id, page=places.prev_num) \
        if places.has_prev else None

    # street = Street.query.get(street_id)
    street = Street.query.options(joinedload('city')).get(street_id)
    parent_place = {
        'city': street.city.name,
        'city_id': street.city.id,
        'street': street.name,
        'street_id': street.id
    }

    return render_template(
        'place/building.html',
        places=places.items,
        parent_place=parent_place,
        next_url=next_url,
        prev_url=prev_url
        )


@place_bp.route('/building/create/<int:street_id>', methods=['GET', 'POST'])
def building_create(street_id):
    form = PlaceForm()
    if form.validate_on_submit():

        find_building = Building.query.filter_by(name=form.name.data, street_id=street_id).first()
        if find_building is not None:
            flash('Сооружение с таким именем уже существует', 'danger')
            return redirect(url_for('.building_view', street_id=street_id))

        building = Building(name=form.name.data, street_id=street_id)
        db.session.add(building)
        db.session.commit()

        flash('Новое сооружение добавлено', 'success')
        return redirect(url_for('.building_view', street_id=street_id))

    parent_street = Street.query.options(joinedload('city')).get(street_id)
    title = 'Добавление строения по адресу {}, {}'.format(parent_street.city.name, parent_street.name)

    return render_template('place/form.html', form=form, title=title)


@place_bp.route('/building/edit/<int:building_id>', methods=['GET', 'POST'])
def building_edit(building_id):
    find_building = Building.query.filter_by(id=building_id).first()

    form = PlaceForm()
    if form.validate_on_submit():
        find_building.name = form.name.data
        street_id = find_building.street_id
        db.session.commit()

        flash('Изменения сохранены', 'success')
        return redirect(url_for('.building_view', street_id=street_id))

    form.name.data = find_building.name
    return render_template('place/form.html', form=form, title='Редактировать название сооружения')


@place_bp.route('/building/delete/<int:building_id>', methods=['GET', 'POST'])
def building_delete(building_id):
    find_building = Building.query.get(building_id)
    street_id = find_building.street_id

    count_client = Client.query.filter_by(building_id=building_id).count()
    count_eqpts = Eqpt.query.filter_by(building_id=building_id).count()

    if count_client > 0:
        flash(
            Markup(
                'Невозможно удалить дом. Удалите сначала <a href="{0}" class="alert-link" target="_blank">клиентов - {1}</a>.'.format(
                    url_for('client_bp.client_search_by_building', building_id=building_id), count_client,
            )), 'danger')

    if count_eqpts > 0:
        flash(
            Markup(
                'Невозможно удалить дом. Удалите сначала <a href="{0}" class="alert-link" target="_blank">оборудование - {1}</a>.'.format(
                    url_for('eqpt_bp.eqpt_search_by_building', building_id=building_id), count_eqpts,
            )), 'danger')

    if (count_client == 0) and (count_eqpts == 0):
        db.session.delete(find_building)
        db.session.commit()
        flash('Удален', 'success')

    return redirect(url_for('.building_view', street_id=street_id))

