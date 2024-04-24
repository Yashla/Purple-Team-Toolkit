from flask import render_template
from . import upnp_bp
from blueprints.upnp.upnp import upnp_main
from flask_login import login_required

@upnp_bp.route('/discover')
@login_required
def discover():
    """
    Route to perform UPnP discovery and display the results in JSON format.
    """
    upnp_dict = upnp_main()
    devices_info = upnp_dict["devices_info"]
    return render_template('upnp_results.html', devices=devices_info)  # Pass JSON string to the template
