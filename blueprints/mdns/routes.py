from . import mdns
from flask import render_template, request
from .discover_mdnss import discover_services 




@mdns.route('/mdns_discovery', methods=['GET'])
def mDNS_page():
    return render_template('mdns_discovery.html')

    

@mdns.route('/mdns_discovery/results', methods=['GET', 'POST'])
def mdns_discovery():
    if request.method == 'POST':
        service_types_input = request.form['service_types']
        service_types = [st.strip() for st in service_types_input.split(',')]
        discovered_services = discover_services(service_types, duration=10)
        return render_template('mdns_results.html', services=discovered_services)
    return render_template('mdns_discovery.html')
