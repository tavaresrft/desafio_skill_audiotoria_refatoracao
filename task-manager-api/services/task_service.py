"""Task use cases and persistence queries, separated from HTTP handlers."""

from datetime import datetime

from sqlalchemy import case, func, or_
from sqlalchemy.orm import joinedload

from database import db
from models.category import Category
from models.task import Task
from models.user import User

ELEVATED_ROLES = {"admin", "manager"}


def _scope(query, actor):
    if actor.role not in ELEVATED_ROLES:
        return query.filter(Task.user_id == actor.id)
    return query


def list_tasks(actor):
    return _scope(Task.query.options(joinedload(Task.user), joinedload(Task.category)), actor).order_by(Task.id).all()


def get_task_for_actor(task_id, actor):
    return _scope(Task.query, actor).filter(Task.id == task_id).first()


def get_user(user_id):
    return db.session.get(User, user_id)


def get_category(category_id):
    return db.session.get(Category, category_id)


def create_task(values, user_id, category_id):
    task = Task(**values, user_id=user_id, category_id=category_id)
    db.session.add(task)
    db.session.commit()
    return task


def save_task(task):
    db.session.commit()
    return task


def remove_task(task):
    db.session.delete(task)
    db.session.commit()


def rollback():
    db.session.rollback()


def search_tasks(actor, query_text="", status="", priority=None, user_id=None):
    query = _scope(Task.query, actor)
    if query_text:
        query = query.filter(or_(Task.title.like(f"%{query_text}%"), Task.description.like(f"%{query_text}%")))
    if status:
        query = query.filter(Task.status == status)
    if priority is not None:
        query = query.filter(Task.priority == priority)
    if user_id is not None:
        query = query.filter(Task.user_id == user_id)
    return query.order_by(Task.id).all()


def task_stats(actor):
    query = db.session.query(
        func.count(Task.id).label("total"),
        func.sum(case((Task.status == "pending", 1), else_=0)).label("pending"),
        func.sum(case((Task.status == "in_progress", 1), else_=0)).label("in_progress"),
        func.sum(case((Task.status == "done", 1), else_=0)).label("done"),
        func.sum(case((Task.status == "cancelled", 1), else_=0)).label("cancelled"),
        func.sum(case((
            (Task.due_date < datetime.utcnow()) & (~Task.status.in_(["done", "cancelled"])), 1
        ), else_=0)).label("overdue"),
    )
    row = _scope(query, actor).one()
    total = row.total or 0
    done = row.done or 0
    return {
        "total": total,
        "pending": row.pending or 0,
        "in_progress": row.in_progress or 0,
        "done": done,
        "cancelled": row.cancelled or 0,
        "overdue": row.overdue or 0,
        "completion_rate": round((done / total) * 100, 2) if total else 0,
    }
