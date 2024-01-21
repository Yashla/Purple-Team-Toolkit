from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity

def snmp_get(target_ip, community_string, oids):
    for oid in oids:
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(community_string),
                   UdpTransportTarget((target_ip, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid)))
        )

        if errorIndication:
            print(errorIndication)
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            for varBind in varBinds:
                print('.'.join([str(x) for x in varBind[0]]), '=', varBind[1])

# Example usage
target_ip = '192.168.80.140'  # Replace with your target IP
community_string = 'public'  # Replace with your community string
oids = ['1.3.6.1.2.1.1.1', '1.3.6.1.2.1.1.5']  # Replace with your OIDs

snmp_get(target_ip, community_string, oids)
