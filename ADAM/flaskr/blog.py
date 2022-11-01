from flask import (
    Blueprint, render_template
)

from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    check = db.execute(
        "DELETE FROM validator WHERE CURRENT_TIMESTAMP > time(created,'+5 minutes');"
    ).fetchone()
    print(check)
    db.commit()
    assessors = db.execute(
        'SELECT * from assessor',
    ).fetchall()
    return render_template('blog/index.html', assessors=assessors)
