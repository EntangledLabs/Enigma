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
