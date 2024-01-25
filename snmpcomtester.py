from pysnmp.hlapi import SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity, getCmd
import concurrent.futures

def test_snmp_community_string(ip_address, community):
    errorIndication, _, _, _ = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip_address, 161)),
               ContextData(),
               ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))
    )

    return community, not bool(errorIndication)

def test_snmp_community_strings(ip_address, community_strings):
    results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit SNMP requests concurrently
        futures = {executor.submit(test_snmp_community_string, ip_address, community): community for community in community_strings}

        # Wait for all requests to complete
        concurrent.futures.wait(futures)

        # Get the results
        for future in futures:
            community, passed = future.result()
            results[community] = passed

    return results

if __name__ == "__main__":
    ip = input("Enter the IP address of the SNMP server: ")
    community_strings_input = input("Enter the community strings separated by commas (e.g., 'public,admin,shreya,aston'): ")
    community_strings = [cs.strip() for cs in community_strings_input.split(',')]
    results = test_snmp_community_strings(ip, community_strings)

    print("Results:")
    for community, passed in results.items():
        if passed:
            print(f"{community} = pass")
        else:
            print(f"{community} = fail")
    
    if all(results.values()):
        print("All community strings passed!")
    elif not any(results.values()):
        print("All community strings failed!")
    else:
        print("Some community strings passed, and some failed.")
