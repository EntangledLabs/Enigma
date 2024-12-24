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

from parable.admin import bp

@bp.route('/box', methods=['GET', 'POST'])
def box():
    pass

@bp.route('/box', methods='DELETE')
def box_delete():
    pass