from flask import Blueprint

mdns = Blueprint('mdns', __name__, template_folder='templates')

from . import routes
