import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor
from zeroconf import Zeroconf, ServiceBrowser, ServiceListener
import paramiko
import time


# Define a class to hold the discovered IP addresses
class NetworkScanner:
    def __init__(self):
        self.windows_array = []
        self.linux_array = []
        self.macbook_array = []

    class MyListener(ServiceListener):
        def __init__(self, scanner):
            self.scanner = scanner

        def remove_service(self, zeroconf, type, name):
            pass

        def update_service(self, zeroconf, type, name):
            pass

        def add_service(self, zeroconf, type, name):
            info = zeroconf.get_service_info(type, name)
            if info:
                addresses = [socket.inet_ntoa(addr) for addr in info.addresses]
                for address in addresses:
                    if address not in self.scanner.macbook_array:
                        self.scanner.macbook_array.append(address)

    def scan_mdns(self):
        zeroconf = Zeroconf()
        listener = self.MyListener(self)
        browser = ServiceBrowser(zeroconf, "_raop._tcp.local.", listener)
        try:
            time.sleep(10)
        finally:
            zeroconf.close()

    def scan_ip(self, ip):
        for port in [22, 5985]:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((str(ip), port))
                if result == 0:
                    if port == 5985:
                        self.windows_array.append(str(ip))
                    elif port == 22:
                        self.linux_array.append(str(ip))
                    break

    def scan_network(self, subnet):
        network = ipaddress.ip_network(subnet)
        with ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(self.scan_ip, network.hosts())

    def refine_linux_array(self):
        # Refine the Linux array by removing MacBook IP addresses
        for mac_ip in self.macbook_array:
            if mac_ip in self.linux_array:
                self.linux_array.remove(mac_ip)


def ssh_into_device(ip, username, password):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            hostname=ip, username=username, password=password, timeout=10
        )
        # Here you can execute commands or perform operations
        ssh_client.close()
        return True, "Connection successful"
    except Exception as e:
        return False, str(e)


# Example usage within Flask
# scanner = NetworkScanner()
# scanner.scan_network('192.168.1.0/24')
# scanner.scan_mdns()
# scanner.refine_linux_array()
# Now, you can use scanner.windows_array, scanner.linux_array, and scanner.macbook_array as needed


if __name__ == "__main__":
    subnet_to_scan = (
        "192.168.0.0/24"  # Example subnet, change this to the subnet you wish to scan
    )
    scanner = NetworkScanner()
    print("Scanning network...")
    scanner.scan_network(subnet_to_scan)
    print("Scanning for mDNS services...")
    scanner.scan_mdns()
    scanner.refine_linux_array()
    print("Windows Devices:", scanner.windows_array)
    print("Linux Devices:", scanner.linux_array)
    print("MacBook Devices:", scanner.macbook_array)
