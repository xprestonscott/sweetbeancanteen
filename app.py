"""
Sweet Bean Canteen — demo site
Run:  pip install flask
      python app.py
Then open http://127.0.0.1:5000
"""
import calendar
import os
from datetime import date, datetime
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, abort)

import models
from emailer import notify_owner

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# Owner password for the admin page (set ADMIN_PASSWORD on Render).
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "sweetbean")

models.init_db()


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login", next=request.path))
        return f(*args, **kwargs)
    return wrapper

# ---------------------------------------------------------------
# BUSINESS INFO (real — pulled from their public listings)
# ---------------------------------------------------------------
BUSINESS = {
    "name": "Sweet Bean Canteen",
    "tagline": "Specialty coffee, brunch & Sweet Bean Canteen Mobile — right off Main Street.",
    "address": "217 W Main St, Chouteau, OK 74337",
    "phone": "(918) 803-3043",
    "phone_href": "tel:+19188033043",
    "hours": [
        ("Monday",    "6:30 AM – 2:00 PM"),
        ("Tuesday",   "6:30 AM – 2:00 PM"),
        ("Wednesday", "6:30 AM – 6:00 PM"),
        ("Thursday",  "6:30 AM – 6:00 PM"),
        ("Friday",    "6:30 AM – 6:00 PM"),
        ("Saturday",  "8:00 AM – 2:00 PM"),
        ("Sunday",    "Closed"),
    ],
    "facebook": "https://www.facebook.com/profile.php?id=100087205220380",
    "doordash": "https://www.doordash.com/store/sweet-bean-canteen-chouteau-34474227/",
    # Keyless Google Maps embed (no API key needed for this iframe style)
    "map_embed": "https://maps.google.com/maps?q=217+W+Main+St,+Chouteau,+OK+74337&z=15&output=embed",
}

# ---------------------------------------------------------------
# MENU HIGHLIGHTS (demo — confirm names/prices with the client)
# ---------------------------------------------------------------
MENU = [
    {
        "name": "Grandma's Cookies Latte",
        "desc": "Warm cookie sweetness. Espresso backbone. Tastes like a hug.",
        "tag": "Fan favorite",
    },
    {
        "name": "Peaches n Cream",
        "desc": "Bright peach, silky cream. Summer in a 24oz cup.",
        "tag": "Seasonal",
    },
    {
        "name": "Fresh Fruit Teas",
        "desc": "Iced tea with real fruit. No syrup-lab shortcuts.",
        "tag": "Refresher",
    },
    {
        "name": "Croissant Sandwiches",
        "desc": "Flaky, buttery, built to order. Wraps and platters too.",
        "tag": "Brunch",
    },
]

# ---------------------------------------------------------------
# REVIEWS (demo placeholders written from real review sentiment —
# replace with exact quotes from their Google listing before launch)
# ---------------------------------------------------------------
REVIEWS = [
    {"name": "Kayla R.",   "text": "The lattes here are really, really good. Grandma's Cookies is dangerous — I get one every morning now."},
    {"name": "Mike T.",    "text": "Friendly service, great coffee, small-town gem. You will enjoy the atmosphere every single time."},
    {"name": "Jess H.",    "text": "They have new items all the time. Follow them on Facebook or you'll miss the good stuff."},
    {"name": "Dana W.",    "text": "Best coffee stop between Pryor and Tulsa, and it's not close. The fruit teas are unreal."},
    {"name": "Cody B.",    "text": "Stopped in while working in the area — happy to find a real dedicated coffee shop out here."},
    {"name": "Amber L.",   "text": "They catered our event and everyone was still talking about the coffee a week later."},
    {"name": "Travis M.",  "text": "Iced caramel. That's it. That's the review. Yummm."},
    {"name": "Shelby K.",  "text": "Largest coffee menu I've seen anywhere, and somehow everything I've tried is a hit."},
]

# ---------------------------------------------------------------
# CUSTOMER FAVORITES (client-supplied drink features — swap the files
# in static/img/favorites/ and update the captions below)
# ---------------------------------------------------------------
GALLERY = [
    {"src": "img/favorites/pryor-strong-latte.jpg", "alt": "Pryor Strong Latte — espresso layered with creamy sweetness and chocolate drizzle, in memory of Cody Pryor", "cap": "Pryor Strong Latte"},
    {"src": "img/favorites/grandmas-cookies-latte.jpg", "alt": "Grandma's Cookies iced macchiato latte with caramel drizzle", "cap": "Grandma's Cookies Iced Macchiato"},
    {"src": "img/favorites/ms-bougee-latte.jpg", "alt": "Ms. Bougee Latte with cookie butter, cinnamon and chocolate drizzle", "cap": "Ms. Bougee Latte"},
]

# ---------------------------------------------------------------
# EVENTS + BLOCKED DAYS (demo data — this becomes the owner-managed
# calendar in the real build)
#   EVENTS: where the trailer will be on a given date (public)
#   BLOCKED: dates unavailable for event/catering bookings
# ---------------------------------------------------------------
def gallery_items():
    """Drop real photos (saved from their Facebook page) into
    static/img/gallery/ and they automatically replace the placeholders
    below — no code changes needed."""
    folder = os.path.join(app.static_folder, "img", "gallery")
    if os.path.isdir(folder):
        exts = (".jpg", ".jpeg", ".png", ".webp")
        real = sorted(f for f in os.listdir(folder) if f.lower().endswith(exts))
        if real:
            return [{"src": "img/gallery/" + f, "alt": "Sweet Bean Canteen"} for f in real]
    return GALLERY


@app.route("/")
def home():
    return render_template(
        "index.html",
        biz=BUSINESS,
        menu=MENU,
        reviews=REVIEWS,
        events=models.all_events()[:4],
        gallery=gallery_items(),
    )


@app.route("/events")
def events():
    try:
        year = int(request.args.get("y", date.today().year))
        month = int(request.args.get("m", date.today().month))
        date(year, month, 1)
    except (ValueError, TypeError):
        year, month = date.today().year, date.today().month

    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdayscalendar(year, month)
    month_events = models.events_for_month(year, month)

    prev_y, prev_m = (year - 1, 12) if month == 1 else (year, month - 1)
    next_y, next_m = (year + 1, 1) if month == 12 else (year, month + 1)

    return render_template(
        "events.html",
        biz=BUSINESS,
        weeks=weeks,
        year=year,
        month=month,
        month_name=calendar.month_name[month],
        events=month_events,
        today=date.today().isoformat(),
        prev_link=f"/events?y={prev_y}&m={prev_m}",
        next_link=f"/events?y={next_y}&m={next_m}",
        iso=lambda d: date(year, month, d).isoformat() if d else "",
        sent=request.args.get("sent") == "1",
    )


@app.route("/events/request", methods=["POST"])
def request_event():
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    phone = (request.form.get("phone") or "").strip()
    day = (request.form.get("day") or "").strip()
    details = (request.form.get("details") or "").strip()

    if not name or not (email or phone):
        flash("Please add your name and a way to reach you.")
        return redirect(url_for("events"))

    models.add_request(name, email, phone, day, details)
    notify_owner({"name": name, "email": email, "phone": phone,
                  "day": day, "details": details})
    return redirect(url_for("events", sent="1"))


# ---------------------- Owner admin ----------------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(request.args.get("next") or url_for("admin"))
        flash("Wrong password.")
    return render_template("admin_login.html", biz=BUSINESS)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("home"))


@app.route("/admin")
@login_required
def admin():
    return render_template(
        "admin.html",
        biz=BUSINESS,
        events=models.all_events(),
        requests=models.all_requests(),
        today=date.today().isoformat(),
    )


@app.route("/admin/event/add", methods=["POST"])
@login_required
def admin_add_event():
    day = (request.form.get("day") or "").strip()
    title = (request.form.get("title") or "").strip()
    location = (request.form.get("location") or "").strip()
    time_text = (request.form.get("time_text") or "").strip()
    blocked = request.form.get("blocked") == "on"
    if day and (title or blocked):
        models.add_event(day, title or "Unavailable", location, time_text, blocked)
        flash("Saved.")
    else:
        flash("A date and a title are required.")
    return redirect(url_for("admin"))


@app.route("/admin/event/<int:event_id>/delete", methods=["POST"])
@login_required
def admin_delete_event(event_id):
    models.delete_event(event_id)
    flash("Removed.")
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True)
