"""Database-backed report calculations and category use cases."""

from datetime import datetime, timedelta

from sqlalchemy import case, func

from database import db
from models.category import Category
from models.task import Task
from models.user import User


def summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()
    status_counts = dict(db.session.query(Task.status, func.count(Task.id)).group_by(Task.status).all())
    priority_counts = dict(db.session.query(Task.priority, func.count(Task.id)).group_by(Task.priority).all())
    now = datetime.utcnow()
    overdue_tasks = Task.query.filter(
        Task.due_date < now,
        ~Task.status.in_(["done", "cancelled"]),
    ).order_by(Task.due_date, Task.id).all()
    seven_days_ago = now - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(Task.status == "done", Task.updated_at >= seven_days_ago).count()
    productivity_rows = (
        db.session.query(
            User.id,
            User.name,
            func.count(Task.id).label("total"),
            func.sum(case((Task.status == "done", 1), else_=0)).label("completed"),
        )
        .outerjoin(Task, Task.user_id == User.id)
        .group_by(User.id, User.name)
        .order_by(User.id)
        .all()
    )
    user_productivity = []
    for user_id, user_name, total, completed in productivity_rows:
        total = total or 0
        completed = completed or 0
        user_productivity.append({
            "user_id": user_id,
            "user_name": user_name,
            "total_tasks": total,
            "completed_tasks": completed,
            "completion_rate": round((completed / total) * 100, 2) if total else 0,
        })
    return {
        "generated_at": now.isoformat(),
        "overview": {"total_tasks": total_tasks, "total_users": total_users, "total_categories": total_categories},
        "tasks_by_status": {
            "pending": status_counts.get("pending", 0),
            "in_progress": status_counts.get("in_progress", 0),
            "done": status_counts.get("done", 0),
            "cancelled": status_counts.get("cancelled", 0),
        },
        "tasks_by_priority": {
            "critical": priority_counts.get(1, 0),
            "high": priority_counts.get(2, 0),
            "medium": priority_counts.get(3, 0),
            "low": priority_counts.get(4, 0),
            "minimal": priority_counts.get(5, 0),
        },
        "overdue": {
            "count": len(overdue_tasks),
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "due_date": str(task.due_date),
                    "days_overdue": (now - task.due_date).days,
                }
                for task in overdue_tasks
            ],
        },
        "recent_activity": {
            "tasks_created_last_7_days": recent_tasks,
            "tasks_completed_last_7_days": recent_done,
        },
        "user_productivity": user_productivity,
    }


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return None
    now = datetime.utcnow()
    row = db.session.query(
        func.count(Task.id).label("total"),
        func.sum(case((Task.status == "done", 1), else_=0)).label("done"),
        func.sum(case((Task.status == "pending", 1), else_=0)).label("pending"),
        func.sum(case((Task.status == "in_progress", 1), else_=0)).label("in_progress"),
        func.sum(case((Task.status == "cancelled", 1), else_=0)).label("cancelled"),
        func.sum(case(((Task.due_date < now) & (~Task.status.in_(["done", "cancelled"])), 1), else_=0)).label("overdue"),
        func.sum(case((Task.priority <= 2, 1), else_=0)).label("high_priority"),
    ).filter(Task.user_id == user_id).one()
    total, done = row.total or 0, row.done or 0
    return {
        "user": {"id": user.id, "name": user.name, "email": user.email},
        "statistics": {
            "total_tasks": total,
            "done": done,
            "pending": row.pending or 0,
            "in_progress": row.in_progress or 0,
            "cancelled": row.cancelled or 0,
            "overdue": row.overdue or 0,
            "high_priority": row.high_priority or 0,
            "completion_rate": round((done / total) * 100, 2) if total else 0,
        },
    }


def list_categories_with_counts():
    rows = (
        db.session.query(Category, func.count(Task.id).label("task_count"))
        .outerjoin(Task, Task.category_id == Category.id)
        .group_by(Category.id)
        .order_by(Category.id)
        .all()
    )
    return [{**category.to_dict(), "task_count": count} for category, count in rows]


def get_category(category_id):
    return db.session.get(Category, category_id)


def create_category(category):
    db.session.add(category)
    db.session.commit()
    return category


def save_category(category):
    db.session.commit()
    return category


def delete_category(category):
    db.session.delete(category)
    db.session.commit()


def rollback():
    db.session.rollback()
