from zeroconf import ServiceBrowser, Zeroconf, ServiceListener

class MyListener(ServiceListener):
    def add_service(self, zeroconf, service_type, name):
        info = zeroconf.get_service_info(service_type, name)
        if info:
            print(f"Discovered service: {name}")
            print(f"Type: {service_type}")
            print(f"Address: {info.parsed_addresses()[0]}:{info.port}")
            print(f"Properties: {info.properties}")

    def remove_service(self, zeroconf, service_type, name):
        print(f"Service {name} removed")

    def update_service(self, zeroconf, service_type, name):
        print(f"Service {name} updated")


# Initialize Zeroconf
zeroconf = Zeroconf()
listener = MyListener()

# List of service types you want to discover
service_types = [
    "_http._tcp.local.",
    "_ftp._tcp.local.",
    "_ssh._tcp.local.",
    "_airplay._tcp.local.",
    "_bonjour._tcp.local.",
    "_googlecast._tcp.local.",
    "_dlna._tcp.local.",
    "_raop._tcp.local.",
    
    # Add more services as needed
]

# Create a ServiceBrowser for each service type
browsers = [ServiceBrowser(zeroconf, st, listener) for st in service_types]

try:
    input("Press Enter to exit...\n\n")
finally:
    zeroconf.close()
