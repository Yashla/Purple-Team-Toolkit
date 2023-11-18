import upnpclient


def discover_upnp_devices():
    devices = upnpclient.discover()
    return devices

if __name__ == "__main__":
    print("Scanning for UPnP devices...")
    upnp_devices = discover_upnp_devices()

    if upnp_devices:
        print("Found UPnP devices:")
        for device in upnp_devices:
            print(f"Device Name: {device.friendly_name}")
            print(f"Location: {device.location}")
            print(f"Manufacturer: {device.manufacturer}")
            print(f"Model Name: {device.model_name}")
            print("\n")
    else:
        print("No UPnP devices found on the network.")
