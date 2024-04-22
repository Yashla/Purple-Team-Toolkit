
from . import ssdp
from flask import render_template, session, redirect, url_for, flash, Response
from models import SSDPOutput
import subprocess
from datetime import datetime
import os
import psutil
from extensions import db
import threading
from flask_login import current_user, login_required


process = None
output_file_path_global = None

# Import any other necessary modules

@ssdp.route('/ssdp_spoofer')
@login_required
def ssdp_spoofer():
    ssdp_outputs = SSDPOutput.query.all()
    return render_template('ssdp_spoofer.html', ssdp_outputs=ssdp_outputs, output=session.get('output'))

@ssdp.route('/start_ssdp', methods=['POST'])
def start_ssdp():
    global process, output_file_path_global
    # Check if the process is not already running
    if process is None or process.poll() is not None:
        # Set the environment variable for the subprocess to disable output buffering
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = "1"
        
        # Start the subprocess with the modified environment
        process = subprocess.Popen(
            ['python3', '/home/yash/Documents/GitHub/FYP-scan-devices-on-network/blueprints/ssdp/essdp/evil/evil_ssdp.py', 'ens37', '--template', 'scanner'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env  # Pass the modified environment
        )
        
        # Define the path to the output file
        now = datetime.now()
        file_name = f"ssdp_spoofer_results_{now.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        output_file_path_global = f"/home/yash/Documents/GitHub/FYP-scan-devices-on-network/blueprints/ssdp/essdp/evil/{file_name}"
        
        # Start a thread to collect output from the subprocess
        threading.Thread(target=collect_output, args=(output_file_path_global,)).start()
    
    # Redirect to the ssdp_spoofer page after starting the subprocess
    return redirect(url_for('ssdp.ssdp_spoofer'))


@ssdp.route('/stop_ssdp', methods=['POST'])
def stop_ssdp():
    global process, output_file_path_global
    if process and process.poll() is None:  # If process is running
        parent_pid = process.pid  # Get the PID of the ssdp spoofer process
        parent = psutil.Process(parent_pid)  # Get the process using psutil
        for child in parent.children(recursive=True):  # Iterate over child processes
            child.kill()  # Terminate the child process
        process.kill()  # Now kill the parent process
        process.wait()  # Wait for the killing to complete
        process = None

        try:
            with open(output_file_path_global, "a") as file:  # Open in append mode
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file.write(f"\n\nFile has been saved on {timestamp}")
        except IOError as e:
            print(f"Error appending to the SSDP output file: {e}")

        # Now, store the updated output file in the database
        try:
            with open(output_file_path_global, "rb") as file:  # Now open in binary read mode
                file_content = file.read()
                file_name = os.path.basename(output_file_path_global)
                new_output = SSDPOutput(file_name=file_name, output_blob=file_content)
                db.session.add(new_output)
                db.session.commit()
        except IOError as e:
            print(f"Error reading the SSDP output file: {e}")
            # Optionally, handle the error
            
        try:
            os.remove(output_file_path_global)
            print(f"File {output_file_path_global} deleted successfully.")
        except OSError as e:
            print(f"Error deleting the SSDP output file: {e}")

    return redirect(url_for('ssdp.ssdp_spoofer'))

def collect_output(output_file_path):
    global process
    if process is None:
        return  # Exit early if the process hasn't been started

    # Determine if the file already exists to avoid overwriting the initial timestamp
    file_exists = os.path.exists(output_file_path)

    with open(output_file_path, "a") as output_file:  # Open in append mode
        # If the file does not exist, it's the first write operation, so add the timestamp
        if not file_exists:
            start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            output_file.write(f"File created on {start_time}\n\n")

        while True:
            if process is None or process.poll() is not None:
                break  # Exit the loop if the process is terminated or completes
            line = process.stdout.readline()
            if not line:
                break  # If there's no more output, exit the loop
            output_file.write(line)
            output_file.flush()  # Flush after each write to ensure real-time update

    os.chmod(output_file_path, 0o644)  # Set file permissions to rw-rw-rw- after closing the file
    
    


@ssdp.route('/download_ssdp_output/<int:ssdp_output_id>')
def download_ssdp_output(ssdp_output_id):
    ssdp_output = SSDPOutput.query.get_or_404(ssdp_output_id)
    # Ensure the output is decoded to a string if it's stored as binary
    output_data = ssdp_output.output_blob.decode('utf-8') if isinstance(ssdp_output.output_blob, bytes) else ssdp_output.output_blob
    # Create a response with the file content, set the appropriate headers for download
    response = Response(output_data, mimetype="text/plain", headers={"Content-Disposition": f"attachment;filename={ssdp_output.file_name}"})
    return response

@ssdp.route('/delete_ssdp_output/<int:ssdp_output_id>', methods=['POST'])
def delete_ssdp_output(ssdp_output_id):
    ssdp_output = SSDPOutput.query.get_or_404(ssdp_output_id)
    db.session.delete(ssdp_output)
    db.session.commit()
    flash('File deleted successfully.', 'success')
    return redirect(url_for('ssdp.ssdp_spoofer'))