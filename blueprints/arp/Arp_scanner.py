from scapy.all import ARP, Ether, srp
import requests
from time import sleep

def get_mac_vendor(mac_address):
    url = f'https://api.macvendors.com/{mac_address}'
    try:
        response = requests.get(url)
        return response.text if response.status_code == 200 else 'Unknown'
    except requests.RequestException:
        return 'API Request Failed'

def perform_arp_scan(target_ip):
    arp_request = ARP(pdst=target_ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    clients = []
    for sent, received in answered_list:
        clients.append({'ip': received.psrc, 'mac': received.hwsrc})

    results = "IP" + " " * 18 + "MAC" + " " * 18 + "Vendor\n"
    results += "--------------------------------------------------\n"

    for client in clients:
        vendor = get_mac_vendor(client['mac'])
        client["vendor"] = vendor
        results += "{:<16}    {:<18}    {}\n".format(client['ip'], client['mac'], vendor)
        sleep(1)
    return clients
