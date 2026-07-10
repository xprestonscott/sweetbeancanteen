# Sweet Bean Canteen — deploy notes

## Run locally
    pip install flask
    python app.py
    # http://127.0.0.1:5000
Local uses a SQLite file (sweetbean.db) automatically. No setup needed.

## Owner dashboard
    /admin  → password from ADMIN_PASSWORD (default "sweetbean" locally)
Add events, block dates, and read event requests there. Changes appear on
the public site instantly.

## Deploy to Render
1. Push this folder to GitHub.
2. Render → New → Web Service → point at the repo.
   - Build command:  pip install -r requirements.txt
   - Start command:  gunicorn app:app
3. Render → New → Postgres (free). Copy its Internal Database URL.
4. In the web service's Environment, add:
   - DATABASE_URL      = (the Postgres URL from step 3)
   - SECRET_KEY        = (any long random string)
   - ADMIN_PASSWORD    = (owner's password)
   - RESEND_API_KEY    = (from resend.com — free)   [optional but needed for email]
   - OWNER_EMAIL       = (where event requests should go)
   - FROM_EMAIL        = Sweet Bean Canteen <onboarding@resend.dev>
5. Deploy. Tables auto-create on first boot.

Without DATABASE_URL it runs on SQLite (fine for a demo, but Render's free
disk resets — use Postgres for the real site).

Without RESEND_API_KEY, event requests still save to the dashboard; they just
won't email. The console prints them so nothing is lost.
