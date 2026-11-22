"""Optional SMTP notifications configured exclusively through environment."""

import logging
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.notifications = []
        self.email_host = os.getenv("SMTP_HOST")
        self.email_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_user = os.getenv("SMTP_USER")
        self.email_password = os.getenv("SMTP_PASSWORD")

    def send_email(self, to, subject, body):
        if not all((self.email_host, self.email_user, self.email_password, to)):
            logger.warning("SMTP não configurado; notificação não enviada")
            return False
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.email_user
        message["To"] = to
        message.set_content(body)
        try:
            with smtplib.SMTP(self.email_host, self.email_port, timeout=10) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(message)
            return True
        except (OSError, smtplib.SMTPException):
            logger.exception("Falha no envio de notificação SMTP")
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\nStatus: {task.status}"
        )
        self.send_email(user.email, subject, body)
        self.notifications.append({
            "type": "task_assigned",
            "user_id": user.id,
            "task_id": task.id,
            "timestamp": datetime.utcnow(),
        })

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}"
        return self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [notification for notification in self.notifications if notification["user_id"] == user_id]
