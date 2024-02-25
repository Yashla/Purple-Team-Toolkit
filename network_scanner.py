import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor
from zeroconf import Zeroconf, ServiceBrowser, ServiceListener
import time
import  winrm
from winrm.exceptions import WinRMTransportError
from flask_sqlalchemy import SQLAlchemy
import paramiko
from paramiko.ssh_exception import AuthenticationException, SSHException
from models import DeviceInfo
from extensions import db





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


    
        
    def get_windows_os_info(device):
        try:
            windows_host = f'http://{device.ip_address}:5985/wsman'
            session = winrm.Session(windows_host, auth=(device.username, device.password), transport='basic')

            # PowerShell script to get the Product with specific format
            ps_script_product = """
            $product = "Windows_" + ((Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion').CurrentMajorVersionNumber) + "_" + ((Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion').DisplayVersion)
            Write-Output $product
            """
            result_product = session.run_ps(ps_script_product)
            Product = result_product.std_out.decode().strip().lower() if result_product.status_code == 0 else "Error fetching Product"
            
            # PowerShell script to get the Version
            ps_script_version = """
            $version = ((Get-WmiObject Win32_OperatingSystem).Version + "." + (Get-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion").UBR)
            Write-Output $version
            """
            result_version = session.run_ps(ps_script_version)
            Version = result_version.std_out.decode().strip().lower() if result_version.status_code == 0 else "Error fetching Version"
            
            Vendor = "microsoft"

            return Vendor, Product, Version
        except Exception as e:
            return "Error", f"An unexpected error occurred: {str(e)}", ""



    def get_linux_os_info(device):
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=device.ip_address, username=device.username, password=device.password)
            
            # Command to check if the OS is Ubuntu
            check_ubuntu_cmd = "if grep -q '^NAME=\"Ubuntu\"' /etc/os-release; then echo 'ubuntu_linux'; fi"
            stdin, stdout, stderr = ssh_client.exec_command(check_ubuntu_cmd)
            Product = stdout.read().decode().strip().lower()
            
            # Command to get the VERSION_ID
            get_version_cmd = "cat /etc/os-release | grep '^VERSION_ID=' | cut -d'=' -f2 | tr -d '\"'"
            stdin, stdout, stderr = ssh_client.exec_command(get_version_cmd)
            Version = stdout.read().decode().strip().lower() or "Error fetching Version"
            
            Vendor = "canonical"
            
            ssh_client.close()
            return Vendor, Product, Version
        except Exception as e:
            return "Error", f"An unexpected error occurred: {str(e)}", ""


    def get_mac_os_info(device):
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=device.ip_address, username=device.username, password=device.password)
            
            # Separate commands for ProductName and ProductVersion
            product_name_command = "sw_vers | awk '/ProductName/{print $2}'"
            stdin, stdout, stderr = ssh_client.exec_command(product_name_command)
            Product = stdout.read().decode().strip().lower() if not stderr.read().decode().strip() else "Error fetching ProductName"
            
            product_version_command = "sw_vers | awk '/ProductVersion/{print $2}'"
            stdin, stdout, stderr = ssh_client.exec_command(product_version_command)
            Version = stdout.read().decode().strip().lower() if not stderr.read().decode().strip() else "Error fetching ProductVersion"
            
            Vendor = "apple"
            
            ssh_client.close()
            return Vendor, Product, Version
        except Exception as e:
            return "Error", f"An unexpected error occurred: {str(e)}", ""






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
