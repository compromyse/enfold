from flask import request, flash
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, logout_user, current_user
from .models import User

from .modules.interface import Interface

states = Interface().get_states()

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def home():
    return render_template('home.html', user=current_user, states=states)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@main.route('/create_user', methods=['POST'])
@login_required
def create_user():
    username = request.form.get('username')
    password = request.form.get('password')

    if current_user.admin != True:
        flash('Only admin can create new users.', 'error')
        return redirect(url_for('main.home'))

    if not username or not password:
        flash('Username and password required.', 'error')
        return redirect(url_for('main.home'))

    user = User.create(username, password)
    if user:
        flash(f'User {username} created successfully.', 'success')
    else:
        flash(f'User {username} already exists.', 'error')

    return redirect(url_for('main.home'))

@main.route('/enqueue_job', methods=['POST'])
@login_required
def enqueue_job():
    act = request.form.get('act')
    section = request.form.get('section')
    state_code = request.form.get('state_code')

    if not act or not state_code:
        flash('All fields must be filled.', 'error')
        return redirect(url_for('main.home'))

    if not section:
        section = ''

    flash('Job created.', 'info')
    return redirect(url_for('main.home'))
