import paramiko

# SSH connection parameters
hostname = '192.168.0.176'  # Replace with the actual hostname or IP of 'test'
username = 'astonmgmt'   # Replace with your username on 'test'
password = 'astonmgmt'  # Path to your private key, if using key authentication

# Commands to gather information
commands = [
    'uname -a',              # Get OS information
    'whoami',           # Get IP address(es)
    'pwd',   # Get detailed OS release information
]

try:
    # Create SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)

    for cmd in commands:
        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"Output of '{cmd}':")
        print(stdout.read().decode('utf-8'))

    client.close()

except Exception as e:
    print(f"An error occurred: {e}")
