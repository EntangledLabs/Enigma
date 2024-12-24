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

from parable.admin import bp

@bp.route('/team', methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        pass

    return render_template('admin/team.html')

@bp.route('/team/create', methods='POST')
def user_add():
    username = request.form['username']
    identifier = ParableUser.last_identifier()
    permission = ParableUser.Permission[request.form['permission']].value
    password = request.form['password']
    error = None

    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is required.'

    if error is None:
        user = ParableUser(
            username=username,
            identifier=identifier,
            permission_level=permission
        )
        user.set_pw(password)
        user.add_to_db()

    flash(error)
    return render_template('admin/team.html')


@bp.route('/team/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def user_modify(id):
    if request.method == 'GET':
        pass