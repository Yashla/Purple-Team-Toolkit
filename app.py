import threading
#from network_scanner import get_windows_os_info
#from network_scanner import get_linux_os_info
#from network_scanner import get_mac_os_info
from discover_mdnss import discover_services
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from network_scanner import NetworkScanner
from extensions import db

from models import DeviceInfo
from models import Device
from models import DeviceCVE

app = Flask(__name__) #starting up flask 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://phpmyadmin:2002@localhost/scan'
app.secret_key = 'your_secret_key'
db.init_app(app)



#ALLOWED_IP = '192.168.0.4'  # Change this to the IP you want to allow

#@app.before_request
#def limit_remote_addr():
#    if request.remote_addr != ALLOWED_IP:
#        abort(403) 



## home page ---------------------------------------------------------------------------------------------------------
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/reset_db')
def reset_db():
    # Caution: This will drop all data and recreate the tables!
    db.drop_all()
    db.create_all()
    # Redirect to the index page after resetting the database
    return redirect(url_for('index'))
#------------------------------------------------------------------------------------------------------------------------
@app.route('/devices')
def show_devices():
    devices = Device.query.all()  # Replace with your method to get all devices
    return render_template('devices.html', devices=devices)

#------------------------------------------------------------------------------------------------------------------------
@app.route('/device_cves/<int:device_id>')
def show_device_cves(device_id):
    device_cves = DeviceCVE.query.filter_by(device_id=device_id).all()
    return render_template('device_cves.html', device_cves=device_cves, device_id=device_id)



#------------------------------------------------------------------------------------------------------------------------

@app.route('/add_device', methods=['POST'])
def add_device():
    ips = request.form.getlist('ip[]')
    for ip in ips:
        device_type = request.form.get('type[{}]'.format(ip))
        username = request.form.get('username[{}]'.format(ip))
        password = request.form.get('password[{}]'.format(ip))

        new_device = Device(ip_address=ip, device_type=device_type, username=username, password=password)
        db.session.add(new_device)
        db.session.flush()

        if device_type.lower() == 'linux':
            vendor, product, version = NetworkScanner.get_linux_os_info(new_device)
        elif device_type.lower() == 'windows':
            vendor, product, version = NetworkScanner.get_windows_os_info(new_device)
        elif device_type.lower() == 'mac':
            vendor, product, version = NetworkScanner.get_mac_os_info(new_device)
        else:
            vendor, product, version = 'Unsupported', 'Unsupported device type', 'N/A'

        if product.startswith("Error") or version.startswith("Error"):
            print(f"Failed to fetch OS information for device {ip} of type {device_type}: {product}, {version}")

        new_device_info = DeviceInfo(device_id=new_device.id, ip_address=ip, device_type=device_type, Vendor=vendor, Product=product, Version=version)
        db.session.add(new_device_info)

        # Pass the device ID to the fetch_and_store_cve_details function
        NetworkScanner.fetch_and_store_cve_details(vendor, product, version, new_device.id)

    db.session.commit()
    return redirect(url_for('index'))



#--------------------------------------------------------------------------------------------------------------------------

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
