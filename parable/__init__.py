from logging.config import dictConfig

from flask import Flask, render_template

from os import getenv
from dotenv import load_dotenv

from enigma_models.models.user import ParableUser

from parable.logger import log_config, write_log_header

load_dotenv(override=True)

def create_app():
    #dictConfig(log_config)

    # Initialize logger
    write_log_header()

    # Create admin competitor with username 'admin' and password 'enigma'
    admin = ParableUser(
        username='admin',
        identifier=0,
        permission_level=0
    )
    admin.set_pw('enigma')
    print(admin.add_to_db())

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=getenv('PARABLE_SECRET_KEY'),
    )

    from parable.competitor import bp as user_bp
    app.register_blueprint(user_bp)

    from parable.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from parable.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app