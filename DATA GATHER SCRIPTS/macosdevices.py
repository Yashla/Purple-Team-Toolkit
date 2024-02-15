import paramiko

# SSH connection parameters
hostname = '192.168.0.132'   # Replace with the actual hostname or IP of the Mac
username = 'astonmgmt'    # Replace with your username on the Mac
password = 'astonmgmt'    # Replace with your password on the Mac

# Commands to gather information on macOS
commands = [
    'uname -a',                   # Get basic OS information     # Get IP address(es)
    'sw_vers',   # Get macOS version information
    'whoami',   
]

try:
    # Create SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Connect using username and password
    client.connect(hostname, username=username, password=password)

    for cmd in commands:
        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"Output of '{cmd}':")
        print(stdout.read().decode('utf-8'))

    client.close()

except Exception as e:
    print(f"An error occurred: {e}")