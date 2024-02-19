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
        windows_host = f'http://{device.ip_address}:5985/wsman'
        try:
            session = winrm.Session(windows_host, auth=(device.username, device.password), transport='basic')
            # Updated PowerShell script for cleaner output
            ps_script = "Get-CimInstance Win32_OperatingSystem | ForEach-Object { \"$($_.Caption) $($_.Version)\" }"
            result = session.run_ps(ps_script)
            if result.status_code == 0:
                os_info = result.std_out.decode().strip()  # Successfully got OS info
                
                # Find the corresponding DeviceInfo entry based on device_id
                device_info = DeviceInfo.query.filter_by(device_id=device.id).first()
                if device_info:
                    # Update the os_version with the retrieved OS information
                    device_info.os_version = os_info
                    db.session.commit()
                    return os_info
                else:
                    return "DeviceInfo entry not found for the given device."
            else:
                return "Can't get information as command execution failed. Check the command and try again."
        except winrm.exceptions.WinRMTransportError as e:
            if 'unauthorized' in str(e).lower():
                return "Can't get information as device can't be logged into. Check login details."
            else:
                return "Connection failed due to a transport error. Check device availability and network."
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

    def get_linux_os_info(device):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(hostname=device.ip_address, username=device.username, password=device.password)
            command = "echo $(awk -F= '/^PRETTY_NAME/{print $2}' /etc/os-release | tr -d '\"') $(uname -r)"
            stdin, stdout, stderr = ssh_client.exec_command(command)
            os_info = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            if error:
                return "Can't get information as command execution failed. Check the command and try again."
            
            # Assuming 'device.id' can be directly used to query the DeviceInfo table
            device_info = DeviceInfo.query.filter_by(device_id=device.id).first()
            if device_info:
                # Update the os_version with the retrieved OS information
                device_info.os_version = os_info
                db.session.commit()
                return os_info
            else:
                return "DeviceInfo entry not found for the given device."
            
        except AuthenticationException:
            return "Can't get information as device can't be logged into. Check login details."
        except SSHException as e:
            return f"Connection failed due to an SSH error. Check device availability and network. Error: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"
        finally:
            ssh_client.close()
    
    




    def get_mac_os_info(device):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(hostname=device.ip_address, username=device.username, password=device.password)
            command = "echo $(sw_vers -productName) $(sw_vers -productVersion)"
            stdin, stdout, stderr = ssh_client.exec_command(command)
            os_info = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            if error:
                return "Can't get information as command execution failed. Check the command and try again."
            
            # Assuming 'device.id' can be directly used to query the DeviceInfo table
            device_info = DeviceInfo.query.filter_by(device_id=device.id).first()
            if device_info:
                # Update the os_version with the retrieved OS information
                device_info.os_version = os_info
                db.session.commit()
                return os_info
            else:
                return "DeviceInfo entry not found for the given device."

        except AuthenticationException:
            return "Can't get information as device can't be logged into. Check login details."
        except SSHException as e:
            return f"Connection failed due to an SSH error. Check device availability and network. Error: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"
        finally:
            ssh_client.close()




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
