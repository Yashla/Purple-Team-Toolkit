from flask import Blueprint

# Create a blueprint for SNMP operations
snmp = Blueprint('snmp', __name__, template_folder='templates')

# Import the routes module after initializing the blueprint to avoid circular imports
from . import routes
