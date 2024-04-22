from . import cve_scanner
from flask import render_template, request, redirect, url_for, flash
from models import Device, DeviceCVE, DeviceInfo 
from blueprints.cve_scanner.network_scanner import NetworkScanner
import subprocess
from extensions import db

@cve_scanner.route('/devices')
def show_devices():
    devices = Device.query.all()
    return render_template('cve_scanner/devices.html', devices=devices)

@cve_scanner.route('/device_cves/<int:device_id>')
def show_device_cves(device_id):
    device = Device.query.get_or_404(device_id)
    device_cves = DeviceCVE.query.filter_by(device_id=device_id).all()
    return render_template('cve_scanner/device_cves.html', device=device, device_cves=device_cves)

@cve_scanner.route('/test_details')
def test_details():
    return render_template('cve_scanner/test_details.html')

@cve_scanner.route('/test_windows', methods=['POST'])
def test_windows():
    ip = request.form['windows_ip']
    username = request.form['windows_username']
    password = request.form['windows_password']
    message = NetworkScanner.test_windows_connection(ip, username, password)
    flash(message)
    return redirect(url_for('cve_scanner.test_details'))

@cve_scanner.route('/test_ssh', methods=['POST'])
def test_ssh():
    ip = request.form['ssh_ip']
    username = request.form['ssh_username']
    password = request.form['ssh_password']
    message = NetworkScanner.test_ssh_connection(ip, username, password)
    flash(message)
    return redirect(url_for('cve_scanner.test_details'))


@cve_scanner.route('/scan', methods=['GET', 'POST'])
def scan_network():
    ip_command_output = subprocess.run(['ip', 'a'], stdout=subprocess.PIPE, text=True).stdout
    
    if request.method == 'POST':
        subnet = request.form['subnet']
        scanner = NetworkScanner()
        scanner.scan_network(subnet)
        scanner.scan_mdns()
        scanner.refine_linux_array()
        return render_template('cve_scanner/scan.html', subnet=subnet, windows=scanner.windows_array, linux=scanner.linux_array, macbooks=scanner.macbook_array, scanned=True)
    return render_template('cve_scanner/scan.html', scanned=False, ip_output=ip_command_output)


@cve_scanner.route('/reset_db')
def reset_db():
    # Caution: This will drop all data and recreate the tables!
    db.drop_all()
    db.create_all()
    # Redirect to the index page after resetting the database
    return redirect(url_for('main.index'))
@cve_scanner.route('/add_device', methods=['POST'])
def add_device():
    ips = request.form.getlist('ip[]')
    for ip in ips:
        # Check if device with this IP already exists
        existing_device = Device.query.filter_by(ip_address=ip).first()
        if existing_device:
            # Optionally update existing device or continue to the next IP
            flash(f'Device with IP {ip} already exists. Skipping...')
            continue

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
    return redirect(url_for('main.index'))