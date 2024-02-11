import nmap

def scan_network_and_detect_os(network='192.168.0.0/24'):
    # Create a new Nmap scanner object
    nm = nmap.PortScanner()

    print(f"Scanning the network {network} for active hosts...")
    # Perform a simple ping scan to discover active hosts
    nm.scan(hosts=network, arguments='-sn')

    active_hosts = nm.all_hosts()
    print(f"Found {len(active_hosts)} active hosts. Performing OS detection...")

    for host in active_hosts:
        print(f"\nScanning {host} for OS details...")
        try:
            # Perform an OS detection scan on each active host
            nm.scan(host, arguments='-O')

            if 'osmatch' in nm[host] and nm[host]['osmatch']:
                for osmatch in nm[host]['osmatch']:
                    print(f"Host: {host}")
                    print(f"OS Name: {osmatch['name']}, Accuracy: {osmatch['accuracy']}")
                    for osclass in osmatch['osclass']:
                        print(f"  OS Class Type: {osclass['type']}")
                        print(f"  OS Vendor: {osclass['vendor']}")
                        print(f"  OS Family: {osclass['osfamily']}")
                        print(f"  OS Generation: {osclass['osgen']}")
                        print(f"  OS Accuracy: {osclass['accuracy']}")
            else:
                print(f"No OS matches found for {host}.")
        except nmap.PortScannerError as e:
            print(f"Scan error for {host}: {e}")
        except Exception as e:
            print(f"Unexpected error for {host}: {e}")

if __name__ == "__main__":
    # Example usage: scan a network segment
    network_address = input("Enter the network address to scan (e.g., 192.168.0.0/24): ")
    scan_network_and_detect_os(network_address)
