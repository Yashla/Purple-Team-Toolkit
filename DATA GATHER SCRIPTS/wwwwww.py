import winrm

# Connection settings
windows_host = 'http://192.168.0.4:5985/wsman'
username = 'Yash'
password = '2002'

# Create a session object
session = winrm.Session(windows_host, auth=(username, password), transport='basic')

# PowerShell script to get the Product
ps_script_product = """
$product = "Windows_" + (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion').CurrentMajorVersionNumber + "_" + (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion').DisplayVersion
Write-Output $product
"""

# Execute the PowerShell command for Product
result_product = session.run_ps(ps_script_product)

# Check if the command executed successfully for Product
if result_product.status_code == 0:
    Product = result_product.std_out.decode().strip()  # Extracting the Product value
    print(f"{Product}")
else:
    print("Error fetching Product:")
    print(result_product.std_err.decode())

# PowerShell script to get the Version
ps_script_version = """
$version = (Get-WmiObject Win32_OperatingSystem).Version + "." + (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion").UBR
Write-Output $version
"""

# Execute the PowerShell command for Version
result_version = session.run_ps(ps_script_version)

# Check if the command executed successfully for Version
if result_version.status_code == 0:
    Version = result_version.std_out.decode().strip()  # Extracting the Version value
    print(f"{Version}")
else:
    print("Error fetching Version:")
    print(result_version.std_err.decode())
