from io import BytesIO
import threading
#from network_scanner import get_windows_os_info
#from network_scanner import get_linux_os_info
#from network_scanner import get_mac_os_info

from flask import Flask, render_template, request, redirect, send_file, url_for, flash, abort, jsonify, session, Response
from blueprints.cve_scanner.network_scanner import NetworkScanner
from extensions import db
from blueprints.mdns.discover_mdnss import discover_services
from models import DeviceInfo
from models import Device
from models import DeviceCVE
from models import SSDPOutput
import subprocess
import os
import psutil
from datetime import datetime

from blueprints.ssdp import ssdp as ssdp_blueprint
from blueprints.mdns import mdns as mdns_blueprint
from blueprints.cve_scanner import cve_scanner as cve_scanner_blueprint
from blueprints.main import main as main_blueprint
from blueprints.arp import arp as arp_blueprint
from blueprints.upnp import upnp_bp 

#'from blueprints.snmp import snmp as snmp_blueprint

from blueprints.snmp import snmp  

app = Flask(__name__)  # Create the Flask application

# Configure your Flask application (You will need to set up the database URI and secret key)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://phpmyadmin:2002@localhost/scan'
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize extensions like the database with the app
db.init_app(app)


# Register Blueprints
app.register_blueprint(ssdp_blueprint, url_prefix='/ssdp')

app.register_blueprint(mdns_blueprint, url_prefix='/mdns')

app.register_blueprint(cve_scanner_blueprint, url_prefix='/cve-scanner')

app.register_blueprint(main_blueprint)

app.register_blueprint(arp_blueprint, url_prefix='/arp')

app.register_blueprint(upnp_bp, url_prefix='/upnptest')

app.register_blueprint(snmp, url_prefix='/snmp')




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')  # Run the application