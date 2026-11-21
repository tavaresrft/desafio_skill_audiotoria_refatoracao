"""Password hashing helpers using the Python standard library."""

import hashlib
import hmac
import secrets


ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 600_000


def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", str(password).encode("utf-8"), salt.encode("ascii"), ITERATIONS
    ).hex()
    return f"{ALGORITHM}${ITERATIONS}${salt}${digest}"


def is_password_hash(value):
    return isinstance(value, str) and value.startswith(f"{ALGORITHM}$")


def verify_password(password, encoded):
    if not is_password_hash(encoded):
        return False
    try:
        algorithm, iterations, salt, expected = encoded.split("$", 3)
        if algorithm != ALGORITHM:
            return False
        actual = hashlib.pbkdf2_hmac(
            "sha256", str(password).encode("utf-8"), salt.encode("ascii"), int(iterations)
        ).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False
