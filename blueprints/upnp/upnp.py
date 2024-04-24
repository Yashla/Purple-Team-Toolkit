import re
import socket
import json
import requests
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import base64
import struct

#converted code into json

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
                # Fetch and parse SCPD (Service Control Protocol Definition)
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


def find_port_mappings_json(p_url, p_service):
    index = 0
    mappings = []
    while True:
        payload = ('<?xml version="1.0" encoding="utf-8" standalone="yes"?>' +
                   '<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">' +
                   '<s:Body>' +
                   '<u:GetGenericPortMappingEntry xmlns:u="' + p_service + '">' +
                   '<NewPortMappingIndex>' + str(index) + '</NewPortMappingIndex>' +
                   '</u:GetGenericPortMappingEntry>' +
                   '</s:Body>' +
                   '</s:Envelope>')

        soapActionHeader = {'Soapaction': '"' + p_service + '#GetGenericPortMappingEntry' + '"',
                            'Content-type': 'text/xml;charset="utf-8"'}
        resp = requests.post(p_url, data=payload, headers=soapActionHeader)

        if resp.status_code != 200:
            break

        try:
            xmlRoot = ET.fromstring(resp.text)
            externalIP = xmlRoot.find(".//*NewRemoteHost").text or '*'
            mapping = {
                "Protocol": xmlRoot.find(".//*NewProtocol").text,
                "External IP": externalIP,
                "External Port": xmlRoot.find(".//*NewExternalPort").text,
                "Internal Client": xmlRoot.find(".//*NewInternalClient").text,
                "Internal Port": xmlRoot.find(".//*NewInternalPort").text,
                "Description": xmlRoot.find(".//*NewPortMappingDescription").text
            }
            mappings.append(mapping)
        except ET.ParseError:
            print('\t\t[!] Failed to parse the response XML')
            break

        index += 1

    return json.dumps(mappings)


def find_directories_json(p_url, p_service):
    directories = []
    payload = ('<?xml version="1.0" encoding="utf-8" standalone="yes"?>' +
               '<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">' +
               '<s:Body>' +
               '<u:Browse xmlns:u="' + p_service + '">' +
               '<ObjectID>0</ObjectID>' +
               '<BrowseFlag>BrowseDirectChildren</BrowseFlag>' +
               '<Filter>*</Filter>' +
               '<StartingIndex>0</StartingIndex>' +
               '<RequestedCount>10</RequestedCount>' +
               '<SortCriteria></SortCriteria>' +
               '</u:Browse>' +
               '</s:Body>' +
               '</s:Envelope>')

    soapActionHeader = {'Soapaction': '"' + p_service + '#Browse' + '"',
                        'Content-type': 'text/xml;charset="utf-8"'}
    resp = requests.post(p_url, data=payload, headers=soapActionHeader)
    if resp.status_code != 200:
        print('\t\tRequest failed with status: %d' % resp.status_code)
        return json.dumps({"error": "Request failed with status: {}".format(resp.status_code)})

    try:
        xmlRoot = ET.fromstring(resp.text)
        containers = xmlRoot.find(".//*Result").text
        if containers:
            containersXml = ET.fromstring(containers)
            for container in containersXml.findall("./{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}container"):
                class_type = container.find("./{urn:schemas-upnp-org:metadata-1-0/upnp/}class").text
                if "object.container" in class_type:
                    directory = {
                        "ID": container.attrib['id'],
                        "Title": container.find("./{http://purl.org/dc/elements/1.1/}title").text,
                        "Class Type": class_type
                    }
                    directories.append(directory)
    except ET.ParseError:
        print('\t\t[!] Failed to parse the response XML')
        return json.dumps({"error": "Failed to parse response XML"})

    return json.dumps(directories)


def find_device_info_json(p_url, p_service):
    device_info = {}
    payload = ('<?xml version="1.0" encoding="utf-8" standalone="yes"?>' +
               '<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">' +
               '<s:Body>' +
               '<u:GetDeviceInfo xmlns:u="' + p_service + '">' +
               '</u:GetDeviceInfo>' +
               '</s:Body>' +
               '</s:Envelope>')

    soapActionHeader = {'Soapaction': '"' + p_service + '#GetDeviceInfo' + '"',
                        'Content-type': 'text/xml;charset="utf-8"'}
    resp = requests.post(p_url, data=payload, headers=soapActionHeader)
    if resp.status_code != 200:
        print('\t[-] Request failed with status: %d' % resp.status_code)
        return json.dumps({"error": "Request failed with status: {}".format(resp.status_code)})

    info_regex = re.compile("<NewDeviceInfo>(.+)</NewDeviceInfo>", re.IGNORECASE)
    encoded_info = info_regex.search(resp.text)
    if not encoded_info:
        print('\t[-] Failed to find the device info')
        return json.dumps({"error": "Failed to find device info"})

    info = base64.b64decode(encoded_info.group(1))
    while info:
        try:
            type, length = struct.unpack('!HH', info[:4])
            value = info[4:4+length].decode()
            info = info[4+length:]

            if type == 0x1023:
                device_info['Model Name'] = value
            elif type == 0x1021:
                device_info['Manufacturer'] = value
            elif type == 0x1011:
                device_info['Device Name'] = value
            elif type == 0x1020:
                device_info['MAC Address'] = ':'.join('%02x' % ord(char) for char in value)
            elif type == 0x1032:
                device_info['Public Key'] = base64.b64encode(value).decode()
            elif type == 0x101a:
                device_info['Nonce'] = base64.b64encode(value).decode()
        except struct.error:
            print("\t[!] Failed TLV parsing")
            break  # Exiting on a parsing error

    return json.dumps(device_info)

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
    print('[+] Discovering UPnP locations')
    locations_json = discover_pnp_locations_json()
    locations = json.loads(locations_json)['locations']
    print('[+] Discovery complete')
    print('[+] %d locations found:' % len(locations))
    for location in locations:
        print('\t-> %s' % location)

    devices_json = parse_locations_json(locations)
    devices_info = json.loads(devices_json)
    print('[+] Loaded device information from locations.')
    for device in devices_info:
        print(json.dumps(device, indent=4))

    print("[+] Fin.")
    
    upnp_dict = {
        "locations" : locations,
        "devices_info" : devices_info
    }
    return upnp_dict


if __name__ == "__main__":
    main()



