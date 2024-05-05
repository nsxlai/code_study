from flask import Blueprint, render_template, redirect, url_for, session, request, flash, abort

from .model import Model
from .cryp import Cryp

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return redirect(url_for('main.login'))
    # return render_template('login.html')


@main.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if 'user' in session:
        error = 'Please logout from previous session'
    else:
        # user & password entered
    return render_template('login.html', error=error)


@main.route('/new', methods=['POST', 'GET'])
def new():
    # abort_func(request.method, 400)
    if request.method == 'POST':
    # if 'user in request.form and 'psw' in request.form:
        user = request.form['user']
        password = request.form['psw']
        email = request.form['email']
        fullname = request.form['fullname']
        add_success = Model.add_user(*(email, user, password, fullname))

        user_valid = Model.user_exists(user, password)
        if user_valid == 0:
            session['user'] = user
            return redirect(url_for('main.profile', user=user))
        elif user_valid == 1:
            error = 'Incorrect password for ' + user
        else:
            error = 'Incorrect user and password'
    if request.method == 'GET':
        pass
