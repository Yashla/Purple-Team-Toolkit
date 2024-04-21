import requests
from xml.etree import ElementTree
import sys

def send_soap_request(ip, service_type, control_url, action, soap_body):
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": f"\"urn:schemas-upnp-org:service:{service_type}#{action}\""
    }
    url = f"http://{ip}:5000{control_url}"
    response = requests.post(url, data=soap_body, headers=headers)
    print("SOAP Response:")
    print(response.text)  # Print the raw SOAP response for debugging
    return response.text

def get_external_ip_address(ip):
    soap_body = '''<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body>
        <u:GetExternalIPAddress xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1">
        </u:GetExternalIPAddress>
    </s:Body>
</s:Envelope>'''
    response = send_soap_request(ip, "WANIPConnection:1", "/ctl/IPConn", "GetExternalIPAddress", soap_body)
    try:
        tree = ElementTree.fromstring(response)
        # Check for a SOAP Fault
        fault = tree.find('.//s:Fault', namespaces={'s': 'http://schemas.xmlsoap.org/soap/envelope/'})
        if fault is not None:
            print("Fault found in the SOAP response:")
            print(ElementTree.tostring(fault, encoding='utf8').decode('utf8'))
            return None

        namespace = {'u': 'urn:schemas-upnp-org:service:WANIPConnection:1'}
        external_ip_element = tree.find('.//u:NewExternalIPAddress', namespace)
        if external_ip_element is not None:
            return external_ip_element.text
        else:
            print("No External IP Address found in the response.")
            return None
    except ElementTree.ParseError:
        print("Failed to parse XML response.")
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    if len(sys.argv) < 3:
        print("Usage: python script.py <IP Address> <Action>")
        sys.exit(1)
    
    ip_address = sys.argv[1]
    action = sys.argv[2]

    if action == "GetExternalIPAddress":
        external_ip = get_external_ip_address(ip_address)
        if external_ip:
            print(f"External IP Address: {external_ip}")
        else:
            print("Unable to retrieve the External IP Address.")
    else:
        print("Unsupported action.")

if __name__ == "__main__":
    main()
