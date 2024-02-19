import threading
#from network_scanner import get_windows_os_info
#from network_scanner import get_linux_os_info
#from network_scanner import get_mac_os_info
from discover_mdnss import discover_services
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from network_scanner import NetworkScanner
from extensions import db


app = Flask(__name__) #starting up flask 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://phpmyadmin:2002@localhost/scan'
app.secret_key = 'your_secret_key'
db.init_app(app)

from models import DeviceInfo
from models import Device

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
@app.route('/add_device', methods=['POST'])
def add_device():
    # Extract device details from the form submission
    ips = request.form.getlist('ip[]')
    for ip in ips:
        device_type = request.form.get('type[{}]'.format(ip))
        username = request.form.get('username[{}]'.format(ip))
        password = request.form.get('password[{}]'.format(ip))
    
        # Create a new Device instance
        new_device = Device(ip_address=ip, device_type=device_type, username=username, password=password)
        db.session.add(new_device)
        db.session.flush()  # Flush to ensure new_device.id is populated
        new_device_info = DeviceInfo(
            device_id=new_device.id,  # Link to the newly created Device entry
            ip_address=new_device.ip_address,  # Copy the IP address to devices_information
            device_type=device_type,  # Copy the device type as well
            os_version='',  # Placeholder for actual OS version to be updated later
            open_ports='',  # Placeholder for actual open ports to be updated later
            apps=''  # Placeholder for apps to be updated later
        )
        db.session.add(new_device_info)
    
    db.session.commit()  # Commit the transaction to save both Device and DeviceInfo
    
    flash('Device details successfully sent to the database!')
    return redirect(url_for('index'))

#--------------------------------------------------------------------------------------------------------------------------

@app.route('/start_scripts')
def start_scripts():
    all_devices = Device.query.all()  # Fetch all devices from the database
    for device in all_devices:
        if device.device_type == 'Windows':
            device.os_info = NetworkScanner.get_windows_os_info(device)
            # Call your Windows script here and update device information
            pass
        elif device.device_type == 'Linux':
            device.os_info = NetworkScanner.get_linux_os_info(device)
            # Call your Linux script here and update device information
            pass
        elif device.device_type == 'Mac':
            device.os_info = NetworkScanner.get_mac_os_info(device)
            # Call your MacBook script here and update device information
            pass
        # Update the database with any new information obtained
        db.session.commit()
    
    return render_template('start_scripts.html', devices=all_devices)








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
