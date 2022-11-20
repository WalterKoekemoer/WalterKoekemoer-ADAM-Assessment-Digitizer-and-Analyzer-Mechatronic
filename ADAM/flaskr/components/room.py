from flask import (
    Blueprint, render_template
)

# from flaskr.db import get_db

bp = Blueprint('room', __name__)


@bp.route('/room', methods=('GET', 'POST'))
def index():
    # if request.method == 'POST':
    #     db = get_db()
    return render_template('room')