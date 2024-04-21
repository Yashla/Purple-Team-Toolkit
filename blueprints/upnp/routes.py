# routes.py
from flask import render_template
from . import upnp_bp
#from .upnptest_utils import discover_pnp_locations_json, parse_locations_json  # Make sure to output JSON from these functions
from blueprints.upnp.upnp import upnp_main
import json

@upnp_bp.route('/discover')
def discover():
    """
    Route to perform UPnP discovery and display the results in JSON format.
    """
    upnp_dict = upnp_main()
    devices_info = upnp_dict["devices_info"]
    return render_template('upnp_results.html', devices=devices_info)  # Pass JSON string to the template
