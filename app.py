from flask import Flask, request, render_template, jsonify
from snmpwalker import snmp_walk # importing functions form main script
from arp_ip_mac_vendor import arp

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
def snmpwalker():
    return render_template('snmpcomtester.html')

@app.route('/snmpcomtester/result', methods=['GET','POST'])### this actually run the script 
def snmpwalker_result():
    ip_addr = request.form['ip_addr']
   
    return render_template('snmpwalker_result.html')




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
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
