from flask import Blueprint, request, render_template, redirect, url_for, make_response, flash
from models.user import User
from utils.auth import generate_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'customer')
        if not username or not password or not email:
            flash("Please provide username, email, and password", "danger")
            return render_template('register.html')
        if User.find_by_username(username):
            flash("Username already exists", "danger")
            return render_template('register.html')
        # Check email uniqueness
        from utils.db import get_collection
        users = get_collection('users')
        if users.find_one({'email': email}):
            flash("Email already registered", "danger")
            return render_template('register.html')
        User.create(username, password, email, role)
        flash("Registration successful. Please login.", "success")
        return redirect(url_for('auth.login'))
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.find_by_username(username)
        if not user or not user.check_password(password):
            flash("Invalid username or password", "danger")
            return render_template('login.html')
        payload = {'username': user.username, 'role': user.role}
        token = generate_token(payload)
        resp = make_response(redirect(url_for('bank.dashboard')))
        resp.set_cookie('access_token', token, httponly=True, samesite='Strict')
        return resp
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    resp = make_response(redirect(url_for('auth.login')))
    resp.delete_cookie('access_token')
    flash("You have been logged out.", "success")
    return resp
