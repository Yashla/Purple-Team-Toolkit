import sys
from pysnmp.hlapi import nextCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity

def snmp_walk(ip_address, community, oids):
    for oid in oids:
        print(f"Querying OID: {oid}", flush=True)
        response_received = False

        for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((ip_address, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
            lexicographicMode=False
        ):
            if errorIndication:
                print(errorIndication, flush=True)
                break
            elif errorStatus:
                print('%s at %s' % (errorStatus.prettyPrint(),
                                    errorIndex and varBinds[int(errorIndex) - 1][0] or '?'), flush=True)
                break
            else:
                for varBind in varBinds:
                    response_received = True
                    print('.'.join([str(x) for x in varBind[0]]), '=', varBind[1].prettyPrint(), flush=True)

        if not response_received:
            print(f"{oid} = [no response check OID]", flush=True)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python snmpwalker.py <IP address> <community string> <OIDs comma-separated>")
        sys.exit(1)

    ip = sys.argv[1]
    community_string = sys.argv[2]
    oids_input = sys.argv[3]
    oids = [oid.strip() for oid in oids_input.split(',')]
    snmp_walk(ip, community_string, oids)
