import httpx
from app.core.config import settings
from typing import Optional

def _is_email_configured() -> bool:
    return bool(settings.BREVO_API_KEY)

async def _send(subject: str, recipients: list, body: str):
    if not _is_email_configured():
        print(f"⚠️ Skipping Email: BREVO_API_KEY not found in settings.")
        return
    
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json"
    }

    payload = {
        "sender": {"name": "KindConnect", "email": settings.MAIL_FROM},
        "to": [{"email": email} for email in recipients],
        "subject": subject,
        "htmlContent": body
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            
        if response.status_code in [200, 201, 202]:
            print(f"✅ Email Sent: {subject}")
        else:
            # This will help you catch the 401 error in Render Logs
            print(f"❌ Brevo Error {response.status_code}: {response.text}")
            print(f"DEBUG: Key used starts with '{settings.BREVO_API_KEY[:5]}'")
            
    except Exception as e:
        print(f"⚠️ Connection Error: {e}")

def _wrap(content: str, header_color: str = "#dc2626", header_text: str = "KindConnect") -> str:
    return f"""
    <html><body style="font-family:Arial,sans-serif;color:#333;max-width:600px;margin:auto;">
        <div style="background:{header_color};padding:20px;text-align:center;border-radius:8px 8px 0 0;">
            <h1 style="color:white;margin:0;">{header_text}</h1>
        </div>
        <div style="padding:30px;border:1px solid #ddd;border-radius:0 0 8px 8px;">
            {content}
        </div>
        <p style="text-align:center;color:#aaa;font-size:12px;margin-top:10px;">
            This is an automated message. Please do not reply.
        </p>
    </body></html>"""

# --- Email Functions (Keep these as they were) ---

async def send_welcome_email(recipient_email: str, name: str, role: str):
    if role == "user":
        content = f"<p>Dear <strong>{name}</strong>,</p><p>🎉 Welcome to KindConnect!</p>"
        subject = "Welcome to KindConnect 🏠"
        color = "#dc2626"
    else:
        content = f"<p>Dear <strong>{name}</strong>,</p><p>🎉 Your orphanage is live!</p>"
        subject = "Orphanage Live 🏠"
        color = "#1d4ed8"
    await _send(subject, [recipient_email], _wrap(content, color, subject))

async def send_donation_greeting(recipient_email: str, donor_name: str, donation_type: str, orphanage_name: str, **kwargs):
    content = f"<p>Dear {donor_name},</p><p>Thank you for your {donation_type} donation to {orphanage_name}!</p>"
    await _send("Thank You for Your Donation 💚", [recipient_email], _wrap(content, "#16a34a", "Thank You!"))

async def send_appointment_email(recipient_email: str, donor_name: str, orphanage_name: str, appointment_date: str, appointment_time: str, purpose: str, status: str):
    content = f"<p>Appt with {orphanage_name} is {status}.</p>"
    await _send(f"Appointment {status}", [recipient_email], _wrap(content, "#f59e0b", "Appointment Update"))
