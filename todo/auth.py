import functools
from flask import (
    Blueprint, flash, g, render_template, request, url_for, session, redirect
)
from werkzeug.security import check_password_hash, generate_password_hash
from todo.db import get_db

bp = Blueprint('auth', __name__, url_prefix = '/auth')

@bp.route('/register', methods = ['POST', 'GET'])
def register():
    if (request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']
        db, c = get_db()
        message = None
        c.execute('select id from user where username = %s', (username, ))
        if (not username or not password):
            message = 'Username and password required!'
        elif (c.fetchone() is not None):
            message = 'The user {} is already registered!'.format(username)

        if (message is None):
            c.execute('insert into user (username, password) values (%s, %s)',
            (username, generate_password_hash(password))
            )
            db.commit()

            return redirect(url_for('auth.login'))

        flash(message)

    return render_template('auth/register.html')

@bp.route('/login', methods = ['POST', 'GET'])
def login ():
    if(request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']
        db, c = get_db()
        message = None
        c.execute('select * from user where username = %s', (username, ))
        user = c.fetchone()
        if(user is None):
            message = 'Wrong username and/or passwords'
        elif(not check_password_hash(user['password'], password)):
            message = 'Wrong username and/or passwords'
        
        if (message is None):
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('todo.index'))

        flash(message)

    return render_template('auth/login.html')

# Decorator function
@bp.before_app_request
def load_looged_in_user():
    user_id = session.get('user_id')
    if(user_id is None):
        g.user = None
    else:
        db,c = get_db()
        c.execute('select * from user where id = %s', (user_id, ))
        g.user = c.fetchone()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if (g.user is None):
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))