# routes.py
from flask import render_template, request, Blueprint
from flask_login import login_required
from . import arp
from .Arp_scanner import perform_arp_scan


@arp.route('/arp_scan', methods=['GET', 'POST'])
@login_required
def arp_scan_view():
    results = ""
    if request.method == 'POST':
        target_ip = request.form['network']
        results = perform_arp_scan(target_ip)
        print(results)
    return render_template('arp/arp_scan.html', scan_results=results)