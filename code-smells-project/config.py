"""Application settings resolved from the environment."""

import os
import secrets
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def _as_bool(value):
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.environ.get("APP_SECRET_KEY") or secrets.token_hex(32)
    DATABASE = os.environ.get("DATABASE_PATH", str(BASE_DIR / "loja.db"))
    DEBUG = _as_bool(os.environ.get("FLASK_DEBUG", "false"))
    JSON_SORT_KEYS = False
