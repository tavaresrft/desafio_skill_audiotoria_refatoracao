"""User account use cases and persistence access."""

from sqlalchemy import func

from database import db
from models.task import Task
from models.user import User


def list_users_with_task_counts():
    task_counts = (
        db.session.query(Task.user_id, func.count(Task.id).label("task_count"))
        .group_by(Task.user_id)
        .subquery()
    )
    return (
        db.session.query(User, func.coalesce(task_counts.c.task_count, 0))
        .outerjoin(task_counts, User.id == task_counts.c.user_id)
        .order_by(User.id)
        .all()
    )


def get_user(user_id):
    return db.session.get(User, user_id)


def find_by_email(email):
    return User.query.filter_by(email=email).first()


def build_public_user(name, email, password):
    user = User(name=name, email=email, role="user", active=True)
    user.set_password(password)
    return user


def get_user_tasks(user_id):
    return Task.query.filter_by(user_id=user_id).order_by(Task.id).all()


def create_user(user):
    db.session.add(user)
    db.session.commit()
    return user


def save_user(user):
    db.session.commit()
    return user


def delete_user(user):
    Task.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    db.session.delete(user)
    db.session.commit()


def authenticate(email, password):
    user = find_by_email(email)
    if not user or not user.check_password(password):
        return None, "invalid"
    if not user.active:
        return None, "inactive"
    db.session.commit()  # Persists the successful legacy-MD5 hash upgrade.
    return user, None


def rollback():
    db.session.rollback()
