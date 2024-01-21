from pysnmp.hlapi import *

def snmp_get(ip, community, oids):
    for oid in oids:
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(community, mpModel=1),  # Use SNMP v2c (mpModel=1)
                   UdpTransportTarget((ip, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid))
            )
        )
        if errorIndication:
            print(f"SNMP GET request for OID {oid} failed: {errorIndication}")
        elif errorStatus:
            print(f"SNMP GET request for OID {oid} failed: {errorStatus.prettyPrint()}")
        else:
            for varBind in varBinds:
                print(f"{varBind.prettyPrint()}")

if __name__ == "__main__":
    target_ip = "192.168.0.172"  # Replace with the target IP address
    snmp_community = "public"  # Replace with your SNMP community string

    oids_to_get = [
        "1.3.6.1.2.1.1.5",  # System Name (hostname)
       # "", # System Description
       # "1.3.6.1.2.1.25.1.1.0",# uptime
        # Add more OIDs here as needed "1.3.6.1.2.1.1.5",  # System Name (hostname) syslocation 1.3.6.1.2.1.1.6
            ]
    snmp_get(target_ip, snmp_community, oids_to_get)
### hellllo this is the for github