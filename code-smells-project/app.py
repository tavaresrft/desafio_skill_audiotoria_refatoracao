"""Application factory and development-server entry point."""

from flask import Flask
from flask_cors import CORS

from config import Config
from database import close_db, init_db
from errors import register_error_handlers
from routes import api


def create_app(config_override=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_override:
        app.config.update(config_override)

    CORS(app)
    app.register_blueprint(api)
    app.teardown_appcontext(close_db)
    register_error_handlers(app)

    with app.app_context():
        init_db()
    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"],
    )
