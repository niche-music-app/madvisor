"""Checks and tidies feed.json before it's published. Run: python3 tools/check_feed.py

- Rejects the file if it isn't valid or an entry is missing required fields.
- Drops entries whose deadline (and event date) have passed.
- Fills lat/lon for any entry with a location, using postcodes.io.
- Refuses anything that looks like personal data about a user (emails, phone numbers).
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

FEED = Path(__file__).resolve().parent.parent / "feed.json"
TYPES = {"Gig", "Grant / funding", "Competition", "Other"}
DISCIPLINES = {"Any creative", "Any musician", "Rapper / MC", "Singer", "DJ", "Producer", "Band", "Songwriter",
               "Instrumentalist", "Visual artist", "Photographer", "Filmmaker", "Dancer", "Poet / spoken word",
               "Writer", "Other creative"}
STAGES = {"just starting", "emerging", "developing", "established"}
REQUIRED = ["id", "name", "type", "disciplines", "link", "verified"]
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE = re.compile(r"(?:\+44|\b0)\s?7\d{3}\s?\d{6}\b")
POSTCODE = re.compile(r"\b([A-Z]{1,2}\d[A-Z\d]?)\s*(\d[A-Z]{2})\b", re.I)
PLACE_TYPES = ["City", "Town", "Other Settlement", "Suburban Area", "Village", "Hamlet"]


def get(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return json.load(r).get("result")
    except Exception:
        return None


def locate(text):
    m = POSTCODE.search(text)
    if m:
        res = get("https://api.postcodes.io/postcodes/" + urllib.parse.quote(m.group(1) + m.group(2)))
        if res:
            return res["latitude"], res["longitude"]
    for part in reversed([p.strip() for p in text.split(",") if p.strip()]):
        res = get("https://api.postcodes.io/places?limit=20&q=" + urllib.parse.quote(part))
        if res:
            q = part.lower()

            def rank(p):
                area = f"{p.get('county_unitary') or ''} {p.get('district_borough') or ''}".lower()
                t = p.get("local_type")
                return ((p.get("name_1") or "").lower() != q, q not in area,
                        PLACE_TYPES.index(t) if t in PLACE_TYPES else 9)
            best = min(res, key=rank)
            return best["latitude"], best["longitude"]
    return None


def still_open(o, today):
    if o.get("rolling"):
        return True
    dates = [d for d in (o.get("deadline"), o.get("event_date")) if d]
    return not dates or max(date.fromisoformat(d) for d in dates) >= today


def main():
    feed = json.loads(FEED.read_text())
    today = date.today()
    errors, kept, seen = [], [], set()
    for o in feed["opportunities"]:
        missing = [k for k in REQUIRED if not o.get(k)]
        if missing:
            errors.append(f"{o.get('name', '?')}: missing {missing}")
            continue
        if o["type"] not in TYPES:
            errors.append(f"{o['name']}: bad type {o['type']!r}")
        bad = set(o["disciplines"]) - DISCIPLINES
        if bad:
            errors.append(f"{o['name']}: unknown disciplines {sorted(bad)}")
        bad = {s.lower() for s in o.get("career_stages", [])} - STAGES
        if bad:
            errors.append(f"{o['name']}: unknown career stages {sorted(bad)}")
        if not o["link"].startswith("https://") and not o["link"].startswith("http://"):
            errors.append(f"{o['name']}: link must be a web address")
        for f in ("deadline", "event_date", "verified", "added"):
            if o.get(f):
                try:
                    date.fromisoformat(o[f])
                except ValueError:
                    errors.append(f"{o['name']}: {f} must be YYYY-MM-DD")
        if o["id"] in seen or o["link"] in seen:
            errors.append(f"{o['name']}: duplicate id or link")
        seen.update({o["id"], o["link"]})
        text = json.dumps(o)
        if EMAIL.search(text) or PHONE.search(text):
            errors.append(f"{o['name']}: contains an email address or phone number; remove it")
        if errors:
            continue
        if not still_open(o, today):
            print(f"expired, removed: {o['name']}")
            continue
        if o.get("location") and (o.get("lat") is None or o.get("lon") is None):
            ll = locate(o["location"])
            if ll:
                o["lat"], o["lon"] = ll
            else:
                print(f"couldn't locate {o['location']!r} for {o['name']}")
        kept.append(o)
    if errors:
        print("NOT SAVED. Fix these:\n- " + "\n- ".join(errors))
        sys.exit(1)
    kept.sort(key=lambda o: o.get("deadline") or o.get("event_date") or "9999")
    feed["opportunities"] = kept
    feed["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    FEED.write_text(json.dumps(feed, indent=1, ensure_ascii=False) + "\n")
    print(f"ok: {len(kept)} open opportunities")


if __name__ == "__main__":
    main()
