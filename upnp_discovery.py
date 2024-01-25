import upnpclient

def discover_upnp_devices():
    devices = upnpclient.discover()
    device_info = []
    for device in devices:
        device_info.append({
            'name': device.friendly_name,
            'location': device.location,
            'manufacturer': device.manufacturer,
            'model_name': device.model_name
        })
    return device_info