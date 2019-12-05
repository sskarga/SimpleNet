from app.models import RadCheck, RadReply, RadUserGroup, RadAcct, RadPostAuth, RadGroupReply, \
    EqptPort, NetworkHost, Network, Client
from app.models import CLIENT_STATUS
from app import db
import click
from flask import current_app
from pyrad.client import Client as RadClient
from pyrad import dictionary
from pyrad import packet
import sys

DEFAULT_SERVICE = 'default'


def check_rad_default_service():
    check_service = RadGroupReply.query.filter_by(groupname=DEFAULT_SERVICE).count()
    if check_service == 0:
        obj_rad = []
        obj_rad.append(
            RadGroupReply(
                groupname=DEFAULT_SERVICE,
                attribute='L4-Redirect-ipset',
                op='=',
                value='deny',
            )
        )

        obj_rad.append(
            RadGroupReply(
                groupname=DEFAULT_SERVICE,
                attribute='L4-Redirect',
                op='=',
                value='1',
            )
        )

        obj_rad.append(
            RadGroupReply(
                groupname=DEFAULT_SERVICE,
                attribute='Filter-Id',
                op='=',
                value='128/128',
            )
        )

        db.session.bulk_save_objects(obj_rad)
        db.session.commit()
        click.echo("Freeradius default service '{0}' create.".format(DEFAULT_SERVICE))
    else:
        click.echo("Freeradius default service exists.")


def rad_add(id_port: int):
    try:
        port = EqptPort.query.get(id_port)
        username = port.radius_user

        # Section Rad check --------------------------------------------------
        rad_check = RadCheck(
            username=username,
            attribute='Cleartext-Password',
            op=':=',
            value=port.radius_pass,
        )

        # Section Rad reply --------------------------------------------------
        obj_rad_reply = []

        net_host = NetworkHost.query.filter_by(eqptport_id=id_port).first()
        network = Network.query.get(net_host.network_id)

        obj_rad_reply.append(
            RadReply(
                username=username,
                attribute='Framed-IP-Address',
                op='=',
                value=net_host.host_ipv4,
            )
        )

        obj_rad_reply.append(
            RadReply(
                username=username,
                attribute='DHCP-Router-IP-Address',
                op='=',
                value=network.gateway_ipv4,
            )
        )

        obj_rad_reply.append(
            RadReply(
                username=username,
                attribute='DHCP-Mask',
                op='=',
                value=network.netmask,
            )
        )

        # Section Rad group --------------------------------------------------
        rad_group = RadUserGroup(
            username=username,
            groupname=DEFAULT_SERVICE,
            priority=1,
        )

        db.session.add(rad_check)
        db.session.bulk_save_objects(obj_rad_reply)
        db.session.add(rad_group)
        db.session.commit()

        return True

    except:
        db.session.rollback()
        raise


def rad_delete(id_port):
    try:
        port = EqptPort.query.get(id_port)
        username = port.radius_user

        RadCheck.query.filter_by(username=username).delete()  # Section Rad check
        RadReply.query.filter_by(username=username).delete()  # Section Rad reply
        RadUserGroup.query.filter_by(username=username).delete()  # Section Rad group
        RadPostAuth.query.filter_by(username=username).delete()
        RadAcct.query.filter_by(username=username).delete()
        db.session.commit()
        return True

    except:
        db.session.rollback()
        raise


def rad_update_group(id_port: int):
    try:
        port = EqptPort.query.get(id_port)
        username = port.radius_user
        rad_group = RadUserGroup.query.filter_by(username=username).first()
        rad_group.groupname = DEFAULT_SERVICE

        client = Client.query.filter_by(eqptport_id=id_port).first()
        if client is not None:
            if client.status == CLIENT_STATUS['on']:
                rad_group.groupname = 'service_{0}'.format(client.service_id)

        db.session.commit()

    except:
        db.session.rollback()
        raise


def rad_disconnect(id_port: int):
    port = EqptPort.query.get(id_port)
    rad_acct = RadAcct.query \
        .filter_by(username=port.radius_user, acctstoptime=None) \
        .order_by(
        RadAcct.radacctid.desc()
    ).first()

    if rad_acct is not None:
        """
        # TO-DO: Need testing ------------------------------------
        """
        acct_session_id = rad_acct.acctsessionid
        nas_ip_address  = rad_acct.nasipaddress

        # create coa client
        client = RadClient(
            server=current_app.config['RADIUS_ADDRESS'],
            secret=current_app.config['RADIUS_SECRET'],
            dict=dictionary.Dictionary("dictionary")
        )
        # set coa timeout
        client.timeout = current_app.config['RADIUS_TIMEOUT']

        attr = {
            "Acct-Session-Id": acct_session_id,
            "User-Name": port.radius_user,
            "NAS-IP-Address": nas_ip_address,
        }

        # create coa request packet
        attributes = {k.replace("-", "_"): attr[k] for k in attr}
        request = client.CreateCoAPacket(code=packet.DisconnectRequest, **attributes)
        return client.SendPacket(request)
        # return 'Off CoA paket - need testing. User online.'
    else:
        return 'No active user session found. User offline.'
