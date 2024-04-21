from zeroconf import ServiceBrowser, Zeroconf, ServiceListener
import time

class MyListener(ServiceListener):
    def __init__(self, services):
        self.services = services

    def add_service(self, zeroconf, service_type, name):
        info = zeroconf.get_service_info(service_type, name)
        if info:
            service_info = {
                'name': name,
                'type': service_type,
                'address': info.parsed_addresses()[0],
                'port': info.port,
                'properties': info.properties
            }
            self.services.append(service_info)

# Make sure this function is at the module level and not within a class
def discover_services(service_types, duration=10):
    discovered_services = []
    zeroconf = Zeroconf()
    listener = MyListener(discovered_services)
    browsers = [ServiceBrowser(zeroconf, st, listener) for st in service_types]

    # Run the discovery for a specified duration
    time.sleep(duration)
    zeroconf.close()
    return discovered_services
