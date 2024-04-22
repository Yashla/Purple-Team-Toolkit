from flask import Blueprint

auth = Blueprint('auth', __name__, template_folder='templates')


from . import routes  # Import at the end to avoid circular dependencies

