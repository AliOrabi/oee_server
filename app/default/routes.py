from datetime import datetime

from flask import render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_required

from app.default import bp
from app.default.db_helpers import create_scheduled_activities
from config import Config


@bp.route('/')
def default():
    return redirect(url_for('login.login'))


@bp.route('/index')
@login_required
def index():
    """ The default page """
    if current_user.is_authenticated:
        user = {'username': current_user.username, 'id': current_user.id}
    else:
        user = {'username': "nobody"}
    return render_template('default/index.html', title='Index', user=user)


@bp.route('/run_schedule', methods=['POST'])
def create_scheduled_activities():

    if "date" in request.args:
        dt = datetime.strptime(request.args['date'], '%d-%m-%y')
    else:
        dt = datetime.now()

    create_scheduled_activities(date=dt)
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}
