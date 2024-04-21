from pysnmp.hlapi import nextCmd, setCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity
import os
from datetime import datetime 

def snmp_walk(ip_address, community, oids):
    oid_results = {
        "ip_addr": ip_address,
        "community_string": community,
        "oids": {}
    }
    success = True  # Maintain overall success status
    last_file_path = None

    now = datetime.now()
    timestamp = now.strftime("%d_%m_%Y_%H:%M:%S")

    for oid in oids:
        sanitized_oid = oid.replace('.', '_')
        filename = f"{ip_address.replace('.', '_')}_Walker_{sanitized_oid}_{timestamp}.txt"
        filepath = filename  # Adjust path as needed
        last_file_path = filepath  # Update last file path

        try:
            with open(filepath, 'w') as file:
                file.write(f"Community String Used: {community}\n\n")

                for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
                    SnmpEngine(),
                    CommunityData(community),
                    UdpTransportTarget((ip_address, 161)),
                    ContextData(),
                    ObjectType(ObjectIdentity(oid)),
                    lexicographicMode=False
                ):
                    if errorIndication:
                        file.write(f"{oid} Error: {str(errorIndication)}\n")
                        oid_results["oids"][oid] = f"Error: {str(errorIndication)}"
                        continue  # Skip to next iteration, not breaking the loop
                    elif errorStatus:
                        error_message = f"{oid} Error: {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}"
                        file.write(error_message + "\n")
                        oid_results["oids"][oid] = f"Error: {error_message}"
                        continue  # Skip to next iteration, not breaking the loop
                    else:
                        for varBind in varBinds:
                            result = f"{'.'.join([str(x) for x in varBind[0]])} = {varBind[1].prettyPrint()}"
                            file.write(result + "\n")
                            if oid not in oid_results["oids"]:
                                oid_results["oids"][oid] = []
                            oid_results["oids"][oid].append(result)

        except Exception as e:
            print(f"Failed to write to file {filepath}: {str(e)}")
            success = False

    return {'file_path': last_file_path, 'success': success}

def snmp_set(ip_address, community, oid, value_type, value):
    """
    Set an SNMP OID to a specified value on a target device.

    Args:
    ip_address (str): The IP address of the SNMP agent (device).
    community (str): The community string for SNMP authentication.
    oid (str): The OID that needs to be set.
    value_type (str): The type of the value ('int' or 'str').
    value: The value to set the OID to.

    Returns:
    str: Result message indicating success or failure.
    """
    # Convert the value based on the specified value_type
    if value_type == 'int':
        try:
            value = int(value)  # Attempt to convert value to an integer if 'int' is specified
        except ValueError:
            return "Error: Value type 'int' specified, but the provided value could not be converted to an integer."
    elif value_type == 'str':
        value = str(value)  # Ensure the value is treated as a string if 'str' is specified
    else:
        return f"Unsupported value type '{value_type}'. Supported types are 'int' and 'str'."

    # Prepare the SNMP set command
    errorIndication, errorStatus, errorIndex, varBinds = next(
        setCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((ip_address, 161), timeout=3, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity(oid), value)
        )
    )

    # Check for SNMP errors
    if errorIndication:
        return f"Error: {errorIndication}"
    elif errorStatus:
        return f"Error: {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}"
    else:
        return f"Success: {oid} set to {value}"

if __name__ == "__main__":
    action = input("Enter 'walk' to perform SNMP walk or 'set' to set an OID value: ").lower()
    if action == 'set':
        ip = input("Enter the IP address of the SNMP device: ")
        community_string = input("Enter the community string (e.g., 'public'): ")
        oid = input("Enter the OID you want to set (e.g., '1.3.6.1.2.1.1.6.0'): ")
        value_type = input("Enter the type of the value (e.g., 'int', 'str'): ")
        value = input("Enter the value you want to set: ")

        # Ensure value_type is passed as a string
        if value_type not in ['int', 'str']:
            print("Unsupported value type. Supported types are 'int' and 'str'.")
        else:
            result_message = snmp_set(ip, community_string, oid, value_type, value)
            print(result_message)
