from flask import Blueprint

cve_scanner = Blueprint('cve_scanner', __name__, template_folder='templates')

from . import routes
