"""Application factory and composition root for the Task Manager API."""

import os
import os
from datetime import datetime

from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError

from config import build_config
from database import db


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(build_config())
    if test_config:
        app.config.update(test_config)

    CORS(app)
    db.init_app(app)

    # Import models before create_all so SQLAlchemy has all tables registered.
    from models import category, task, user  # noqa: F401
    from routes.report_routes import report_bp
    from routes.task_routes import task_bp
    from routes.user_routes import user_bp

    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})

    @app.get("/")
    def index():
        return jsonify({"message": "Task Manager API", "version": "1.0"})

    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        app.logger.exception("Database operation failed", exc_info=error)
        db.session.rollback()
        return jsonify({"error": "Erro interno"}), 500

    @app.errorhandler(404)
    def handle_not_found(_error):
        return jsonify({"error": "Recurso não encontrado"}), 404

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=False,
    )
