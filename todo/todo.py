from flask import (
    Blueprint, flash, redirect, g, request, render_template, url_for, request
)
from werkzeug.exceptions import abort
from todo.auth import login_required
from todo.db import get_db

bp = Blueprint('todo', __name__)

@bp.route('/')
@login_required
def index():
    db, c = get_db()
    c.execute(
        'select  t.id, t.description, u.username, t.completed, t.created_at from todo t JOIN user u on t.created_by = u.id where created_by = %s order by created_at desc',
        (g.user['id'], ))
    todos = c.fetchall()
    return render_template('todo/index.html', todos = todos)

@bp.route('/create', methods = ['GET', 'POST'])
@login_required
def create():
    if(request.method == 'POST'):
        description = request.form['description']
        message = None
        if(description == None):
            message = 'Description required.'
        if(message is not None):
            flash(message)
        else:
            db, c = get_db()
            c.execute('insert into todo (description, completed, created_by) values (%s, %s, %s)', (description, False, g.user['id']))
            db.commit()
            return redirect(url_for('todo.index'))
    return render_template('todo/create.html')

def get_todo(id):
    db, c = get_db()
    c.execute('select t.id, t.description, t.created_by, t.created_at, u.username from todo t join user u on t.created_by = u.id where t.id = %s',(id, ))
    todo = c.fetchone()
    if (todo is None):
        abort(404, "Todo {0} does not exist".format(id)) 
    return todo

@bp.route('/<int:id>/update', methods = ['GET', 'POST'])
@login_required
def update(id):
    todo = get_todo(id)
    if(request.method == 'POST'):
        description = request.form['description']
        completed = True if request.form.get('completed') == 'on' else False
        message = None

        if(not description):
            message = 'Description required.'
        if(message is not None):
            flash(message)
        else:
            db, c = get_db()
            c.execute('UPDATE todo SET description = %s, completed = %s WHERE id = %s and created_by = %s', (description, completed, id, g.user['id']))
            db.commit()
            return redirect(url_for('todo.index'))
    return render_template('todo/update.html', todo = todo)

@bp.route('/<int:id>/delete', methods = ['POST'])
@login_required
def delete(id):
    db, c = get_db()
    c.execute('DELETE FROM todo WHERE id = %s and created_by = %s', (id, g.user['id']))
    db.commit()
    return redirect(url_for('todo.index'))