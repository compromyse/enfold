from flask import request, flash, send_from_directory
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, logout_user, current_user
from tinydb import TinyDB
from .models import User

import json
import time
import os

from .modules.interface import Interface
from .job_manager import JobManager

states = Interface().get_states()
act_list = json.loads(open('app/acts.json').read())

job_manager = JobManager()
main = Blueprint('main', __name__)

@main.route('/')
@login_required
def home():
    jobs = job_manager.get_jobs()
    completed_jobs = TinyDB('jobs.json').all()
    return render_template('home.html', user=current_user, states=states, acts=act_list, completed_jobs=completed_jobs, jobs=jobs)

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
    admin = request.form.get('admin')

    if current_user.admin != True:
        flash('Only admin can create new users.', 'error')
        return redirect(url_for('main.home'))

    if not username or not password:
        flash('Username and password required.', 'error')
        return redirect(url_for('main.home'))

    user = User.create(username, password, admin == 'on')
    if user:
        flash(f'User {username} created successfully.', 'success')
    else:
        flash(f'User {username} already exists.', 'error')

    return redirect(url_for('main.home'))

@main.route('/enqueue_job', methods=['POST'])
@login_required
def enqueue_job():
    acts = request.form.getlist('act')
    sections = request.form.get('section', '').split(',')
    state_code = request.form.get('state_code')
    name = request.form.get('name')

    if not sections:
        sections = ''

    job_manager.enqueue_scrape(f'{name} - {time.time_ns()}', acts, sections, state_code)

    flash('Job created.', 'info')
    return redirect(url_for('main.home'))

@main.route('/download/<filename>')
@login_required
def download_output(filename):
    output_dir = os.path.join(os.getcwd(), 'app/outputs')
    return send_from_directory(output_dir, f'{filename}.csv', as_attachment=True)
