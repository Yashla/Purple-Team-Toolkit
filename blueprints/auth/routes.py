from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db
from models import User
from . import auth
from flask import session

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # Assuming 'main.index' is a valid endpoint post-login

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            next_page = request.args.get('next') or url_for('main.index')  # Fallback to 'main.index'
            return redirect(next_page)
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # Make sure this points to a valid view function

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Username already exists. Choose a different one.')
            return redirect(url_for('auth.register'))

        # Use the default method for password hashing
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')
