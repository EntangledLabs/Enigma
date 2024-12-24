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
from parable.competitor import bp

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        pass

    return render_template('competitor/dashboard.html')