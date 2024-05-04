import unittest
from blueprints.arp.Arp_scanner import get_mac_vendor, perform_arp_scan

class TestARPScannerFunctions(unittest.TestCase):

    def test_perform_arp_scan(self):
        # Warning: This test will perform an ARP scan on the specified network
        target_ip = '192.168.0.0/24'  # Example subnet
        results = perform_arp_scan(target_ip)
        
        # Print the results of the ARP scan
        print(f"ARP Scan Results for network {target_ip}:")
        for result in results:
            print(result)
        
        # Check the result is a list and has at least one entry
        self.assertIsInstance(results, list, "Results should be a list")
        if results:
            # Assuming each result is a dictionary with 'ip' and 'mac' keys
            self.assertIn('ip', results[0], "Each entry should have an 'ip' key")
            self.assertIn('mac', results[0], "Each entry should have a 'mac' key")

# Running the test
if __name__ == '__main__':
    unittest.main()
