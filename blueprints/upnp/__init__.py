from flask import Blueprint

upnp_bp = Blueprint('upnp_bp', __name__, template_folder='templates')
from . import routes
