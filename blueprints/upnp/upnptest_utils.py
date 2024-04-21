import re
import socket
import json
import requests
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import base64
import struct
import sys

def safe_parse_location(url):
    try:
        response = requests.get(url, timeout=2)
        # Check if the content type is XML
        if response.status_code == 200 and 'application/xml' in response.headers.get('Content-Type', ''):
            return ET.fromstring(response.text)
        else:
            print(f"[!] No valid XML returned from {url}")
    except requests.exceptions.RequestException as e:
        print(f"[!] HTTP request failed for {url}: {str(e)}")
    except ET.ParseError as e:
        print(f"[!] Failed XML parsing of {url} due to {str(e)}")
    return None

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
    except socket.timeout:
        print("[!] Discovery timeout: No more responses received.")
    except socket.error as e:
        print(f"[!] Socket error: {str(e)}")
    finally:
        sock.close()

    return json.dumps({"locations": locations})

def get_attribute(xml, xml_name, print_name):
    """
    Extracts text from an XML element and returns it in a dictionary.
    
    Args:
    xml (ElementTree.Element): The XML tree or subtree to search within.
    xml_name (str): The XPath to the element to find.
    print_name (str): The key under which the found text is stored in the result dictionary.

    Returns:
    dict: A dictionary containing the requested text under the specified key, or None if not found.
    """
    result = {}
    element = xml.find(xml_name)
    if element is not None and element.text is not None:
        result[print_name] = element.text
    else:
        result[print_name] = None  # Could log specific cases here if needed
    return result

def parse_locations_json(locations):
    devices_info = []
    for location in locations:
        print('[+] Loading %s...' % location)
        xmlRoot = safe_parse_location(location)
        if xmlRoot is None:
            continue  # Skip this location due to XML parsing issues
        
        device_data = {'Location': location, 'Services': []}
        device_data['Server String'] = xmlRoot.find("./device/server").text if xmlRoot.find("./device/server") is not None else "No server string"

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
                'API': urlparse(location).scheme + "://" + urlparse(location).netloc + service.find('{urn:schemas-upnp-org:device-1-0}SCPDURL').text,
                'Actions': []
            }
            scp_xml = safe_parse_location(service_data['API'])
            if scp_xml is not None:
                actions = scp_xml.findall(".//*{urn:schemas-upnp-org:service-1-0}action")
                for action in actions:
                    service_data['Actions'].append(action.find('{urn:schemas-upnp-org:service-1-0}name').text)
                device_data['Services'].append(service_data)

        devices_info.append(device_data)

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
        try:
            resp = requests.post(p_url, data=payload, headers=soapActionHeader)
            if resp.status_code == 200:
                xmlRoot = ET.fromstring(resp.text)
                if xmlRoot.find(".//*NewProtocol") is None:
                    break  # Assuming no more mappings are available if certain tags are missing

                mapping = {
                    "Protocol": xmlRoot.find(".//*NewProtocol").text,
                    "External IP": xmlRoot.find(".//*NewRemoteHost").text or '*',
                    "External Port": xmlRoot.find(".//*NewExternalPort").text,
                    "Internal Client": xmlRoot.find(".//*NewInternalClient").text,
                    "Internal Port": xmlRoot.find(".//*NewInternalPort").text,
                    "Description": xmlRoot.find(".//*NewPortMappingDescription").text
                }
                mappings.append(mapping)
            else:
                print(f"[!] HTTP Error {resp.status_code} for index {index}: {resp.reason}")
                break
        except requests.exceptions.RequestException as e:
            print(f"[!] Request failed: {str(e)}")
            break
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
    try:
        resp = requests.post(p_url, data=payload, headers=soapActionHeader)
        if resp.status_code == 200:
            xmlRoot = ET.fromstring(resp.text)
            containers = xmlRoot.find(".//*Result").text
            if containers:
                containersXml = ET.fromstring(containers)
                for container in containersXml.findall(".//{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}container"):
                    class_type = container.find(".//{urn:schemas-upnp-org:metadata-1-0/upnp/}class").text
                    if "object.container" in class_type:
                        directory = {
                            "ID": container.attrib['id'],
                            "Title": container.find(".//{http://purl.org/dc/elements/1.1/}title").text,
                            "Class Type": class_type
                        }
                        directories.append(directory)
        else:
            print(f'[!] Request failed with status: {resp.status_code} - {resp.reason}')
            return json.dumps({"error": f"Request failed with status: {resp.status_code}"})
    except requests.exceptions.RequestException as e:
        print(f'[!] Request failed: {str(e)}')
        return json.dumps({"error": "Request exception occurred"})
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
    try:
        resp = requests.post(p_url, data=payload, headers=soapActionHeader)
        if resp.status_code == 200:
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
        else:
            print(f'\t[-] Request failed with status: {resp.status_code}')
            return json.dumps({"error": f"Request failed with status: {resp.status_code}"})
    except requests.exceptions.RequestException as e:
        print(f'\t[-] Request exception: {str(e)}')
        return json.dumps({"error": "Network request failed"})

    return json.dumps(device_info)

def main(argv):
    output_data = {
        "discovery": {},
        "device_details": []
    }

    print('[+] Discovering UPnP locations')
    try:
        locations_json = discover_pnp_locations_json()
        locations = json.loads(locations_json)['locations']
        output_data['discovery']['locations'] = locations
        print('[+] Discovery complete')
        print('[+] %d locations found:' % len(locations))
        for location in locations:
            print('\t-> %s' % location)

        devices_json = parse_locations_json(locations)
        devices_info = json.loads(devices_json)
        output_data['device_details'] = devices_info
        print('[+] Loaded device information from locations.')
        for device in devices_info:
            print(json.dumps(device, indent=4))
    except Exception as e:
        print(f'[!] An error occurred during UPnP discovery or processing: {str(e)}')

    print("[+] Fin.")
    return output_data

if __name__ == "__main__":
    result = main(sys.argv)
    print(json.dumps(result, indent=4))  # Print the final JSON output that you would pass to your web application
