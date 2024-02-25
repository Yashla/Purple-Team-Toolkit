import paramiko
from paramiko.ssh_exception import AuthenticationException, SSHException

class Device:
    def __init__(self, ip_address, username, password):
        self.ip_address = ip_address
        self.username = username
        self.password = password

def get_linux_os_info(device):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(hostname=device.ip_address, username=device.username, password=device.password)
        command = "echo $(awk -F= '/^PRETTY_NAME/{print $2}' /etc/os-release | tr -d '\"') $(uname -r)"
        stdin, stdout, stderr = ssh_client.exec_command(command)
        os_info = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        if error:
            return "Can't get information as command execution failed. Check the command and try again."
        return os_info

    except AuthenticationException:
        return "Can't get information as device can't be logged into. Check login details."
    except SSHException as e:
        return f"Connection failed due to an SSH error. Check device availability and network. Error: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
    finally:
        ssh_client.close()

# This block allows the script to run some tests if executed directly
if __name__ == '__main__':
    test_device = Device(ip_address='192.168.0.176', username='astonmgmt', password='astonmgmt')
    print(get_linux_os_info(test_device))
