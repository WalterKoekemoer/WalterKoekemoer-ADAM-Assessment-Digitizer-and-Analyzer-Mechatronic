from flask import (
    Blueprint, render_template
)

from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    db.execute(
        "DELETE FROM validator WHERE timestamp < (NOW() - INTERVAL 5 MINUTE);"
    )
    db.commit()
    assessors = db.execute(
        'SELECT * from assessors'
    ).fetchall()
    return render_template('blog/index.html', assessors=assessors)
