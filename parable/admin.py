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

from parable.auth import admin_required

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/box', methods=('GET', 'POST'))
@admin_required
def box():
    pass

@bp.route('/credlist', methods=('GET', 'POST'))
@admin_required
def credlist():
    pass
