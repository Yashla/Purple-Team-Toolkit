from flask import Blueprint

# Create a Blueprint for the UPnP test module
upnp_bp = Blueprint('upnp_bp', __name__, template_folder='templates')

# Import the routes module, which also imports the upnp_bp object
from . import routes
