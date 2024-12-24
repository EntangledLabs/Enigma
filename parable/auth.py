import functools

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

from enigma_models.models.user import ParableUser

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = ParableUser.find(username=username)
        error = None

        if user is None:
            error = 'Invalid username'
        elif not user.check_pw(password):
            error = 'Incorrect password'

        if error is None:
            session.clear()
            session['user_id'] = user.identifier
            return redirect(url_for('user.dashboard'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@bp.route('/unauthorized')
def unauthorized():
    return redirect(url_for('auth.unauthorized'))

@bp.before_app_request
def load_current_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = ParableUser.find(identifier=user_id)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)
    return wrapped_view

@login_required
def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user.permission_level == 0:
            return redirect(url_for('auth.unauthorized'))

        return view(**kwargs)
    return wrapped_view

@login_required
def gt_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user.permission_level <= 1:
            return redirect(url_for('auth.unauthorized'))

        return view(**kwargs)
    return wrapped_view