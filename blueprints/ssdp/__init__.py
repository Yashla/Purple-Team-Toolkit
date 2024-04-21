from flask import Blueprint

ssdp = Blueprint('ssdp', __name__, template_folder='templates')

from . import routes



