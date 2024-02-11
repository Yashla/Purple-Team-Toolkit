import winrm

# Connection settings
windows_host = 'http://192.168.0.4:5985/wsman'  # Ensure 'http://' is used
username = 'Yash'
password = '2002'

# Create a session object
session = winrm.Session(windows_host, 
                        auth=(username, password), 
                        transport='basic')  # Use 'http' for transport

# PowerShell command to get OS version via WMI
ps_script = "Get-WmiObject -Class Win32_OperatingSystem | Select-Object Caption, Version"

# Execute the PowerShell command
result = session.run_ps(ps_script)

# Output the results
if result.status_code == 0:
    print("OS Information:")
    print(result.std_out.decode())
else:
    print("Error:")
    print(result.std_err.decode())
