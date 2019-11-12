from flask import render_template, redirect, flash, url_for, Markup
from app import db
from app.models import Network, NetworkHost
from .forms import LanCreateForm
from . import lan_bp
import ipaddress
from app.auth_helper import requires_admin


# generate list hosts except atewayhost
def itemsnethost(ipnet, gatewayhost):
    nethosts = []

    if (ipnet.prefixlen <= 24):
        for subnetwork in ipnet.subnets(new_prefix=24):
            nethosts.extend(subnetwork.hosts())
    else:
        nethosts = list(ipnet.hosts())

    if gatewayhost in nethosts:
        nethosts.remove(gatewayhost)

    return nethosts


@lan_bp.route('/')
def show_lan():
    lans = Network.query.all()
    return render_template('lan/index.html', lans=lans)


@lan_bp.route('/create', methods=['GET', 'POST'])
@requires_admin
def lan_create():
    form = LanCreateForm()

    if form.validate_on_submit():

        net = Network(
            name=form.name.data,
            svlan=form.svlan.data,
            netmask=form.netmask.data,
        )
        net.netlan_ipv4 = form.netlan_ipv4.data
        net.dns_ipv4 = form.dns_ipv4.data
        net.gateway_ipv4 = form.gateway_ipv4.data

        ipnet = ipaddress.ip_network("{0}/{1}".format(form.netlan_ipv4.data, form.netmask.data))
        gateway = ipaddress.ip_address(form.gateway_ipv4.data)

        nethosts = itemsnethost(ipnet, gateway)

        db.session.add(net)
        db.session.flush()
        db.session.refresh(net)

        obj_host = []

        for nethost in nethosts:
            int_host = int(ipaddress.IPv4Address(nethost))
            obj_host.append(
                NetworkHost(
                    network_id=net.id,
                    host=int_host,
                )
            )

        db.session.bulk_save_objects(obj_host)

        db.session.commit()
        flash('Новая подсеть добавлена.', 'success')
        return redirect(url_for('.show_lan'))

    return render_template(
        'lan/form.html',
        title='Добавление сети',
        form=form,
    )

@lan_bp.route('/stat/<int:id>')
def lan_stat(id):
    network = Network.query.get(id)
    count_host_create = NetworkHost.query.filter_by(network_id=id).count()
    count_host_free = NetworkHost.query.filter_by(network_id=id, eqptport_id=None).count()
    return render_template(
        'lan/stat.html',
        title='Статистика подсети',
        network=network,
        host_count=count_host_create,
        host_free=count_host_free,
    )


@lan_bp.route('/delete/<int:id>')
@requires_admin
def lan_delete(id):
    count_host_create = NetworkHost.query.filter_by(network_id=id).count()
    count_host_free = NetworkHost.query.filter_by(network_id=id, eqptport_id=None).count()

    if count_host_create == count_host_free:
        host = NetworkHost.query.filter_by(network_id=id).all()
        db.session.delete(host)
        db.session.commit()
        flash('Удален', 'success')
    else:
        flash(
            Markup(
                '<b>Невозможно удалить подсеть.</b> '
                'Удалите сначала все порты из этой сети. '
                '<b>Создано {0}, использовано {1}.</b>'.format(
                    count_host_create, count_host_create - count_host_free,
                )), 'danger')

    return redirect(url_for('.show_lan'))
