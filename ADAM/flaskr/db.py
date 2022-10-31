import sqlite3

import click
from flask import current_app, g

#In web applications this connection is typically tied to the request. 
# It is created at some point when handling a request, and closed before the response is sent.

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

# Add the Python functions that will run these SQL commands to the db.py file 
# flask --app flaskr init-db

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


# register the app 
# flask --app flaskr --debug run

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)