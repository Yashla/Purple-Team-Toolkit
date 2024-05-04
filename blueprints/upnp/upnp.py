import re
import socket
import json
import requests
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import base64
import struct

# converted code into json

def discover_pnp_locations_json():
    locations = []
    location_regex = re.compile("location:[ ]*(.+)\r\n", re.IGNORECASE)
    ssdpDiscover = ('M-SEARCH * HTTP/1.1\r\n' +
                    'HOST: 239.255.255.250:1900\r\n' +
                    'MAN: "ssdp:discover"\r\n' +
                    'MX: 1\r\n' +
                    'ST: ssdp:all\r\n' +
                    '\r\n')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(ssdpDiscover.encode('ASCII'), ("239.255.255.250", 1900))
    sock.settimeout(3)
    try:
        while True:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            location_result = location_regex.search(data.decode('ASCII'))
            if location_result and (location_result.group(1) not in locations):
                locations.append(location_result.group(1))
    except socket.error:
        sock.close()

    return json.dumps({"locations": locations})


def print_attribute_json(xml, xml_name, print_name):
    result = {}
    try:
        temp = xml.find(xml_name).text
        result[print_name] = temp
    except AttributeError:
        result[print_name] = None
    return result

def parse_locations_json(locations):
    devices_info = []
    for location in locations:
        device_data = {'Location': location, 'Services': []}
        print('[+] Loading %s...' % location)
        try:
            resp = requests.get(location, timeout=2)
            device_data['Server String'] = resp.headers.get('server', 'No server string')
            try:
                xmlRoot = ET.fromstring(resp.text)
            except ET.ParseError as e:
                print('\t[!] Failed XML parsing of %s due to %s' % (location, str(e)))
                continue  # Skip to the next location if parsing fails
            parsed = urlparse(location)
            # Extract device attributes
            attributes = [
                ("./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}deviceType", "Device Type"),
                ("./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}friendlyName", "Friendly Name"),
                ("./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}manufacturer", "Manufacturer"),
                ("./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}manufacturerURL", "Manufacturer URL"),
                ("./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}modelDescription", "Model Description"),
                ("./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}modelName", "Model Name"),
                ("./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}modelNumber", "Model Number")
            ]
            for path, name in attributes:
                element = xmlRoot.find(path)
                device_data[name] = element.text if element is not None else "Not available"
            # Extract services and their details
            services = xmlRoot.findall(".//*{urn:schemas-upnp-org:device-1-0}serviceList/{urn:schemas-upnp-org:device-1-0}service")
            for service in services:
                service_data = {
                    'Service Type': service.find('{urn:schemas-upnp-org:device-1-0}serviceType').text,
                    'Control': service.find('{urn:schemas-upnp-org:device-1-0}controlURL').text,
                    'Events': service.find('{urn:schemas-upnp-org:device-1-0}eventSubURL').text,
                    'API': parsed.scheme + "://" + parsed.netloc + service.find('{urn:schemas-upnp-org:device-1-0}SCPDURL').text,
                    'Actions': []
                }
                try:
                    scp_response = requests.get(service_data['API'], timeout=2)
                    scp_xml = ET.fromstring(scp_response.text)
                except ET.ParseError as e:
                    print('\t[!] Failed to parse SCPD of %s due to %s' % (service_data['API'], str(e)))
                    continue

                actions = scp_xml.findall(".//*{urn:schemas-upnp-org:service-1-0}action")
                for action in actions:
                    service_data['Actions'].append(action.find('{urn:schemas-upnp-org:service-1-0}name').text)
                
                device_data['Services'].append(service_data)
            devices_info.append(device_data)
        except requests.exceptions.RequestException as e:
            print('[!] Failed to load %s due to %s' % (location, str(e)))
    return json.dumps(devices_info, indent=4)



def upnp_main():
    locations_json = discover_pnp_locations_json()
    locations = json.loads(locations_json)['locations']
    
    devices_json = parse_locations_json(locations)
    devices_info = json.loads(devices_json)

    upnp_dict = {
        "locations" : locations,
        "devices_info" : devices_info
    }
    return upnp_dict


def main():
    locations_json = discover_pnp_locations_json()
    locations = json.loads(locations_json)['locations']
    devices_json = parse_locations_json(locations)
    devices_info = json.loads(devices_json)
#    for device in devices_info:
#        print(json.dumps(device, indent=4))


    upnp_dict = {
        "locations" : locations,
        "devices_info" : devices_info
    }
    return upnp_dict


if __name__ == "__main__":
    main()
