"""
Simple SMTP email helper for sending login credentials.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings


async def send_credentials_email(to_email: str, name: str, password: str) -> None:
    """Send an email with the user's login credentials."""

    subject = "Your Warehouse ERP Login Credentials"
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>Welcome to Warehouse ERP, {name}!</h2>
        <p>Your account has been approved. Here are your login credentials:</p>
        <table style="border-collapse: collapse; margin: 16px 0;">
            <tr>
                <td style="padding: 8px 16px; font-weight: bold;">Email:</td>
                <td style="padding: 8px 16px;">{to_email}</td>
            </tr>
            <tr>
                <td style="padding: 8px 16px; font-weight: bold;">Password:</td>
                <td style="padding: 8px 16px;"><code>{password}</code></td>
            </tr>
        </table>
        <p>Please change your password after your first login.</p>
        <p style="color: #888; font-size: 12px;">
            This is an automated message from Warehouse ERP. Do not reply.
        </p>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM_EMAIL
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    # Send via SMTP (runs in the default executor to avoid blocking the event loop)
    import asyncio

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _smtp_send, msg)


def _smtp_send(msg: MIMEMultipart) -> None:
    """Blocking SMTP send — called inside run_in_executor."""
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
