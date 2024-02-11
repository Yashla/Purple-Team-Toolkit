import paramiko

# SSH connection parameters
hostname = '192.168.0.176'  # Replace with the actual hostname or IP of 'test'
username = 'kali'   # Replace with your username on 'test'
key_file = '/home/yash/.ssh/id_rsa'  # Path to your private key, if using key authentication

# Commands to gather information
commands = [
    'uname -a',              # Get OS information
    'hostname -I',           # Get IP address(es)
    'cat /etc/os-release',   # Get detailed OS release information
]

try:
    # Create SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, key_filename=key_file)

    for cmd in commands:
        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"Output of '{cmd}':")
        print(stdout.read().decode('utf-8'))

    client.close()

except Exception as e:
    print(f"An error occurred: {e}")
