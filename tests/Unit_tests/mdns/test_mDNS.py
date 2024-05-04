import unittest
from blueprints.mdns.discover_mdnss import discover_services

class TestRealMDNSServiceDiscovery(unittest.TestCase):

    def test_discover_services(self):
        # Define the service type for RAOP (Remote Audio Output Protocol)
        service_types = ["_raop._tcp.local."]
        # Discover services for 10 seconds
        discovered_services = discover_services(service_types, duration=10)
        # Print the discovered services
        print("Discovered RAOP Services:", discovered_services)

# Running the test
if __name__ == '__main__':
    unittest.main()
