from flask import jsonify, make_response, request, json
from app.models import City, Street, Building
from . import api_bp


# Api place --------------------------------------------------------
@api_bp.route('places/сities', methods=['GET'])
def get_сities():
    сities = City.query.order_by('name')

    list_сities = [r.as_dict() for r in сities]
    if len(list_сities) > 0:
        return jsonify(
            results=list_сities,
        )

    return make_response(jsonify({'error': 'Not found'}), 404)


@api_bp.route('places/сities/<int:city_id>', methods=['GET'])
def get_сity(city_id):
    сity = City.query.get(city_id)

    if сity is not None:
        return jsonify({city_id: сity.name})

    return make_response(jsonify({'error': 'Not found'}), 404)


@api_bp.route('places/сities/<int:city_id>/streets', methods=['GET'])
def get_streets_by_сity(city_id):
    if city_id > 0:
        find_street = Street.query.filter_by(city_id=city_id).order_by('name')
        list_street = [r.as_dict() for r in find_street]

        if len(list_street) > 0:
            return jsonify(list_street)

    return make_response(jsonify(
        error='Not found',
        results='',
    ), 404)


@api_bp.route('places/streets', methods=['GET'])
def get_streets():
    search_q = request.args.get('q', None)
    id_q = request.args.get('id', None)
    streets: None

    if id_q:
        if search_q:
            streets = Street.query\
                .filter_by(city_id=id_q)\
                .filter(Street.name.ilike("%{0}%".format(search_q)))\
                .limit(10)
        else:
            streets = Street.query \
                .filter_by(city_id=id_q)

        list_streets = [r.as_dict() for r in streets]
        if len(list_streets) > 0:
            return jsonify(
                results=list_streets,
            )

    return jsonify(
        error='Not found',
        results='',
    )


@api_bp.route('places/streets/<int:street_id>', methods=['GET'])
def get_street(street_id):
    street = Street.query.get(street_id)

    if street is not None:
        return jsonify({street_id: street.name})

    return make_response(jsonify({'error': 'Not found'}), 404)


@api_bp.route('places/streets/<int:street_id>/buildings', methods=['GET'])
def get_buildings_by_street(street_id):
    if street_id > 0:
        find_building = Building.query\
            .filter_by(street_id=street_id)\
            .order_by('name')
        list_building = [r.as_dict() for r in find_building]

        if len(list_building) > 0:
            return jsonify(list_building)

    return make_response(jsonify({'error': 'Not found'}), 404)


@api_bp.route('places/buildings', methods=['GET'])
def get_buildings():
    search_q = request.args.get('q', None)
    id_q = request.args.get('id', None)

    if id_q:
        buildings = Building.query\
            .filter_by(street_id=id_q)\
            .filter(Building.name.ilike("%{0}%".format(search_q)))\
            .limit(10)
        list_buildings = [r.as_dict() for r in buildings]
        if len(list_buildings) > 0:
            return jsonify(
                results=list_buildings,
            )

    return jsonify(
        error='Not found',
        results='',
    )


@api_bp.route('places/buildings/<int:building_id>', methods=['GET'])
def get_building(building_id):
    building = Building.query.get(building_id)

    if building is not None:
        return jsonify({building_id: building.name})

    return make_response(jsonify({'error': 'Not found'}), 404)
