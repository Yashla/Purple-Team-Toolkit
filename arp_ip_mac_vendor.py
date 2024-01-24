from scapy.all import ARP, Ether, srp
import requests
import time

def get_mac_vendor(mac_address):
    url = f'https://api.macvendors.com/{mac_address}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return 'Unknown'
    except requests.RequestException:
        return 'The request didnt make it to the API'

def arp(t_ip):
    arp = ARP(pdst=t_ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    result = srp(packet, timeout=1, verbose=0)[0]
    clients = []

    for sent, received in result:
        mac_vendor = get_mac_vendor(received.hwsrc)
        clients.append({
            'ip': received.psrc,
            'mac': received.hwsrc,
            'vendor': mac_vendor
        })
        time.sleep(1)  # Wait for 1 seconds before the next request

        print("Available devices in the network:")
        print("IP" + " "*18 + "MAC" + " "*18 + "Vendor")
        

        for client in clients:
         print("{:<16}    {:<18}    {}".format(client['ip'], client['mac'], client['vendor']))


    return clients 

if __name__ == "__main__":
    t_ip = input("Enter the network address with subnet mask to scan (e.g., 192.168.0.1/24): ")