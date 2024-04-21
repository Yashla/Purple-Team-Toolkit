from flask import render_template, request, redirect, url_for, send_from_directory, current_app, Response, flash
from . import snmp
from .snmpwalker import snmp_walk, snmp_set
import os
from models import SNMP_Output
from extensions import db

@snmp.route('/operations')
def snmp_operations():
    snmp_outputs = SNMP_Output.query.all()
    return render_template('snmp_operations.html', snmp_outputs=snmp_outputs)

@snmp.route('/set', methods=['POST'])
def set_oid():
    if request.method == 'POST':
        # Collect form data
        ip_address = request.form['ip_address']
        community_string = request.form['community_string']
        oid = request.form['oid']
        value = request.form['value']
        value_type = request.form['value_type']

        # Execute SNMP set operation
        result_message = snmp_set(ip_address, community_string, oid, value_type, value)
        
        # Return directly with the result message, avoiding redirect
        snmp_outputs = SNMP_Output.query.all()  # If you need to display other data as well
        return render_template('snmp_operations.html', result_message=result_message, snmp_outputs=snmp_outputs)

    return render_template('snmp_operations.html')

@snmp.route('/walk', methods=['GET', 'POST'])
def walk_oid():
    if request.method == 'POST':
        ip_address = request.form['ip_address']
        community_string = request.form['community_string']
        oids = request.form['oid'].split(',')

        walk_result = snmp_walk(ip_address, community_string, oids)
        file_path = walk_result['file_path']
        success = walk_result['success']

        if success and file_path:
            try:
                with open(file_path, 'rb') as file:
                    file_data = file.read()
                    new_snmp_output = SNMP_Output(filename=os.path.basename(file_path), data=file_data)
                    db.session.add(new_snmp_output)
                    db.session.commit()
                flash("File saved to database and removed from the directory.", 'success')
            except Exception as e:
                flash(f"An error occurred: {str(e)}", 'error')
            finally:
                os.remove(file_path)  # This ensures the file is removed whether db commit succeeds or fails
        else:
            flash("SNMP Walk failed or did not generate a file.", 'error')
        
        return redirect(url_for('snmp.snmp_operations'))

    return render_template('snmp_operations.html')

@snmp.route('/download_snmp_output/<int:snmp_output_id>')
def download_snmp_output(snmp_output_id):
    snmp_output = SNMP_Output.query.get_or_404(snmp_output_id)
    response = Response(snmp_output.data, mimetype="text/plain", headers={"Content-Disposition": f"attachment;filename={snmp_output.filename}"})
    return response

@snmp.route('/delete_snmp_output/<int:snmp_output_id>', methods=['POST'])
def delete_snmp_output(snmp_output_id):
    snmp_output = SNMP_Output.query.get_or_404(snmp_output_id)
    db.session.delete(snmp_output)
    db.session.commit()
    flash('File deleted successfully.', 'success')
    return redirect(url_for('snmp.snmp_operations'))
