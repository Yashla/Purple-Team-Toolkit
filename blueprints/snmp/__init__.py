from flask import Blueprint

snmp = Blueprint('snmp', __name__, template_folder='templates')

from . import routes
