import click

from app.auth_helper import check_user_admin
from app.freeradius import check_rad_default_service

def register(app):
    @app.cli.group()
    def init():
        """Init commands."""
        pass

    @init.command()
    def admin():
        """Create default user admin"""
        click.echo('Create default user admin')
        check_user_admin()


    @init.command()
    def raddefault():
        """Create default rad service"""
        click.echo('Create default rad service')
        check_rad_default_service()
