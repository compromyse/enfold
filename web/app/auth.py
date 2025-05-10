from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user
from .models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.validate_login(username, password)
        if user:
            login_user(user)
            return redirect(url_for('main.home'))
        
        error = "Invalid credentials"
        
    return render_template('login.html', error=error)
