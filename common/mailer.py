import smtplib
from email.message import EmailMessage

from common.settings import get_settings


def send_email(*, to: str, subject: str, content: str) -> None:
    settings = get_settings()
    if not settings.smtp_host:
        print("MAIL_TO=", to)
        print("MAIL_SUBJECT=", subject)
        print(content)
        return

    msg = EmailMessage()
    msg["From"] = settings.mail_from
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(content)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as s:
        s.starttls()
        if settings.smtp_user and settings.smtp_password:
            s.login(settings.smtp_user, settings.smtp_password)
        s.send_message(msg)

