"""Signed bearer-token helpers and route authorization decorators."""

from functools import wraps
import hmac

from flask import current_app, g, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from database import db
from models.user import User


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="task-manager-auth-v1")


def issue_token(user):
    return _serializer().dumps({"sub": user.id})


def token_required(handler):
    @wraps(handler)
    def wrapped(*args, **kwargs):
        authorization = request.headers.get("Authorization", "")
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            response = jsonify({"error": "Autenticação necessária"})
            response.status_code = 401
            response.headers["WWW-Authenticate"] = "Bearer"
            return response

        try:
            payload = _serializer().loads(
                token,
                max_age=current_app.config["TOKEN_TTL_SECONDS"],
            )
            user_id = payload.get("sub")
        except SignatureExpired:
            return jsonify({"error": "Token expirado"}), 401
        except (BadSignature, AttributeError, TypeError):
            return jsonify({"error": "Token inválido"}), 401

        user = db.session.get(User, user_id) if isinstance(user_id, int) else None
        if not user or not user.active:
            return jsonify({"error": "Token inválido"}), 401

        g.current_user = user
        return handler(*args, **kwargs)

    return wrapped


def roles_required(*allowed_roles):
    def decorator(handler):
        @wraps(handler)
        def wrapped(*args, **kwargs):
            if g.current_user.role not in allowed_roles:
                return jsonify({"error": "Acesso negado"}), 403
            return handler(*args, **kwargs)

        return wrapped

    return decorator


def can_access_user(user_id):
    return g.current_user.id == user_id or g.current_user.role in {"admin", "manager"}


def is_legacy_md5(stored_hash):
    return isinstance(stored_hash, str) and len(stored_hash) == 32 and all(
        char in "0123456789abcdef" for char in stored_hash.lower()
    )


def verify_legacy_md5(stored_hash, password):
    import hashlib

    candidate = hashlib.md5(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(stored_hash.lower(), candidate)
