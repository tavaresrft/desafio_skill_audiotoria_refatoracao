"""Environment-backed application settings."""

import os
import secrets

from dotenv import load_dotenv


def _database_uri():
    configured_uri = os.getenv("DATABASE_URL")
    if configured_uri:
        return configured_uri
    path = os.getenv("DATABASE_PATH", "tasks.db")
    if path == ":memory:":
        return "sqlite:///:memory:"
    if path.startswith("sqlite:///"):
        return path
    return f"sqlite:///{os.path.abspath(path)}"


def build_config():
    """Return Flask settings, validating production secrets at startup."""
    load_dotenv()
    secret_key = os.getenv("APP_SECRET_KEY")
    if not secret_key and os.getenv("APP_ENV", "development").lower() == "production":
        raise RuntimeError("APP_SECRET_KEY é obrigatória em produção")
    token_ttl_seconds = int(os.getenv("TOKEN_TTL_SECONDS", "3600"))
    if token_ttl_seconds <= 0:
        raise RuntimeError("TOKEN_TTL_SECONDS deve ser maior que zero")

    return {
        "SECRET_KEY": secret_key or secrets.token_urlsafe(48),
        "SQLALCHEMY_DATABASE_URI": _database_uri(),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "TOKEN_TTL_SECONDS": token_ttl_seconds,
        "DEBUG": False,
    }
