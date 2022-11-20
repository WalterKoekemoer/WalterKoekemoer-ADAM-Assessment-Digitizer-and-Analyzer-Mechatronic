import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .components.mail_server import mail, Message

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

import numpy as np
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/validate', methods=('GET', 'POST'))
def validate():
    if request.method == 'POST':
        password = request.form['code']
        error = None
        
        if not password:
            error = "code not entered"
            flash(error)
            return redirect('auth/validate.html')

        db = get_db()
        validate = db.execute(
            'SELECT * FROM validator WHERE username = ? ORDER BY created DESC', (session['user_id'],)
        ).fetchone()

        if np.datetime64(validate.created,"s") - np.datetime64(datetime.now(),"s") < 300:
            
            if validate.password != password:
                error = "sorry, that is wrong..."
                flash(error)
                return render_template('auth/register.html')

            if not error:
                id = session['user_id']
                password = session.get('password')
                
                try:
                    db.execute(
                        "INSERT INTO lecturer (id, username, password) VALUES (?, ?)",
                        (id, generate_password_hash(password)),
                    )
                    db.commit()
                except db.IntegrityError:
                    error = f"User {id} is already registered."
                else:
                    return redirect(url_for("auth.login"))
        else:
            error = "Password expired"
            
        flash(error)

    return render_template('auth/register.html')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        id = request.form['user_id']
        password = request.form['password']
        type = request.form['type']
        FOS = request.form['field']
        T = request.form['year']
        M = None
        if 'masters' in request.form:
            M = request.form['masters']

        error = None
        if not username and type != "Student":
            error = "username is required"
        elif not id:
            error = 'NWU ID is required'
        elif id.__len__() != 8:
            error = 'NWU ID is wrong'
        elif not id.isnumeric():
            error = 'NWU ID is wrong'
        elif not password:
            error = 'Password is required'

        if error:
            flash(error)
            return redirect(request.referrer)

        if not error and type != "Student":          
            db = get_db()
            try:
                if type == "Assessor":
                    if M:
                        db.execute(
                            "INSERT INTO assessor (id, username, password, FOS, T, M) VALUES (?, ?, ?, ?, ?, ?)",
                            (int(id), username, generate_password_hash(password), FOS, '~', 1),
                        )
                    elif not M:
                        db.execute(
                            "INSERT INTO assessor (id, username, password, FOS, T, M) VALUES (?, ?, ?, ?, ?, ?)",
                            (int(id), username, generate_password_hash(password), FOS, T, 0),
                        )
                elif type == "Lecturer":
                    db.execute(
                        "INSERT INTO lecturer (id, username, password) VALUES (?, ?, ?)",
                        (int(id), username, generate_password_hash(password)),
                    )
                
                db.commit()
            except db.IntegrityError:
                error = f"User {id} is already registered."
            else:
                return redirect(url_for("auth.login"))
        
        elif not error and type == "Student":
            session['username'] = username
            session['user_id'] = int(id)
            session['password'] = password
            session['type'] = type
            session['field'] = FOS
            session['year'] = T
            if 'masters' in request.form:
                session['masters'] = M

            db = get_db()
            password = str(np.random.rand())[2:]
            db.execute(
                "INSERT INTO validator (id, password) VALUES (?, ?)",
                (session['user_id'],password),
            )
            db.commit()

            msg = Message(
                    'ADAM',
                    sender = str(session['user_id']) + '@student.g.nwu.ac.za',
                )
            msg.body = 'Your verification code is ' + password
            mail.send(msg)

            return render_template('auth/validate.html')

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        id = request.form['user_id']
        password = request.form['password']
        type = request.form['type']
        db = get_db()
        error = None

        if id.__len__() != 8:
            error = 'NWU ID is wrong'
        elif not id.isnumeric():
            error = 'NWU ID is wrong'

        if error:
            flash(error)
            return redirect(request.referrer)

        if type == "Assessor":
            user = db.execute(
                'SELECT * FROM assessor WHERE id = ?', (int(id),)
            ).fetchone()
        elif type == "Lecturer":
            user = db.execute(
                'SELECT * FROM lecturer WHERE id = ?', (int(id),)
            ).fetchone()
        elif type == "Student":
            user = db.execute(
                'SELECT * FROM student WHERE id = ?', (int(id),)
            ).fetchone()

        if not user:
            error = 'Incorrect id'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'

        if not error:
            session.clear()
            session['user_id'] = user['id']
            session['user_type'] = type
            if type == "Assessor":
                return redirect(url_for('assessor.scheadule'))
            elif type == "Lecturer":
                return redirect(url_for('lecturer.assessors'))
            elif type == "Student":
                return redirect(url_for('student.student_results'))

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