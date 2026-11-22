"""Idempotently add local demo records without deleting existing data."""

import os
from datetime import datetime, timedelta

from app import app, db
from models.category import Category
from models.task import Task
from models.user import User


def seed_data():
    admin_password = os.getenv("SEED_ADMIN_PASSWORD")
    demo_password = os.getenv("SEED_DEMO_PASSWORD")
    if not admin_password or len(admin_password) < 8:
        raise RuntimeError("Defina SEED_ADMIN_PASSWORD com pelo menos 8 caracteres")
    if not demo_password or len(demo_password) < 8:
        raise RuntimeError("Defina SEED_DEMO_PASSWORD com pelo menos 8 caracteres")

    with app.app_context():
        users = [
            ("João Silva", "joao@email.com", admin_password, "admin"),
            ("Maria Santos", "maria@email.com", demo_password, "user"),
            ("Pedro Oliveira", "pedro@email.com", demo_password, "manager"),
        ]
        by_email = {}
        for name, email, password, role in users:
            user = User.query.filter_by(email=email).first()
            if user is None:
                user = User(name=name, email=email, role=role, active=True)
                user.set_password(password)
                db.session.add(user)
                db.session.flush()
            by_email[email] = user

        categories = [
            ("Backend", "Tarefas de backend", "#3498db"),
            ("Frontend", "Tarefas de frontend", "#2ecc71"),
            ("DevOps", "Tarefas de infraestrutura", "#e74c3c"),
            ("Bug", "Correção de bugs", "#e67e22"),
        ]
        category_by_name = {}
        for name, description, color in categories:
            category = Category.query.filter_by(name=name).first()
            if category is None:
                category = Category(name=name, description=description, color=color)
                db.session.add(category)
                db.session.flush()
            category_by_name[name] = category

        now = datetime.utcnow()
        sample_tasks = [
            ("Implementar autenticação JWT", "Adicionar autenticação real com JWT", "pending", 1, "joao@email.com", "Backend", now - timedelta(days=3), None),
            ("Criar tela de login", "Tela de login responsiva", "in_progress", 2, "maria@email.com", "Frontend", now + timedelta(days=5), None),
            ("Configurar CI/CD", "Pipeline com GitHub Actions", "done", 2, "pedro@email.com", "DevOps", None, "devops,ci,github"),
            ("Corrigir bug no filtro de busca", "Filtro não funciona com caracteres especiais", "pending", 1, "joao@email.com", "Bug", now - timedelta(days=1), None),
            ("Adicionar paginação na API", "Endpoints retornam todos os registros", "pending", 3, "joao@email.com", "Backend", now + timedelta(days=10), None),
            ("Escrever testes unitários", "Cobertura mínima de 80%", "pending", 2, "maria@email.com", "Backend", None, None),
            ("Documentar API com Swagger", "Gerar documentação automática", "cancelled", 4, "pedro@email.com", "Backend", None, None),
            ("Refatorar models", "Melhorar organização dos models", "in_progress", 3, "maria@email.com", "Backend", None, "refactor,tech-debt"),
            ("Configurar monitoramento", "Prometheus + Grafana", "pending", 4, "pedro@email.com", "DevOps", now + timedelta(days=20), None),
            ("Melhorar validações de input", "Usar marshmallow ou pydantic", "pending", 3, "joao@email.com", "Backend", None, "improvement,validation"),
        ]
        for title, description, status, priority, email, category_name, due_date, tags in sample_tasks:
            if Task.query.filter_by(title=title).first():
                continue
            db.session.add(Task(
                title=title,
                description=description,
                status=status,
                priority=priority,
                user_id=by_email[email].id,
                category_id=category_by_name[category_name].id,
                due_date=due_date,
                tags=tags,
            ))
        db.session.commit()
        app.logger.info(
            "Seed concluído: %s usuários, %s categorias, %s tasks",
            User.query.count(), Category.query.count(), Task.query.count(),
        )


if __name__ == "__main__":
    seed_data()
