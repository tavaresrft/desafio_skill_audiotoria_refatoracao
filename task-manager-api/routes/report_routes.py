"""HTTP handlers for reports and category use cases."""

import re

from flask import Blueprint, current_app, jsonify, request

from models.category import Category
from security import can_access_user, roles_required, token_required
from services import report_service

report_bp = Blueprint("reports", __name__)
COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")


def _valid_category_text(value, max_length):
    return value is None or (isinstance(value, str) and len(value) <= max_length)


@report_bp.get("/reports/summary")
@token_required
@roles_required("admin", "manager")
def summary_report():
    return jsonify(report_service.summary_report()), 200


@report_bp.get("/reports/user/<int:user_id>")
@token_required
def user_report(user_id):
    if not can_access_user(user_id):
        return jsonify({"error": "Acesso negado"}), 403
    report = report_service.user_report(user_id)
    if report is None:
        return jsonify({"error": "Usuário não encontrado"}), 404
    return jsonify(report), 200


@report_bp.get("/categories")
@token_required
def get_categories():
    return jsonify(report_service.list_categories_with_counts()), 200


@report_bp.post("/categories")
@token_required
@roles_required("admin", "manager")
def create_category():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Dados inválidos"}), 400
    name = data.get("name")
    description = data.get("description", "")
    color = data.get("color", "#000000")
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 100:
        return jsonify({"error": "Nome é obrigatório"}), 400
    if not _valid_category_text(description, 300):
        return jsonify({"error": "Descrição inválida"}), 400
    if not isinstance(color, str) or not COLOR_PATTERN.fullmatch(color):
        return jsonify({"error": "Cor inválida"}), 400
    category = Category(name=name.strip(), description=description, color=color)
    try:
        category = report_service.create_category(category)
    except Exception:
        report_service.rollback()
        current_app.logger.exception("Category creation failed")
        return jsonify({"error": "Erro ao criar categoria"}), 500
    return jsonify(category.to_dict()), 201


@report_bp.put("/categories/<int:cat_id>")
@token_required
@roles_required("admin", "manager")
def update_category(cat_id):
    category = report_service.get_category(cat_id)
    if not category:
        return jsonify({"error": "Categoria não encontrada"}), 404
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Dados inválidos"}), 400
    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip() or len(data["name"].strip()) > 100:
            return jsonify({"error": "Nome inválido"}), 400
        category.name = data["name"].strip()
    if "description" in data:
        if not _valid_category_text(data["description"], 300):
            return jsonify({"error": "Descrição inválida"}), 400
        category.description = data["description"]
    if "color" in data:
        color = data["color"]
        if not isinstance(color, str) or not COLOR_PATTERN.fullmatch(color):
            return jsonify({"error": "Cor inválida"}), 400
        category.color = color
    try:
        category = report_service.save_category(category)
    except Exception:
        report_service.rollback()
        current_app.logger.exception("Category update failed")
        return jsonify({"error": "Erro ao atualizar"}), 500
    return jsonify(category.to_dict()), 200


@report_bp.delete("/categories/<int:cat_id>")
@token_required
@roles_required("admin", "manager")
def delete_category(cat_id):
    category = report_service.get_category(cat_id)
    if not category:
        return jsonify({"error": "Categoria não encontrada"}), 404
    try:
        report_service.delete_category(category)
    except Exception:
        report_service.rollback()
        current_app.logger.exception("Category deletion failed")
        return jsonify({"error": "Erro ao deletar"}), 500
    return jsonify({"message": "Categoria deletada"}), 200
