import httpx
from app.core.config import settings
from typing import Optional


# ── Guard ─────────────────────────────────────────────────────────────────────

def _is_email_configured() -> bool:
    return bool(settings.BREVO_API_KEY)


# ── Core sender ───────────────────────────────────────────────────────────────

async def _send(subject: str, recipients: list, body: str):
    if not _is_email_configured():
        print(f"⚠️  Brevo not configured — skipping '{subject}' to {recipients}")
        return

    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json",
    }
    payload = {
        "sender":      {"name": "KindConnect", "email": settings.MAIL_FROM},
        "to":          [{"email": e} for e in recipients],
        "subject":     subject,
        "htmlContent": body,
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post("https://api.brevo.com/v3/smtp/email",
                                    headers=headers, json=payload, timeout=15)
        if res.status_code in (200, 201, 202):
            print(f"✅ Email sent: '{subject}' → {recipients}")
        else:
            print(f"❌ Brevo {res.status_code}: {res.text}")
    except Exception as e:
        print(f"⚠️  Email send failed: {e}")


# ── HTML builder ──────────────────────────────────────────────────────────────

def _wrap(content: str, header_color: str = "#dc2626", header_text: str = "KindConnect") -> str:
    """Wraps email body content in a polished, branded HTML shell."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>KindConnect</title>
</head>
<body style="margin:0;padding:0;background:#f4f4f5;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f5;padding:32px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0"
             style="max-width:600px;width:100%;background:#ffffff;border-radius:12px;
                    overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

        <!-- Header -->
        <tr>
          <td style="background:{header_color};padding:32px 40px;text-align:center;">
            <div style="font-size:28px;font-weight:700;color:white;letter-spacing:-0.5px;">
              🏠 KindConnect
            </div>
            <div style="color:rgba(255,255,255,0.85);font-size:13px;margin-top:6px;letter-spacing:0.5px;">
              MAKING A DIFFERENCE TOGETHER
            </div>
          </td>
        </tr>

        <!-- Title Bar -->
        <tr>
          <td style="background:{header_color}22;padding:16px 40px;border-bottom:1px solid {header_color}33;">
            <p style="margin:0;font-size:15px;font-weight:600;color:{header_color};">{header_text}</p>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:36px 40px;color:#374151;font-size:15px;line-height:1.7;">
            {content}
          </td>
        </tr>

        <!-- Divider -->
        <tr>
          <td style="padding:0 40px;">
            <hr style="border:none;border-top:1px solid #e5e7eb;margin:0;">
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="padding:24px 40px;text-align:center;">
            <p style="margin:0 0 6px;font-size:13px;color:#9ca3af;">
              © 2026 KindConnect · Making the world a better place
            </p>
            <p style="margin:0;font-size:12px;color:#d1d5db;">
              This is an automated message — please do not reply directly to this email.
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


def _button(text: str, url: str, color: str = "#dc2626") -> str:
    """Reusable CTA button for emails."""
    return f"""
    <div style="text-align:center;margin:28px 0 12px;">
      <a href="{url}" style="display:inline-block;background:{color};color:white;
         text-decoration:none;padding:14px 32px;border-radius:8px;font-weight:600;
         font-size:15px;letter-spacing:0.3px;">{text}</a>
    </div>"""


def _info_box(rows: list[tuple], accent: str = "#dc2626") -> str:
    """Renders a styled summary box. rows = list of (label, value) tuples."""
    items = "".join(f"""
      <tr>
        <td style="padding:8px 16px;font-weight:600;color:#6b7280;
                   font-size:13px;width:40%;white-space:nowrap;">{label}</td>
        <td style="padding:8px 16px;color:#111827;font-size:14px;">{value}</td>
      </tr>""" for label, value in rows)
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0"
           style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;
                  border-left:4px solid {accent};margin:20px 0;overflow:hidden;">
      {items}
    </table>"""


# ── Welcome — User ────────────────────────────────────────────────────────────

async def send_welcome_email(recipient_email: str, name: str, role: str):
    if role == "user":
        content = f"""
        <p style="font-size:22px;font-weight:700;color:#111827;margin:0 0 8px;">
          Welcome aboard, {name}! 🎉
        </p>
        <p style="color:#6b7280;margin:0 0 24px;">
          Your KindConnect donor account is ready. Here's what you can do:
        </p>

        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
          <tr>
            <td style="padding:10px 14px;background:#fef2f2;border-radius:8px;margin-bottom:8px;display:block;">
              💰 <strong>Donate money</strong> — UPI, bank transfer, cash or card
            </td>
          </tr>
          <tr><td style="height:8px;"></td></tr>
          <tr>
            <td style="padding:10px 14px;background:#fef2f2;border-radius:8px;">
              📦 <strong>Donate items</strong> — clothes, food, books, toys and more
            </td>
          </tr>
          <tr><td style="height:8px;"></td></tr>
          <tr>
            <td style="padding:10px 14px;background:#fef2f2;border-radius:8px;">
              📅 <strong>Book appointments</strong> — visit orphanages in person
            </td>
          </tr>
          <tr><td style="height:8px;"></td></tr>
          <tr>
            <td style="padding:10px 14px;background:#fef2f2;border-radius:8px;">
              ⭐ <strong>Share feedback</strong> — help us improve the platform
            </td>
          </tr>
        </table>

        <p style="color:#374151;">
          Every act of kindness — big or small — brings hope to a child who needs it.
          Thank you for choosing to make a difference.
        </p>

        <p style="margin-top:28px;color:#374151;">
          With warm regards,<br>
          <strong style="color:#dc2626;">The KindConnect Team</strong>
        </p>"""

        await _send(
            "Welcome to KindConnect — Your Journey Starts Here! 🏠",
            [recipient_email],
            _wrap(content, "#dc2626", "Account Created Successfully"),
        )

    else:
        content = f"""
        <p style="font-size:22px;font-weight:700;color:#111827;margin:0 0 8px;">
          Congratulations, {name}! 🎉
        </p>
        <p style="color:#6b7280;margin:0 0 24px;">
          Your orphanage is now <strong style="color:#16a34a;">live on KindConnect</strong>.
          Donors across the country can now find you and support your cause.
        </p>

        <p style="font-weight:600;color:#374151;margin-bottom:12px;">
          Your dashboard lets you:
        </p>

        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
          <tr>
            <td style="padding:10px 14px;background:#eff6ff;border-radius:8px;">
              📥 <strong>Review donations</strong> — confirm or manage incoming donations
            </td>
          </tr>
          <tr><td style="height:8px;"></td></tr>
          <tr>
            <td style="padding:10px 14px;background:#eff6ff;border-radius:8px;">
              📅 <strong>Manage appointments</strong> — approve or decline donor visit requests
            </td>
          </tr>
          <tr><td style="height:8px;"></td></tr>
          <tr>
            <td style="padding:10px 14px;background:#eff6ff;border-radius:8px;">
              ⭐ <strong>Read feedback</strong> — see what donors say about your orphanage
            </td>
          </tr>
        </table>

        <p style="color:#374151;">
          Thank you for joining our mission. Together, we can give every child the care they deserve.
        </p>

        <p style="margin-top:28px;color:#374151;">
          With gratitude,<br>
          <strong style="color:#1d4ed8;">The KindConnect Team</strong>
        </p>"""

        await _send(
            f"{name} is Now Live on KindConnect! 🏠",
            [recipient_email],
            _wrap(content, "#1d4ed8", "Orphanage Registered Successfully"),
        )


# ── Donation Thank-You ────────────────────────────────────────────────────────

async def send_donation_greeting(
    recipient_email: str,
    donor_name: str,
    donation_type: str,
    orphanage_name: str,
    money_details: Optional[dict] = None,
    item_details: Optional[dict] = None,
):
    if donation_type == "money" and money_details:
        amount = money_details.get("amount", 0)
        method = money_details.get("payment_method", "other").replace("_", " ").title()
        summary_rows = [
            ("Donation Type", "💰 Money"),
            ("Amount",        f"<strong style='color:#16a34a;font-size:18px;'>₹{amount:,.2f}</strong>"),
            ("Payment",       method),
            ("Orphanage",     orphanage_name),
            ("Donor",         donor_name),
        ]
        subject   = f"Thank You for Your ₹{amount:,.2f} Donation to {orphanage_name} 💚"
        hero_text = f"₹{amount:,.2f} donated"
        accent    = "#16a34a"
    else:
        items  = item_details.get("items", []) if item_details else []
        qty    = item_details.get("quantity_description", "") if item_details else ""
        cond   = (item_details.get("condition", "good") if item_details else "good").title()
        pickup = "Yes — pickup requested" if (item_details or {}).get("pickup_required") else "No — will drop off"
        paddr  = (item_details or {}).get("pickup_address", "")
        summary_rows = [
            ("Donation Type", "📦 Items"),
            ("Items",         ", ".join(i.title() for i in items)),
            ("Quantity",      qty or "—"),
            ("Condition",     cond),
            ("Pickup",        pickup + (f"<br><small>{paddr}</small>" if paddr else "")),
            ("Orphanage",     orphanage_name),
            ("Donor",         donor_name),
        ]
        subject   = f"Thank You for Your Item Donation to {orphanage_name} 💚"
        hero_text = f"{len(items)} item type(s) donated"
        accent    = "#16a34a"

    content = f"""
    <div style="text-align:center;background:linear-gradient(135deg,#f0fdf4,#dcfce7);
                border-radius:10px;padding:28px 20px;margin-bottom:28px;">
      <div style="font-size:40px;margin-bottom:8px;">💚</div>
      <p style="font-size:22px;font-weight:700;color:#15803d;margin:0 0 4px;">
        Thank You, {donor_name}!
      </p>
      <p style="color:#16a34a;font-size:14px;margin:0;">{hero_text}</p>
    </div>

    <p style="color:#374151;">
      Your generosity will make a <strong>real difference</strong> in the lives of children
      at <strong>{orphanage_name}</strong>. Every contribution — no matter the size —
      helps provide food, shelter, education, and love to those who need it most.
    </p>

    <p style="font-weight:600;color:#374151;margin:20px 0 4px;">Donation Summary</p>
    {_info_box(summary_rows, accent)}

    <p style="color:#374151;">
      The orphanage team will review and confirm your donation shortly.
      You can track its status anytime from your KindConnect dashboard.
    </p>

    <p style="margin-top:28px;color:#374151;">
      With heartfelt gratitude,<br>
      <strong style="color:#16a34a;">The KindConnect Team</strong>
    </p>"""

    await _send(subject, [recipient_email], _wrap(content, "#16a34a", "Donation Received 💚"))


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
    config = {
        "pending":  {
            "color":   "#f59e0b",
            "emoji":   "⏳",
            "title":   "Appointment Request Received",
            "headline": f"We've received your request, {donor_name}!",
            "message": (
                "Your appointment request has been sent to <strong>{org}</strong>. "
                "Their team will review it and get back to you soon."
            ),
        },
        "approved": {
            "color":   "#16a34a",
            "emoji":   "✅",
            "title":   "Appointment Approved!",
            "headline": f"Great news, {donor_name}!",
            "message": (
                "Your appointment at <strong>{org}</strong> has been <strong "
                "style='color:#16a34a;'>confirmed</strong>. Please arrive on time "
                "and bring any items you plan to donate."
            ),
        },
        "rejected": {
            "color":   "#dc2626",
            "emoji":   "❌",
            "title":   "Appointment Could Not Be Confirmed",
            "headline": f"We're sorry, {donor_name}",
            "message": (
                "Unfortunately <strong>{org}</strong> is unable to accommodate your "
                "appointment at the requested date or time. Please try booking "
                "a different slot — we'd love to see you there!"
            ),
        },
    }
    c = config.get(status, config["pending"])
    msg_text = c["message"].format(org=orphanage_name)
    color    = c["color"]

    summary_rows = [
        ("Orphanage",  orphanage_name),
        ("Date",       appointment_date),
        ("Time",       appointment_time),
        ("Purpose",    purpose),
        ("Status",     f"<strong style='color:{color};text-transform:uppercase;'>{status}</strong>"),
    ]

    content = f"""
    <div style="text-align:center;padding:24px 20px;background:#f9fafb;
                border-radius:10px;margin-bottom:28px;">
      <div style="font-size:40px;margin-bottom:8px;">{c["emoji"]}</div>
      <p style="font-size:20px;font-weight:700;color:#111827;margin:0 0 6px;">
        {c["headline"]}
      </p>
    </div>

    <p style="color:#374151;">{msg_text}</p>

    <p style="font-weight:600;color:#374151;margin:20px 0 4px;">Appointment Details</p>
    {_info_box(summary_rows, color)}

    {"<p style='color:#374151;'>We look forward to seeing you! If you need to reschedule, you can book a new appointment from your dashboard.</p>" if status == "approved" else ""}

    <p style="margin-top:28px;color:#374151;">
      Regards,<br>
      <strong style="color:{color};">The KindConnect Team</strong>
    </p>"""

    await _send(
        f"{c['emoji']} Appointment {status.title()} — {orphanage_name}",
        [recipient_email],
        _wrap(content, color, c["title"]),
    )
