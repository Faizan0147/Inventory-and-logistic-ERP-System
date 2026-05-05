import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings


async def send_credentials_email(to_email: str, name: str, password: str) -> None:
    """Send an email with the user's login credentials."""

    subject = "Your GodaamX Account is Ready 🎉"
    html_body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <title>Welcome to GodaamX</title>
    </head>
    <body style="margin:0;padding:0;background-color:#f0f4f8;font-family:'Segoe UI',Arial,sans-serif;">

      <!-- Wrapper -->
      <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f0f4f8;padding:40px 0;">
        <tr>
          <td align="center">
            <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

              <!-- Header -->
              <tr>
                <td align="center" style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 60%,#0f3460 100%);border-radius:16px 16px 0 0;padding:48px 40px 36px;">
                  <div style="background:rgba(255,255,255,0.08);display:inline-block;padding:12px 28px;border-radius:50px;margin-bottom:20px;">
                    <span style="color:#e2b96f;font-size:13px;font-weight:600;letter-spacing:2px;text-transform:uppercase;">Warehouse Management</span>
                  </div>
                  <h1 style="margin:0;color:#ffffff;font-size:32px;font-weight:700;letter-spacing:-0.5px;">GodaamX</h1>
                  <p style="margin:10px 0 0;color:#94a3b8;font-size:14px;">Your account is ready to go</p>
                </td>
              </tr>

              <!-- Body -->
              <tr>
                <td style="background:#ffffff;padding:44px 48px;">

                  <!-- Greeting -->
                  <h2 style="margin:0 0 8px;color:#1a1a2e;font-size:22px;font-weight:700;">Welcome, {name}! 👋</h2>
                  <p style="margin:0 0 32px;color:#64748b;font-size:15px;line-height:1.6;">
                    Your registration has been approved by our admin team. Below are your login credentials to access the GodaamX platform.
                  </p>

                  <!-- Credentials Card -->
                  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;margin-bottom:32px;">
                    <tr>
                      <td style="padding:28px 32px;">
                        <p style="margin:0 0 20px;color:#94a3b8;font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;">Your Login Credentials</p>

                        <!-- Email row -->
                        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:16px;">
                          <tr>
                            <td style="padding:14px 18px;background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;">
                              <p style="margin:0 0 4px;color:#94a3b8;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px;">Email Address</p>
                              <p style="margin:0;color:#1a1a2e;font-size:15px;font-weight:600;">{to_email}</p>
                            </td>
                          </tr>
                        </table>

                        <!-- Password row -->
                        <table width="100%" cellpadding="0" cellspacing="0">
                          <tr>
                            <td style="padding:14px 18px;background:#1a1a2e;border-radius:8px;">
                              <p style="margin:0 0 4px;color:#94a3b8;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px;">Temporary Password</p>
                              <p style="margin:0;color:#e2b96f;font-size:16px;font-weight:700;font-family:'Courier New',monospace;letter-spacing:1px;">{password}</p>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>

                  <!-- Warning -->
                  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:32px;">
                    <tr>
                      <td style="padding:16px 20px;background:#fffbeb;border-left:4px solid #e2b96f;border-radius:0 8px 8px 0;">
                        <p style="margin:0;color:#92400e;font-size:14px;font-weight:600;">⚠️ Please change your password after your first login.</p>
                      </td>
                    </tr>
                  </table>

                  <!-- CTA Button -->
                  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:32px;">
                    <tr>
                      <td align="center">
                        <a href="#" style="display:inline-block;background:linear-gradient(135deg,#0f3460,#1a1a2e);color:#ffffff;text-decoration:none;padding:14px 40px;border-radius:8px;font-size:15px;font-weight:600;letter-spacing:0.5px;">
                          Login to GodaamX →
                        </a>
                      </td>
                    </tr>
                  </table>

                  <p style="margin:0;color:#94a3b8;font-size:13px;line-height:1.6;text-align:center;">
                    If you have any issues logging in, please contact your administrator.
                  </p>
                </td>
              </tr>

              <!-- Footer -->
              <tr>
                <td align="center" style="background:#1a1a2e;border-radius:0 0 16px 16px;padding:24px 40px;">
                  <p style="margin:0 0 6px;color:#e2b96f;font-size:14px;font-weight:700;">GodaamX</p>
                  <p style="margin:0;color:#475569;font-size:12px;">This is an automated message. Please do not reply to this email.</p>
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>

    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM_EMAIL
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _smtp_send, msg)


def _smtp_send(msg: MIMEMultipart) -> None:
    """Blocking SMTP send — called inside run_in_executor."""
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
