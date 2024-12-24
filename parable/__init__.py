from logging.config import dictConfig

from flask import Flask, render_template

from os import getenv
from dotenv import load_dotenv

from parable.logger import log_config

load_dotenv(override=True)

def create_app():
    #dictConfig(log_config)
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=getenv('PARABLE_SECRET_KEY'),
    )

    from parable.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from parable.user import bp as user_bp
    app.register_blueprint(user_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app