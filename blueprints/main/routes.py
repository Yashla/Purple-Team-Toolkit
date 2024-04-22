from . import main
from flask import render_template,redirect, url_for
from flask_login import current_user

@main.route('/')
def index():
    return render_template('index.html')
