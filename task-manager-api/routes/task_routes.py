"""HTTP handlers for task use cases."""

from datetime import datetime

from flask import Blueprint, current_app, g, jsonify, request

from security import token_required
from services import task_service

task_bp = Blueprint("tasks", __name__)
VALID_STATUSES = {"pending", "in_progress", "done", "cancelled"}
ELEVATED_ROLES = {"admin", "manager"}


def _can_manage(task):
    return g.current_user.role in ELEVATED_ROLES or task.user_id == g.current_user.id


def _serialize_list_item(task):
    result = task.to_dict()
    result.update({
        "overdue": task.is_overdue(),
        "user_name": task.user.name if task.user else None,
        "category_name": task.category.name if task.category else None,
    })
    return result


def _validate_task_data(data, partial=False):
    if not isinstance(data, dict):
        return None, {"error": "Dados inválidos"}
    validated = {}
    if not partial or "title" in data:
        title = data.get("title")
        if not isinstance(title, str) or len(title.strip()) < 3:
            return None, {"error": "Título muito curto" if title else "Título é obrigatório"}
        if len(title.strip()) > 200:
            return None, {"error": "Título muito longo"}
        validated["title"] = title.strip()
    if "description" in data:
        if data["description"] is not None and not isinstance(data["description"], str):
            return None, {"error": "Descrição inválida"}
        validated["description"] = data["description"]
    if not partial or "status" in data:
        status = data.get("status", "pending")
        if not isinstance(status, str) or status not in VALID_STATUSES:
            return None, {"error": "Status inválido"}
        validated["status"] = status
    if not partial or "priority" in data:
        priority = data.get("priority", 3)
        if type(priority) is not int or not 1 <= priority <= 5:
            return None, {"error": "Prioridade deve ser entre 1 e 5"}
        validated["priority"] = priority
    if "due_date" in data:
        if data["due_date"] in (None, ""):
            validated["due_date"] = None
        else:
            try:
                validated["due_date"] = datetime.strptime(data["due_date"], "%Y-%m-%d")
            except (TypeError, ValueError):
                return None, {"error": "Formato de data inválido. Use YYYY-MM-DD"}
    if "tags" in data:
        tags = data["tags"]
        if isinstance(tags, list) and all(isinstance(tag, str) for tag in tags):
            validated["tags"] = ",".join(tags)
        elif isinstance(tags, str):
            validated["tags"] = tags
        else:
            return None, {"error": "Tags inválidas"}
    return validated, None


@task_bp.get("/tasks")
@token_required
def get_tasks():
    return jsonify([_serialize_list_item(task) for task in task_service.list_tasks(g.current_user)]), 200


@task_bp.get("/tasks/<int:task_id>")
@token_required
def get_task(task_id):
    task = task_service.get_task_for_actor(task_id, g.current_user)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404
    data = task.to_dict()
    data["overdue"] = task.is_overdue()
    return jsonify(data), 200


@task_bp.post("/tasks")
@token_required
def create_task():
    data = request.get_json(silent=True)
    values, error = _validate_task_data(data)
    if error:
        return jsonify(error), 400

    elevated = g.current_user.role in ELEVATED_ROLES
    user_id = data.get("user_id") if elevated else g.current_user.id
    category_id = data.get("category_id")
    if user_id is not None and (type(user_id) is not int or not task_service.get_user(user_id)):
        return jsonify({"error": "Usuário não encontrado"}), 404
    if category_id is not None and (type(category_id) is not int or not task_service.get_category(category_id)):
        return jsonify({"error": "Categoria não encontrada"}), 404
    try:
        task = task_service.create_task(values, user_id, category_id)
    except Exception:
        task_service.rollback()
        current_app.logger.exception("Task creation failed")
        return jsonify({"error": "Erro ao criar task"}), 500
    return jsonify(task.to_dict()), 201


@task_bp.put("/tasks/<int:task_id>")
@token_required
def update_task(task_id):
    task = task_service.get_task_for_actor(task_id, g.current_user)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404
    if not _can_manage(task):
        return jsonify({"error": "Acesso negado"}), 403
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Dados inválidos"}), 400
    values, error = _validate_task_data(data, partial=True)
    if error:
        return jsonify(error), 400
    elevated = g.current_user.role in ELEVATED_ROLES
    if "user_id" in data:
        if not elevated:
            return jsonify({"error": "Apenas administradores podem reatribuir tasks"}), 403
        user_id = data["user_id"]
        if user_id is not None and (type(user_id) is not int or not task_service.get_user(user_id)):
            return jsonify({"error": "Usuário não encontrado"}), 404
        task.user_id = user_id
    if "category_id" in data:
        category_id = data["category_id"]
        if category_id is not None and (type(category_id) is not int or not task_service.get_category(category_id)):
            return jsonify({"error": "Categoria não encontrada"}), 404
        task.category_id = category_id
    for field, value in values.items():
        setattr(task, field, value)
    task.updated_at = datetime.utcnow()
    try:
        task_service.save_task(task)
    except Exception:
        task_service.rollback()
        current_app.logger.exception("Task update failed")
        return jsonify({"error": "Erro ao atualizar"}), 500
    return jsonify(task.to_dict()), 200


@task_bp.delete("/tasks/<int:task_id>")
@token_required
def delete_task(task_id):
    task = task_service.get_task_for_actor(task_id, g.current_user)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404
    if not _can_manage(task):
        return jsonify({"error": "Acesso negado"}), 403
    try:
        task_service.remove_task(task)
    except Exception:
        task_service.rollback()
        current_app.logger.exception("Task deletion failed")
        return jsonify({"error": "Erro ao deletar"}), 500
    return jsonify({"message": "Task deletada com sucesso"}), 200


@task_bp.get("/tasks/search")
@token_required
def search_tasks():
    query_text = request.args.get("q", "")
    status = request.args.get("status", "")
    priority_text = request.args.get("priority", "")
    user_id_text = request.args.get("user_id", "")
    if status and status not in VALID_STATUSES:
        return jsonify({"error": "Status inválido"}), 400
    try:
        priority = int(priority_text) if priority_text else None
        if priority is not None and not 1 <= priority <= 5:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Prioridade inválida"}), 400
    user_id = None
    if user_id_text:
        try:
            user_id = int(user_id_text)
        except ValueError:
            return jsonify({"error": "Usuário inválido"}), 400
        if g.current_user.role not in ELEVATED_ROLES and user_id != g.current_user.id:
            return jsonify({"error": "Acesso negado"}), 403
    tasks = task_service.search_tasks(g.current_user, query_text, status, priority, user_id)
    return jsonify([task.to_dict() for task in tasks]), 200


@task_bp.get("/tasks/stats")
@token_required
def task_stats():
    return jsonify(task_service.task_stats(g.current_user)), 200
