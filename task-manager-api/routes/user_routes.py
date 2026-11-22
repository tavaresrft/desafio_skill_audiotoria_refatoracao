"""User registration, authentication, and account routes."""

import re

from flask import Blueprint, current_app, g, jsonify, request

from security import can_access_user, issue_token, roles_required, token_required
from services import user_service

user_bp = Blueprint("users", __name__)
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")
MIN_PASSWORD_LENGTH = 8


@user_bp.get("/users")
@token_required
@roles_required("admin", "manager")
def get_users():
    rows = user_service.list_users_with_task_counts()
    return jsonify([
        {
            **user.to_dict(),
            "task_count": task_count,
        }
        for user, task_count in rows
    ]), 200


@user_bp.get("/users/<int:user_id>")
@token_required
def get_user(user_id):
    if not can_access_user(user_id):
        return jsonify({"error": "Acesso negado"}), 403
    user = user_service.get_user(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    data = user.to_dict()
    data["tasks"] = [task.to_dict() for task in user_service.get_user_tasks(user_id)]
    return jsonify(data), 200


@user_bp.post("/users")
def create_user():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Dados inválidos"}), 400
    if "role" in data:
        return jsonify({"error": "Cadastro público não permite definir role"}), 403

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 100:
        return jsonify({"error": "Nome é obrigatório"}), 400
    if not isinstance(email, str) or len(email) > 150 or not EMAIL_PATTERN.fullmatch(email):
        return jsonify({"error": "Email inválido"}), 400
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        return jsonify({"error": f"Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres"}), 400
    if user_service.find_by_email(email):
        return jsonify({"error": "Email já cadastrado"}), 409

    user = user_service.build_public_user(name.strip(), email, password)
    try:
        user_service.create_user(user)
    except Exception:
        user_service.rollback()
        current = user_service.find_by_email(email)
        if current:
            return jsonify({"error": "Email já cadastrado"}), 409
        current_app.logger.exception("User registration failed")
        return jsonify({"error": "Erro ao criar usuário"}), 500
    return jsonify(user.to_dict()), 201


@user_bp.put("/users/<int:user_id>")
@token_required
def update_user(user_id):
    if not can_access_user(user_id):
        return jsonify({"error": "Acesso negado"}), 403
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Dados inválidos"}), 400
    user = user_service.get_user(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    is_admin = g.current_user.role == "admin"
    if g.current_user.id != user_id and not is_admin:
        return jsonify({"error": "Acesso negado"}), 403
    if not is_admin and ({"role", "active"} & data.keys()):
        return jsonify({"error": "Apenas administradores podem alterar role ou active"}), 403
    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip() or len(data["name"].strip()) > 100:
            return jsonify({"error": "Nome inválido"}), 400
        user.name = data["name"].strip()
    if "email" in data:
        email = data["email"]
        if not isinstance(email, str) or len(email) > 150 or not EMAIL_PATTERN.fullmatch(email):
            return jsonify({"error": "Email inválido"}), 400
        existing = user_service.find_by_email(email)
        if existing and existing.id != user.id:
            return jsonify({"error": "Email já cadastrado"}), 409
        user.email = email
    if "password" in data:
        password = data["password"]
        if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
            return jsonify({"error": f"Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres"}), 400
        user.set_password(password)
    if "role" in data:
        if not is_admin:
            return jsonify({"error": "Acesso negado"}), 403
        if not isinstance(data["role"], str) or data["role"] not in {"user", "admin", "manager"}:
            return jsonify({"error": "Role inválido"}), 400
        user.role = data["role"]
    if "active" in data:
        if not is_admin or not isinstance(data["active"], bool):
            return jsonify({"error": "Apenas administradores podem alterar active"}), 403
        user.active = data["active"]

    try:
        user_service.save_user(user)
    except Exception:
        user_service.rollback()
        current_app.logger.exception("User update failed")
        return jsonify({"error": "Erro ao atualizar"}), 500
    return jsonify(user.to_dict()), 200


@user_bp.delete("/users/<int:user_id>")
@token_required
@roles_required("admin")
def delete_user(user_id):
    user = user_service.get_user(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    try:
        user_service.delete_user(user)
    except Exception:
        user_service.rollback()
        current_app.logger.exception("User deletion failed")
        return jsonify({"error": "Erro ao deletar"}), 500
    return jsonify({"message": "Usuário deletado com sucesso"}), 200


@user_bp.get("/users/<int:user_id>/tasks")
@token_required
def get_user_tasks(user_id):
    if not can_access_user(user_id):
        return jsonify({"error": "Acesso negado"}), 403
    user = user_service.get_user(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    result = []
    for task in user_service.get_user_tasks(user_id):
        item = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "created_at": str(task.created_at),
            "due_date": str(task.due_date) if task.due_date else None,
            "overdue": task.is_overdue(),
        }
        result.append(item)
    return jsonify(result), 200


@user_bp.post("/login")
def login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Dados inválidos"}), 400
    email, password = data.get("email"), data.get("password")
    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({"error": "Email e senha são obrigatórios"}), 400
    try:
        user, error = user_service.authenticate(email, password)
    except Exception:
        user_service.rollback()
        current_app.logger.exception("User authentication failed")
        return jsonify({"error": "Erro interno"}), 500
    if error == "invalid":
        return jsonify({"error": "Credenciais inválidas"}), 401
    if error == "inactive":
        return jsonify({"error": "Usuário inativo"}), 403
    return jsonify({
        "message": "Login realizado com sucesso",
        "user": user.to_dict(),
        "token": issue_token(user),
    }), 200
