import unittest
import time
from blueprints.snmp.snmpwalker import snmp_walk, snmp_set

class TestSNMPIntegration(unittest.TestCase):
    
    def test_snmp_set_and_walk(self):
        # Parameters for the test
        ip_address = "192.168.0.185"  # Change to the actual IP address of your SNMP device
        community = "public"
        set_oid = "1.3.6.1.2.1.1.5.0"  # Example writable OID
        value_type = "str"
        value = "Test Location"

        # Perform SNMP set
        set_result = snmp_set(ip_address, community, set_oid, value_type, value)
        print("SNMP Set Results:", set_result)

        # Wait for 4 seconds before doing the walk
        time.sleep(4)

        # Now perform SNMP walk to confirm changes or check other details
        walk_oids = ["1.3.6.1.2.1.1.5"]  # System OIDs, change based on what you want to test
        walk_result = snmp_walk(ip_address, community, walk_oids)
        print("SNMP Walk Results:", walk_result)

# Running the test
if __name__ == '__main__':
    unittest.main()
