"""Central HTTP error mapping without exposing internal exception details."""

from flask import jsonify
from werkzeug.exceptions import HTTPException


def internal_error_response(error):
    from flask import current_app

    current_app.logger.exception("Request failed", exc_info=error)
    return jsonify({"erro": "Erro interno do servidor"}), 500


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({"erro": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        return internal_error_response(error)
