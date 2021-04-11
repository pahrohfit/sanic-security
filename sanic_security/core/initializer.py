from sanic import Sanic

from sanic_security.core.config import config
from sanic_security.core.models import Session
from sanic_security.lib.ip2proxy import initialize_ip2proxy
from sanic_security.lib.tortoise import initialize_tortoise


def initialize_security(app: Sanic):
    """
    Initializes sanic-security.

    :param app: Sanic object used to add tasks too.
    """
    if config.has_section('IP2PROXY'):
        app.add_task(initialize_ip2proxy())
    Session.initialize_cache(app)
    initialize_tortoise(app)