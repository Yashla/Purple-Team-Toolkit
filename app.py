from flask import Flask, request, render_template, jsonify
from snmpwalker import snmp_walk # importing functions form main script
from snmpcomtester import test_snmp_community_strings
from arp_ip_mac_vendor import arp
from upnp_discovery import discover_upnp_devices
from discover_mdnss import discover_services

app = Flask(__name__) #starting up flask 
## home page ---------------------------------------------------------------------------------------------------------
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

##SNMP walker stuff --------------------------------------------------------------------------------------------------
@app.route('/snmpwalker', methods=['GET'])# get info from the snmpwalker page and sends its to the snmpwalker results page 
def snmpwalker():
    return render_template('snmpwalker.html')

@app.route('/snmpwalker/result', methods=['GET','POST'])### this actually run the script 
def snmpwalker_result():
    ip_addr = request.form['ip_addr']
    community_string = request.form['community_string']
    oid = request.form['oid']
    oids = [oid.strip() for oid in oid.split(', ')]
    result = snmp_walk(ip_addr, community_string, oids)
    return render_template('snmpwalker_result.html', result=result)
##----------------------------------------------------------------------------------------------------------------------


#SNMP Com Tester----------------------------------------------------------------------------------------------------------
@app.route('/snmpcomtester', methods=['GET'])# get info from the snmpwalker page and sends its to the snmpwalker results page 
def snmpcomtester():
    return render_template('snmpcomtester.html')

@app.route('/snmpcomtester/result', methods=['GET','POST'])### this actually run the script 
def snmpcomtester_result():
    ip = request.form['ip_address']
    community_strings_input = request.form['community_strings']
    community_strings = [cs.strip() for cs in community_strings_input.split(',')]
    com_results = test_snmp_community_strings(ip, community_strings)
    return render_template('snmpcomtester_result.html',results=com_results, ip_address=ip)




#arp/ip/vendor----------------------------------------------------------------------------------------------------------
@app.route('/arp_ip_vendor', methods=['GET'])
def arp_page():
    return render_template('arp_ip_vendor.html')

@app.route('/arp_ip_vendor/result', methods=['GET','POST'])
def arp_page_result():
    ip_addr = request.form['ip_addr']
    arp_results = arp(ip_addr)
    return render_template('arp_ip_vendor_result.html', clients=arp_results)
#-----------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------------
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
