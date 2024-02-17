import threading
from upnp_discovery import discover_upnp_devices
from discover_mdnss import discover_services
from flask import Flask, render_template, request, redirect, url_for, flash
from network_scanner import NetworkScanner
from network_scanner import ssh_into_device
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__) #starting up flask 

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://phpmyadmin:2002@localhost/scan'
db = SQLAlchemy(app)

app.secret_key = 'your_secret_key'



## home page ---------------------------------------------------------------------------------------------------------
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

    
class devices(db.Model):
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(15), nullable=False)
    device_type = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Device {self.ip_address}>'
    


#------------------------------------------------------------------------------------------------------------------------
@app.route('/add_device', methods=['POST'])
def add_device():
    # Extract device details from the form submission
    ips = request.form.getlist('ip[]')
    for ip in ips:
        device_type = request.form.get('type[{}]'.format(ip))
        username = request.form.get('username[{}]'.format(ip))
        password = request.form.get('password[{}]'.format(ip))
    
        # Create a new Device instance
        new_device = devices(ip_address=ip, device_type=device_type, username=username, password=password)
        
        # Add to the session and commit to the database
        db.session.add(new_device)
    db.session.commit()
    
    # Provide feedback to the user or redirect
    flash('Device details successfully sent to the database!')
    return redirect(url_for('index'))









#------------------------------------------------------------------------------------------------------------------------
#scan
@app.route('/scan', methods=['GET', 'POST'])
def scan_network():
    if request.method == 'POST':
        subnet = request.form['subnet']
        scanner = NetworkScanner()
        scanner.scan_network(subnet)
        scanner.scan_mdns()
        scanner.refine_linux_array()
        return render_template('scan.html', subnet=subnet, windows=scanner.windows_array, linux=scanner.linux_array, macbooks=scanner.macbook_array, scanned=True)
    return render_template('scan.html', scanned=False)

@app.route('/ssh', methods=['POST'])
def handle_ssh():
    ip = request.form['ip']
    username = request.form['username']
    password = request.form['password']
    success, message = ssh_into_device(ip, username, password)
    if success:
        flash("SSH connection to {} successful.".format(ip))
    else:
        flash("SSH connection failed: {}".format(message))
    return redirect(url_for('scan_network'))

@app.route('/discover_upnp', methods=['GET'])
def discover():
    devices = discover_upnp_devices()
    return render_template('upnp_devices.html', devices=devices)

#-------------------------------------------------------------------------------------------------------------------------

@app.route('/mdns_discovery', methods=['GET'])
def mDNS_page():
    return render_template('mdns_discovery.html')

    

@app.route('/mdns_discovery', methods=['GET', 'POST'])
def mdns_discovery():
    if request.method == 'POST':
        service_types_input = request.form['service_types']
        service_types = [st.strip() for st in service_types_input.split(',')]
        discovered_services = discover_services(service_types, duration=10)
        return render_template('mdns_results.html', services=discovered_services)
    return render_template('mdns_discovery.html')






#-----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
