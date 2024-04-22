from flask import Flask
from extensions import db
from blueprints.ssdp import ssdp as ssdp_blueprint
from blueprints.mdns import mdns as mdns_blueprint
from blueprints.cve_scanner import cve_scanner as cve_scanner_blueprint
from blueprints.main import main as main_blueprint
from blueprints.arp import arp as arp_blueprint
from blueprints.upnp import upnp_bp 
from blueprints.snmp import snmp  
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

# Configure your Flask application
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://phpmyadmin:2002@localhost/scan'
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)
migrate = Migrate(app, db)

# Initialize and register blueprints
app.register_blueprint(ssdp_blueprint, url_prefix='/ssdp')
app.register_blueprint(mdns_blueprint, url_prefix='/mdns')
app.register_blueprint(cve_scanner_blueprint, url_prefix='/cve-scanner')
app.register_blueprint(main_blueprint)
app.register_blueprint(arp_blueprint, url_prefix='/arp')
app.register_blueprint(upnp_bp, url_prefix='/upnptest')
app.register_blueprint(snmp, url_prefix='/snmp')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
