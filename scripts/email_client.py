from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


class EmailClient:
    def __init__(self):
        self.smtp_user = os.environ.get("EMAIL_SMTP_USER", "").strip()
        self.smtp_password = os.environ.get("EMAIL_SMTP_PASSWORD", "").strip()
        self.email_to = os.environ.get("EMAIL_TO", "").strip()
        self.email_from = os.environ.get("EMAIL_FROM", "").strip() or self.smtp_user

        self._enabled = bool(self.smtp_user and self.smtp_password and self.email_to)

    def enabled(self) -> bool:
        return self._enabled

    def send(self, subject: str, body: str) -> None:
        if not self.enabled():
            return

        msg = EmailMessage()
        msg["From"] = self.email_from
        msg["To"] = self.email_to
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.smtp_user, self.smtp_password)
            smtp.send_message(msg)