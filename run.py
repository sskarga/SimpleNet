# -*- coding: utf-8 -*-
from app import create_app, db, cli
from app.models import City, Street, Building, Network, NetworkHost, EqptModel, Eqpt, EqptPort,\
    PORT_STATUS, Service, CLIENT_STATUS, Client, LOG_EVENT, LogClient, User,\
    RadCheck, RadGroupCheck, RadGroupReply, RadReply, RadUserGroup

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db, City=City, Street=Street, Building=Building,
        Network=Network, NetworkHost=NetworkHost, EqptModel=EqptModel, Eqpt=Eqpt,
        EqptPort=EqptPort, PORT_STATUS=PORT_STATUS, Service=Service, CLIENT_STATUS=CLIENT_STATUS,
        Client=Client, LOG_EVENT=LOG_EVENT, LogClient=LogClient, User=User,
        RadCheck=RadCheck, RadGroupCheck=RadGroupCheck, RadGroupReply=RadGroupReply, RadReply=RadReply,
        RadUserGroup=RadUserGroup
    )
