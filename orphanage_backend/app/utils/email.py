import resend
from app.core.config import settings
from typing import Optional


def _is_email_configured() -> bool:
    """Return True only if Resend API key is configured."""
    return bool(settings.RESEND_API_KEY)


async def _send(subject: str, recipients: list, body: str):
    if not _is_email_configured():
        print(f"⚠️  Resend API key not configured — skipping '{subject}' to {recipients}")
        return
    try:
        resend.api_key = settings.RESEND_API_KEY
        resend.Emails.send({
            "from": settings.MAIL_FROM,
            "to": recipients,
            "subject": subject,
            "html": body,
        })
        print(f"✅ Email sent: '{subject}' to {recipients}")
    except Exception as e:
        print(f"⚠️  Resend email failed: {e}")


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


# ── Welcome ───────────────────────────────────────────────────────────────────

async def send_welcome_email(recipient_email: str, name: str, role: str):
    if role == "user":
        content = f"""
            <p>Dear <strong>{name}</strong>,</p>
            <p>🎉 Welcome to <strong>KindConnect</strong>! Your donor account has been created successfully.</p>
            <p>You can now:</p>
            <ul style="color:#555;line-height:1.9;">
                <li>💰 Donate money to orphanages</li>
                <li>📦 Donate items like clothes, food, and books</li>
                <li>📅 Book appointments to visit orphanages</li>
                <li>⭐ Leave feedback after your donations</li>
            </ul>
            <p>Every act of kindness makes a difference. Thank you for joining us!</p>
            <p style="margin-top:30px;">Warm regards,<br/><strong>KindConnect Team</strong></p>"""
        subject = "Welcome to KindConnect — Start Making a Difference! 🏠"
        color, htxt = "#dc2626", "Welcome to KindConnect 🏠"
    else:
        content = f"""
            <p>Dear <strong>{name}</strong>,</p>
            <p>🎉 Your orphanage has been successfully registered on <strong>KindConnect</strong>!</p>
            <p>Your profile is now live and donors can find you.</p>
            <p>Through your dashboard you can:</p>
            <ul style="color:#555;line-height:1.9;">
                <li>📥 View and confirm received donations</li>
                <li>📅 Manage appointment requests from donors</li>
                <li>⭐ See feedback left by donors</li>
            </ul>
            <p>Thank you for being part of our mission to help children in need.</p>
            <p style="margin-top:30px;">Warm regards,<br/><strong>KindConnect Team</strong></p>"""
        subject = "Your Orphanage is Now Live on KindConnect! 🏠"
        color, htxt = "#1d4ed8", "Orphanage Registered Successfully 🏠"

    await _send(subject, [recipient_email], _wrap(content, color, htxt))


# ── Donation Greeting ─────────────────────────────────────────────────────────

async def send_donation_greeting(
    recipient_email: str,
    donor_name: str,
    donation_type: str,
    orphanage_name: str,
    money_details: Optional[dict] = None,
    item_details: Optional[dict] = None,
):
    if donation_type == "money" and money_details:
        amount  = money_details.get("amount", 0)
        method  = money_details.get("payment_method", "other").replace("_", " ").title()
        summary = f"""
            <p style="margin:5px 0;">Type: <strong>Money Donation</strong></p>
            <p style="margin:5px 0;">Amount: <strong style="color:#16a34a;">₹{amount:,.2f}</strong></p>
            <p style="margin:5px 0;">Payment Method: {method}</p>"""
        subject = f"Thank You for Your Donation of ₹{amount:,.2f} to {orphanage_name} 💚"
        intro   = f"We are deeply grateful for your monetary donation of <strong style='color:#16a34a;'>₹{amount:,.2f}</strong> to <strong>{orphanage_name}</strong>."
    else:
        items  = item_details.get("items", []) if item_details else []
        qty    = item_details.get("quantity_description", "") if item_details else ""
        cond   = (item_details.get("condition", "good") if item_details else "good").title()
        pickup = "Yes" if (item_details or {}).get("pickup_required") else "No"
        paddr  = (item_details or {}).get("pickup_address", "")
        ilist  = "".join(f"<li>{i.title()}</li>" for i in items)
        summary = f"""
            <p style="margin:5px 0;">Type: <strong>Item Donation</strong></p>
            <p style="margin:5px 0;">Items:<ul style="margin:4px 0 4px 20px;">{ilist}</ul></p>
            {"<p style='margin:5px 0;'>Description: "+qty+"</p>" if qty else ""}
            <p style="margin:5px 0;">Condition: {cond}</p>
            <p style="margin:5px 0;">Pickup Required: {pickup}</p>
            {"<p style='margin:5px 0;'>Pickup Address: "+paddr+"</p>" if paddr else ""}"""
        subject = f"Thank You for Your Item Donation to {orphanage_name} 💚"
        intro   = f"We are grateful for your donation of <strong>{', '.join(i.title() for i in items)}</strong> to <strong>{orphanage_name}</strong>."

    content = f"""
        <p>Dear <strong>{donor_name}</strong>,</p>
        <p>{intro}</p>
        <p>Your kindness will make a real difference in children's lives.</p>
        <div style="background:#f9f9f9;padding:15px;border-left:4px solid #16a34a;margin:20px 0;">
            <p style="margin:0 0 8px 0;"><strong>Donation Summary:</strong></p>
            <p style="margin:5px 0;">Donor: {donor_name}</p>
            <p style="margin:5px 0;">Orphanage: {orphanage_name}</p>
            {summary}
        </div>
        <p>You can leave feedback from your dashboard!</p>
        <p style="margin-top:30px;">With heartfelt gratitude,<br/><strong>KindConnect Team</strong></p>"""

    await _send(subject, [recipient_email], _wrap(content, "#16a34a", "💚 Thank You for Your Donation!"))


# ── Appointment ───────────────────────────────────────────────────────────────

async def send_appointment_email(
    recipient_email: str,
    donor_name: str,
    orphanage_name: str,
    appointment_date: str,
    appointment_time: str,
    purpose: str,
    status: str,
):
    status_map = {
        "pending":  ("⏳ Appointment Received",   "#f59e0b", "Your appointment request has been received and is awaiting confirmation."),
        "approved": ("✅ Appointment Approved!",   "#16a34a", "Great news! Your appointment has been <strong>approved</strong>. Please arrive on time."),
        "rejected": ("❌ Appointment Unavailable", "#dc2626", "Unfortunately your appointment could not be accommodated. Please try a different date or time."),
    }
    emoji, color, status_msg = status_map.get(status, ("📅 Appointment Update", "#6b7280", "Your appointment status has been updated."))

    content = f"""
        <p>Dear <strong>{donor_name}</strong>,</p>
        <p>{status_msg}</p>
        <div style="background:#f9f9f9;padding:15px;border-left:4px solid {color};margin:20px 0;">
            <p style="margin:0 0 8px 0;"><strong>Appointment Details:</strong></p>
            <p style="margin:5px 0;">🏠 Orphanage: <strong>{orphanage_name}</strong></p>
            <p style="margin:5px 0;">📅 Date: <strong>{appointment_date}</strong></p>
            <p style="margin:5px 0;">🕐 Time: <strong>{appointment_time}</strong></p>
            <p style="margin:5px 0;">📝 Purpose: {purpose}</p>
            <p style="margin:5px 0;">Status: <strong style="color:{color};">{status.upper()}</strong></p>
        </div>
        <p style="margin-top:30px;">Regards,<br/><strong>KindConnect Team</strong></p>"""

    await _send(
        f"{emoji} Appointment {status.title()} — {orphanage_name}",
        [recipient_email],
        _wrap(content, color, f"{emoji} Appointment {status.title()}")
    )
