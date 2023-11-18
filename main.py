import asyncio
from pysnmp.hlapi.asyncio import (
    SnmpEngine,
    CommunityData,
    getCmd,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity
)
import socket

def check_snmp_port(ip):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(1)
            s.connect((ip, 161))
            # UDP is connectionless, so connect() doesn't really establish a connection
            # This is mainly to check if the destination is reachable
        return True
    except socket.error:
        return False

async def get_multi_oids(snmpDispatcher, hostname, community_string, oids):
    var_binds = []

    for oid in oids:
        errorIndication, errorStatus, errorIndex, var_bind = await getCmd(
            snmpDispatcher,
            CommunityData(community_string),
            UdpTransportTarget((hostname, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )

        if errorIndication:
            print(f"Error for OID {oid}: {errorIndication}")
        elif errorStatus:
            print(f"Error for OID {oid}: {errorStatus.prettyPrint()}")
        else:
            var_binds.append(var_bind)

    return var_binds
def main():
    # Get user input for the target device's IP address and community string
    target_ip = input("Enter the IP address of the target device: ")
    community_string = input("Enter the community string: ")  # Securely collect the community string

    # Get user input for a comma-separated list of OIDs in numeric format
    oids_input = input("Enter a comma-separated list of OIDs in numeric format: ")
    oids = [oid.strip() for oid in oids_input.split(',')]

    snmpDispatcher = SnmpEngine()
    loop = asyncio.get_event_loop()

    # Check if the target device has an open SNMP port
    if check_snmp_port(target_ip):
        # Retrieve and display SNMP GET results for the specified OIDs
        results = loop.run_until_complete(get_multi_oids(snmpDispatcher, target_ip, community_string, oids))

        print(f"SNMP GET Results for {target_ip}:")
        for result in results:
            for oid, val in result:
                print(f"{oid.prettyPrint()}: {val.prettyPrint()}")

    else:
        print(f"No open SNMP port found on {target_ip}.")

    loop.close()

if __name__ == "main":
    main()