from flask import Blueprint

arp = Blueprint('arp', __name__, template_folder='templates')

from .routes import *
