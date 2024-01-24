from pysnmp.hlapi import nextCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity

def snmp_walk(ip_address, community, oids):
    oid_result = {
        "ip_addr" : ip_address,
        "community_string": community,
        "oids" : {}
    } # Created a dictionary to store all the OIDs with Their Results
    for oid in oids:
        print(f"Querying OID: {oid}")
        response_received = False

        for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((ip_address, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
            lexicographicMode=False  # Stop walking at the end of the subtree
        ):
            if errorIndication:
                print(errorIndication)
                oid_result["oids"][f"{oid}"] = errorIndication #Storing the OID along with the message received in a dictionary
                break
            elif errorStatus:
                print('%s at %s' % (errorStatus.prettyPrint(),
                                    errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))

                oid_result["oids"][f"{oid}"] = '%s at %s' % (errorStatus.prettyPrint(),
                                    errorIndex and varBinds[int(errorIndex) - 1][0] or '?') #Storing the OID along with the message received in a dictionary
                break
            else:
                for varBind in varBinds:
                    response_received = True
                    print('.'.join([str(x) for x in varBind[0]]), '=', varBind[1].prettyPrint())
                    oid_result["oids"][f"{oid}"] = f"{'.'.join([str(x) for x in varBind[0]])} = {varBind[1].prettyPrint()}" #Storing the OID along with the message received in a dictionary

        if not response_received:
            print(f"{oid} = [no response check OID]")
            oid_result["oids"][f"{oid}"] = f"{oid} = [no response check OID]" #Storing the OID along with the message received in a dictionary
    
    print(oid_result)
    return oid_result # Returning the OID Results to be used by Flask

if __name__ == "__main__":
    ip = input("Enter the IP address of the SNMP device: ")
    community_string = input("Enter the community string (e.g., 'public'): ")
    oids_input = input("Enter OIDs separated by commas (e.g., '1.3.6.1.2.1.1.5, 1.3.6.1.2.1.1.6): ")
    oids = [oid.strip() for oid in oids_input.split(', ')]
    snmp_walk(ip, community_string, oids)
