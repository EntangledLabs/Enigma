from flask import (
    Blueprint,
    flash,
    render_template,
    g,
    redirect,
    request,
    session,
    url_for
)

from parable.auth import login_required

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/dashboard', methods='GET')
@login_required
def dashboard():
    return render_template('user/dashboard.html')

@bp.route('/summary', methods='GET')
@login_required
def summary():
    pass