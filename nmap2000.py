import nmap

def os_detection(ip='192.168.0.1'):
    # Create a new Nmap scanner object
    nm = nmap.PortScanner() 

    try:
        # Perform an OS detection scan
        nm.scan(ip, arguments='-O')

        # Check if the IP address had any OS matches
        if 'osmatch' in nm[ip]:
            for osmatch in nm[ip]['osmatch']:
                print(f"OS Name: {osmatch['name']} Accuracy: {osmatch['accuracy']}")
                for osclass in osmatch['osclass']:
                    print(f"  OS Class Type: {osclass['type']}")
                    print(f"  OS Vendor: {osclass['vendor']}")
                    print(f"  OS Family: {osclass['osfamily']}")
                    print(f"  OS Generation: {osclass['osgen']}")
                    print(f"  OS Accuracy: {osclass['accuracy']}")
        else:
            print("No OS matches found.")
    except nmap.PortScannerError as e:
        print(f"Scan error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    os_detection()
