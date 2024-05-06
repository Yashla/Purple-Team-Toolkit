import unittest
from blueprints.cve_scanner.network_scanner import NetworkScanner
from models import Device

class TestNetworkScanner(unittest.TestCase):

    def test_get_mac_os_info(self):
        # Device credentials for a Mac device
        device_ip = '192.168.0.132'  # Replace with the actual Mac device IP address
        device_username = 'Yash'  # Replace with the actual Mac username
        device_password = 'test'  # Replace with the actual Mac password

        # Create a new device instance for a Mac device
        new_device = Device(
            ip_address=device_ip,
            device_type='mac',
            username=device_username,
            password=device_password
        )

        # Call the method with the new_device instance
        vendor, product, version = NetworkScanner.get_mac_os_info(new_device)

        # Print out the Vendor, Product, and Version information for Mac
        print("\nMac Device:")
        print("Vendor:", vendor)
        print("Product:", product)
        print("Version:", version)

    def test_get_linux_os_info(self):
        # Device credentials for a Linux device
        device_ip = '192.168.0.188'  # Replace with the actual Linux device IP address
        device_username = 'test'  # Replace with the actual Linux username
        device_password = 'test'  # Replace with the actual Linux password

        # Create a new device instance for a Linux device
        new_device = Device(
            ip_address=device_ip,
            device_type='linux',
            username=device_username,
            password=device_password
        )

        # Call the method with the new_device instance
        vendor, product, version = NetworkScanner.get_linux_os_info(new_device)

        # Print out the Vendor, Product, and Version information for Linux
        print("\nLinux Device:")
        print("Vendor:", vendor)
        print("Product:", product)
        print("Version:", version)

    def test_get_windows_os_info(self):
        print("\nStarting test for Windows device...")
        device_ip = '192.168.0.4'  # Replace with the actual Windows device IP address
        device_username = 'yash'  # Replace with the actual Windows username
        device_password = 'test'  # Replace with the actual Windows password

        # Create a new device instance for a Windows device
        new_device = Device(
            ip_address=device_ip,
            device_type='windows',
            username=device_username,
            password=device_password
        )


        vendor, product, version = NetworkScanner.get_windows_os_info(new_device)


        print("Windows Device:")
        print("Vendor:", vendor)
        print("Product:", product)
        print("Version:", version)

if __name__ == '__main__':
    unittest.main()