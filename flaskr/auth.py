import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .mail_server import mail_server, Message

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

import numpy as np
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/validate', methods=('GET', 'POST'))
def validate():
    if request.method == 'POST':
        password = request.form['code']
        id = int(request.form['id'])
        error = None
        
        if not password:
            error = "code not entered"
            flash(error)
            return redirect('auth/validate.html', user_id = str(id))

        db = get_db()
        validate = db.execute(
            'SELECT * FROM validator WHERE username = ? ORDER BY created DESC', (id,)
        ).fetchone()

        if np.datetime64(validate.created,"s") - np.datetime64(datetime.now(),"s") < 300:
            
            if validate.password != password or session['id'] != id:
                error = "sorry, that is wrong..."
                flash(error)
                return render_template('auth/register.html')

            if not error:
                username = session.get('username')
                id = session['id']
                password = session.get('password')
                type = session.get('type')
                FOS = session.get('FOS')
                T = session.get('T')
                M = session.get('M')
                
                try:
                    if type == "Assessor":
                        if M:
                            db.execute(
                                "INSERT INTO assessor (id, username, password, FOS, T, M) VALUES (?, ?, ?, ?, ?, ?)",
                                (id, username, generate_password_hash(password), FOS, '~', M),
                            )
                        else:
                            db.execute(
                                "INSERT INTO assessor (id, username, password, FOS, T, M) VALUES (?, ?, ?, ?, ?, ?)",
                                (id, username, generate_password_hash(password), FOS, T, M),
                            )
                    elif type == "Lecturer":
                        db.execute(
                            "INSERT INTO lecturer (id, username, password) VALUES (?, ?, ?)",
                            (id, username, generate_password_hash(password)),
                        )
                    elif type == "Student":
                        db.execute(
                            "INSERT INTO lecturer (id, username, password) VALUES (?, ?)",
                            (id, generate_password_hash(password)),
                        )
                    db.commit()
                except db.IntegrityError:
                    error = f"User {id} is already registered."
                else:
                    return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['id'] = int(request.form['id'])
        session['password'] = request.form['password']
        session['type'] = request.form['type']
        session['field'] = request.form['field']
        session['year'] = request.form['year']
        session['masters'] = request.form['masters']
        error = None

        if not session['username']:
            error = "username is required"
        elif not session['id']:
            error = 'NWU ID is required'
        elif str(session['id']).__len__() != 8:
            error = 'NWU ID is wrong'
        elif str(session['id']).isnumeric():
            error = 'NWU ID is wrong'
        elif not session['password']:
            error = 'Password is required'
        

        if error:
            flash(error)
            return render_template('auth/register.html')

        db = get_db()
        password = str(np.random.rand())[:2]
        db.execute(
            "INSERT INTO validator (id, password) VALUES (?, ?)",
            (session['id'],password),
        )
        db.commit()
        
        msg = Message(
                'ADAM',
                sender =session['id'] + '@student.g.nwu.ac.za',
               )
        msg.body = 'Your verification code is ' + password
        mail_server.send(msg)
        return render_template('auth/validate.html', user_id = str(session['id']))


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        id = int(request.form['id'])
        password = request.form['password']
        type = request.form['type']
        db = get_db()
        error = None

        if type == "Assessor":
            user = db.execute(
                'SELECT * FROM assessor WHERE username = ?', (id,)
            ).fetchone()
        elif type == "Lecturer":
            user = db.execute(
                'SELECT * FROM lecturer WHERE username = ?', (id,)
            ).fetchone()
        elif type == "Student":
            user = db.execute(
                'SELECT * FROM student WHERE username = ?', (id,)
            ).fetchone()

        if user is None:
            error = 'Incorrect id'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['user_type'] = type
            if type == "Assessor":
                return redirect(url_for('scheadule'))
            elif type == "Lecturer":
                return redirect(url_for('assessors'))
            elif type == "Student":
                return redirect(url_for('student_results', id = session['user_id']))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    user_type = session.get('user_type')

    if user_id is None:
        g.user = None
    else:
        if user_type == "Assessor":
            g.user = get_db().execute(
                'SELECT * FROM assessor WHERE id = ?', (user_id,)
            ).fetchone()
        elif user_type == "Lecturer":
            g.user = get_db().execute(
                'SELECT * FROM lecturer WHERE id = ?', (user_id,)
            ).fetchone()
        elif user_type == "Student":
            g.user = get_db().execute(
                'SELECT * FROM student WHERE id = ?', (user_id,)
            ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def create_app():
    app = ...
    # existing code omitted

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app