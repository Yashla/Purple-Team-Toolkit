from . import main
from flask import render_template, redirect, url_for
from flask_login import current_user, login_required

@main.route('/')
@login_required
def index():
    return render_template('index.html')  # Render the main dashboard or home page after login


 #   if not current_user.is_authenticated:
  #      return redirect(url_for('auth.login'))