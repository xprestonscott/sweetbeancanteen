"""
Sends the owner an email when a customer requests an event date.

If RESEND_API_KEY is set, it sends a real email via Resend (free tier).
If not, it just prints the notification to the console so the demo works
with zero setup.
"""
import os
import json
import urllib.request

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
OWNER_EMAIL = os.environ.get("OWNER_EMAIL", "owner@example.com")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "Sweet Bean Canteen <onboarding@resend.dev>")


def notify_owner(req):
    """req is a dict with name, email, phone, day, details."""
    subject = f"New event request from {req['name']}"
    body = (
        f"New event / catering request from the website:\n\n"
        f"Name:    {req['name']}\n"
        f"Email:   {req.get('email') or '-'}\n"
        f"Phone:   {req.get('phone') or '-'}\n"
        f"Date:    {req.get('day') or 'flexible'}\n\n"
        f"Details:\n{req.get('details') or '-'}\n"
    )

    if not RESEND_API_KEY:
        print("\n=== EVENT REQUEST (email not configured) ===")
        print(body)
        print("============================================\n")
        return False

    payload = json.dumps({
        "from": FROM_EMAIL,
        "to": [OWNER_EMAIL],
        "reply_to": req.get("email") or None,
        "subject": subject,
        "text": body,
    }).encode()

    request = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as resp:
            return resp.status < 300
    except Exception as e:  # noqa
        print("Email send failed:", e)
        return False
