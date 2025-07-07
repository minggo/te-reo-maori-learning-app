import smtplib
from email.message import EmailMessage
from app.core.config import settings

def send_verification_email(to_email: str, code: str) -> None:
    """
    Send a plain‐text email containing the verification code.
    This runs in a background thread/task so blocking smtplib is acceptable.
    """
    msg = EmailMessage()
    msg["Subject"] = "Your verification code"
    msg["From"] = settings.SMTP_SENDER
    msg["To"] = to_email
    msg.set_content(f"Your verification code is: {code}\nIt expires in {settings.VERIFICATION_CODE_EXPIRE_MINUTES} minutes.")

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.send_message(msg)
