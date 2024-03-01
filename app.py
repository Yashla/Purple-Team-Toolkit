import threading
#from network_scanner import get_windows_os_info
#from network_scanner import get_linux_os_info
#from network_scanner import get_mac_os_info
from discover_mdnss import discover_services
from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify, session
from network_scanner import NetworkScanner
from extensions import db

from models import DeviceInfo
from models import Device
from models import DeviceCVE
import subprocess
import os
import psutil

app = Flask(__name__) #starting up flask 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://phpmyadmin:2002@localhost/scan'
app.secret_key = 'your_secret_key'
db.init_app(app)

process = None 


#ALLOWED_IP = '192.168.0.4'  # Change this to the IP you want to allow

#@app.before_request
#def limit_remote_addr():
#    if request.remote_addr != ALLOWED_IP:
#        abort(403) 


## home page ---------------------------------------------------------------------------------------------------------
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

#########################################################################################################################


@app.route('/ssdp_spoofer')
def ssdp_spoofer():
    return render_template('ssdp_spoofer.html', output=session.get('output'))

@app.route('/start_ssdp', methods=['POST'])
def start_ssdp():
    global process
    # Check if the process is not already running
    if process is None or process.poll() is not None:
        # Set the environment variable for the subprocess to disable output buffering
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = "1"
        
        # Start the subprocess with the modified environment
        process = subprocess.Popen(
            ['python3', '/home/yash/Documents/GitHub/FYP-scan-devices-on-network/essdp/evil/evil_ssdp.py', 'ens37', '--template', 'scanner'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env  # Pass the modified environment
        )
        
        # Define the path to the output file
        output_file_path = "/home/yash/Documents/GitHub/FYP-scan-devices-on-network/essdp/evil/output.txt"
        
        # Start a thread to collect output from the subprocess
        threading.Thread(target=collect_output, args=(output_file_path,)).start()
    
    # Redirect to the ssdp_spoofer page after starting the subprocess
    return redirect(url_for('ssdp_spoofer'))


@app.route('/stop_ssdp', methods=['POST'])
def stop_ssdp():
    global process
    if process and process.poll() is None:  # If process is running
        parent_pid = process.pid  # Get the PID of the ssdp spoofer process
        parent = psutil.Process(parent_pid)  # Get the process using psutil
        for child in parent.children(recursive=True):  # Iterate over child processes
            child.kill()  # Terminate the child process
        process.kill()  # Now kill the parent process
        process.wait()  # Wait for the killing to complete
        process = None
    return redirect(url_for('ssdp_spoofer'))

def collect_output(output_file_path):
    global process
    if process is None:
        return  # Exit early if the process hasn't been started

    with open(output_file_path, "w") as output_file:
        while True:
            if process is None or process.poll() is not None:
                break  # Exit the loop if the process is terminated or completes
            line = process.stdout.readline()
            if not line:
                break  # If there's no more output, exit the loop
            output_file.write(line)
            output_file.flush()  # Flush after each write to ensure real-time update

    os.chmod(output_file_path, 0o666)  # Set file permissions to rw-rw-rw- after closing the file
###########################################################################################################################################################

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
    devices = Device.query.all()
    return render_template('devices.html', devices=devices)


#------------------------------------------------------------------------------------------------------------------------
@app.route('/device_cves/<int:device_id>')
def show_device_cves(device_id):
    device = Device.query.get_or_404(device_id)
    device_cves = DeviceCVE.query.filter_by(device_id=device_id).all()
    return render_template('device_cves.html', device=device, device_cves=device_cves)


#------------------------------------------------------------------------------------------------------------------------
@app.route('/test_details')
def test_details():
    return render_template('test_details.html')

@app.route('/test_windows', methods=['POST'])
def test_windows():
    ip = request.form['windows_ip']
    username = request.form['windows_username']
    password = request.form['windows_password']
    message = NetworkScanner.test_windows_connection(ip, username, password)
    flash(message)  # Using Flask's flash to display messages
    return redirect(url_for('test_details'))

@app.route('/test_ssh', methods=['POST'])
def test_ssh():
    ip = request.form['ssh_ip']
    username = request.form['ssh_username']
    password = request.form['ssh_password']
    message = NetworkScanner.test_ssh_connection(ip, username, password)
    flash(message)
    return redirect(url_for('test_details'))
#-------------------------------------------------------------------------------------------------------------------------

@app.route('/upnp_devices_detailed')
def display_upnp_devices():
    devices_info = NetworkScanner.discover_upnp_devices_detailed()
    return render_template('upnp_devices_detailed.html', devices=devices_info)

#-------------------------------------------------------------------------------------------------------------------------

@app.route('/upnp_devices_github')
def run_script():
    # Assuming your script prints its output, capture it using subprocess
    result = subprocess.run(['python3', 'upnp_info.py'], capture_output=True, text=True)
    output = result.stdout  # Get the standard output of your script
    # Pass the output to a new template or return it directly
    return render_template('upnp_results_github.html', output=output)





#-------------------------------------------------------------------------------------------------------------------------
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
    
    ip_command_output = subprocess.run(['ip', 'a'], stdout=subprocess.PIPE, text=True).stdout
    
    if request.method == 'POST':
        subnet = request.form['subnet']
        scanner = NetworkScanner()
        scanner.scan_network(subnet)
        scanner.scan_mdns()
        scanner.refine_linux_array()
        return render_template('scan.html', subnet=subnet, windows=scanner.windows_array, linux=scanner.linux_array, macbooks=scanner.macbook_array, scanned=True)
    return render_template('scan.html', scanned=False, ip_output=ip_command_output)


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
