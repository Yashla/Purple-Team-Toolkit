import threading
from upnp_discovery import discover_upnp_devices
from discover_mdnss import discover_services
from flask import Flask, render_template, request, redirect, url_for, flash
from network_scanner import NetworkScanner
from network_scanner import ssh_into_device

app = Flask(__name__) #starting up flask 
app.secret_key = 'your_secret_key'
## home page ---------------------------------------------------------------------------------------------------------
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

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
