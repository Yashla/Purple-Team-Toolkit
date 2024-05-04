from flask import Flask, redirect, request, url_for
from flask_migrate import Migrate
from flask_login import LoginManager,current_user
from extensions import db
from blueprints.ssdp import ssdp as ssdp_blueprint
from blueprints.mdns import mdns as mdns_blueprint
from blueprints.cve_scanner import cve_scanner as cve_scanner_blueprint
from blueprints.main import main as main_blueprint
from blueprints.arp import arp as arp_blueprint
from blueprints.upnp import upnp_bp 
from blueprints.snmp import snmp  
from blueprints.auth import auth
from models import User

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://yash:yash@mysql/scan'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

app.register_blueprint(ssdp_blueprint, url_prefix='/ssdp')
app.register_blueprint(mdns_blueprint, url_prefix='/mdns')
app.register_blueprint(cve_scanner_blueprint, url_prefix='/cve-scanner')
app.register_blueprint(main_blueprint)
app.register_blueprint(arp_blueprint, url_prefix='/arp')
app.register_blueprint(upnp_bp, url_prefix='/upnptest')
app.register_blueprint(snmp, url_prefix='/snmp')
app.register_blueprint(auth, url_prefix='/auth')

@app.before_request
def ensure_authenticated():
    print("Requested endpoint:", request.endpoint)  
    print("Is user authenticated", current_user.is_authenticated) 
    if not current_user.is_authenticated:
        open_endpoints = ['auth.login', 'auth.register', 'static']
        if request.endpoint not in open_endpoints:
            print("Redirecting to login page.")
            return redirect(url_for('auth.login'))
        else:
            print("Accessing open endpoint:", request.endpoint)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
