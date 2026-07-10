"""
Storage for events and event requests.

Uses Postgres when DATABASE_URL is set (Render), otherwise a local SQLite
file for development. Same API either way, so the rest of the app doesn't
care which one is active.
"""
import os
from datetime import datetime

DATABASE_URL = os.environ.get("DATABASE_URL", "")
USE_PG = DATABASE_URL.startswith("postgres")

if USE_PG:
    import psycopg2
    import psycopg2.extras
    # Render sometimes hands out a "postgres://" URL; psycopg2 wants "postgresql://"
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    PH = "%s"  # placeholder style
else:
    import sqlite3
    SQLITE_PATH = os.path.join(os.path.dirname(__file__), "sweetbean.db")
    PH = "?"


def _connect():
    if USE_PG:
        return psycopg2.connect(DATABASE_URL, sslmode="require")
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist, and seed demo events once."""
    conn = _connect()
    cur = conn.cursor()
    if USE_PG:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                day DATE NOT NULL,
                title TEXT NOT NULL,
                location TEXT DEFAULT '',
                time_text TEXT DEFAULT '',
                blocked BOOLEAN DEFAULT FALSE
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                day DATE,
                details TEXT DEFAULT '',
                created TIMESTAMP DEFAULT NOW(),
                handled BOOLEAN DEFAULT FALSE
            )
        """)
    else:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT NOT NULL,
                title TEXT NOT NULL,
                location TEXT DEFAULT '',
                time_text TEXT DEFAULT '',
                blocked INTEGER DEFAULT 0
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                day TEXT,
                details TEXT DEFAULT '',
                created TEXT DEFAULT CURRENT_TIMESTAMP,
                handled INTEGER DEFAULT 0
            )
        """)
    conn.commit()

    # Seed a few demo events the first time only.
    cur.execute("SELECT COUNT(*) FROM events")
    count = cur.fetchone()[0]
    if count == 0:
        from datetime import date
        import calendar as _cal
        t = date.today()
        last = _cal.monthrange(t.year, t.month)[1]

        def d(day):
            return date(t.year, t.month, min(day, last)).isoformat()

        seed = [
            (d(11), "Chouteau Farmers Market", "119 W Main St, Chouteau", "8 AM - 1 PM", False),
            (d(18), "MidAmerica Industrial Park", "Pryor, OK", "7 AM - 11 AM", False),
            (d(25), "Downtown Pop-Up", "Main St, Chouteau", "9 AM - 2 PM", False),
            (d(14), "Private Event", "Booked", "All day", True),
        ]
        for row in seed:
            cur.execute(
                f"INSERT INTO events (day, title, location, time_text, blocked) "
                f"VALUES ({PH},{PH},{PH},{PH},{PH})", row
            )
        conn.commit()
    cur.close()
    conn.close()


def _norm(row):
    """Return a plain dict with consistent keys and an ISO day string."""
    d = dict(row)
    day = d.get("day")
    if hasattr(day, "isoformat"):
        day = day.isoformat()
    d["day"] = str(day)[:10] if day else ""
    d["blocked"] = bool(d.get("blocked"))
    return d


def events_for_month(year, month):
    """All events in a given month, keyed by ISO date string."""
    conn = _connect()
    cur = conn.cursor()
    prefix = f"{year:04d}-{month:02d}-"
    if USE_PG:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT * FROM events WHERE to_char(day, 'YYYY-MM-') = %s ORDER BY day", (prefix,)
        )
    else:
        cur.execute("SELECT * FROM events WHERE day LIKE ? ORDER BY day", (prefix + "%",))
    rows = [_norm(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    out = {}
    for r in rows:
        out[r["day"]] = r
    return out


def all_events():
    """Every event, soonest first — used for the homepage teaser."""
    conn = _connect()
    if USE_PG:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        cur = conn.cursor()
    cur.execute("SELECT * FROM events ORDER BY day")
    rows = [_norm(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def add_event(day, title, location, time_text, blocked=False):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO events (day, title, location, time_text, blocked) "
        f"VALUES ({PH},{PH},{PH},{PH},{PH})",
        (day, title, location, time_text, bool(blocked) if USE_PG else int(blocked)),
    )
    conn.commit()
    cur.close()
    conn.close()


def delete_event(event_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM events WHERE id = {PH}", (event_id,))
    conn.commit()
    cur.close()
    conn.close()


def add_request(name, email, phone, day, details):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO requests (name, email, phone, day, details) "
        f"VALUES ({PH},{PH},{PH},{PH},{PH})",
        (name, email, phone, day or None, details),
    )
    conn.commit()
    cur.close()
    conn.close()


def all_requests():
    conn = _connect()
    if USE_PG:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        cur = conn.cursor()
    cur.execute("SELECT * FROM requests ORDER BY created DESC")
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows
