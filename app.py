from flask import Flask, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash

# Import your configured `db` from extensions, ensure it's properly set up there
from extensions import db

# Import blueprints
from blueprints.ssdp import ssdp as ssdp_blueprint
from blueprints.mdns import mdns as mdns_blueprint
from blueprints.cve_scanner import cve_scanner as cve_scanner_blueprint
from blueprints.main import main as main_blueprint
from blueprints.arp import arp as arp_blueprint
from blueprints.upnp import upnp_bp 
from blueprints.snmp import snmp  
from blueprints.auth import auth

# Import all models
from models import User, Device, DeviceInfo, CVE, DeviceCVE, SSDPOutput, SNMP_Output

app = Flask(__name__)

# Configure your Flask application
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://phpmyadmin:2002@localhost/scan'
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


# Register blueprints
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
    print("Requested endpoint:", request.endpoint)  # Check what endpoint is being accessed
    print("Is user authenticated?", current_user.is_authenticated)  # Check authentication status
    if not current_user.is_authenticated:
        open_endpoints = ['auth.login', 'auth.register', 'static']
        if request.endpoint not in open_endpoints:
            print("Redirecting to login page.")
            return redirect(url_for('auth.login'))
        else:
            print("Accessing open endpoint:", request.endpoint)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
