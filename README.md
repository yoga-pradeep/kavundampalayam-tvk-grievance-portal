# TVK Makkal Sevai — Kavundampalayam

Citizen grievance & needs portal for the **Kavundampalayam MLA Constituency**
(AC 117, Coimbatore), representing **Dr. R.D. Kanimozhi Santhosh**, Tamilaga
Vettri Kazhagam (TVK).

## Features
- Bilingual (Tamil / English) interface — one-click language toggle, saved per visitor
- Complaint & Needs submission forms with ward → street cascading dropdowns
- Automatic Ticket ID generation (`TVK-EB-2026-XXXXXX`) with priority detection and SLA deadline
- Public "Track Complaint" page with a live status timeline
- "Use My Location" geolocation capture on the form
- Simple rule-based chat assistant (bottom-right widget) that answers common
  questions about filing complaints, tracking tickets, office contact info, etc.
- Staff login + dashboard to update ticket status (Assigned → In Progress → Resolved…)
- Embedded Google Map of Kavundampalayam
- TVK brand colours (red / gold) matching the party's official look

## Run locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Visit **http://localhost:5000**

## Demo staff login
- Email: `admin@tvkkavundampalayam.in`
- Password: `Kanimozhi@2026`

(Change this immediately in `data/staff.json` before going live — passwords are
stored in plain text in this demo build and should be hashed with
`werkzeug.security` for production use.)

## Project structure
```
app.py                  Flask app (routes, ticket logic, chatbot rules)
templates/               Jinja2 templates (base, index, track, login, dashboard)
static/css/style.css     TVK-themed styling
static/js/main.js        Language toggle, form logic, chatbot, tracking
static/img/              Honourable Chief Minister of Tamil Nadu & MLA photos, TVK flag, icons
data/tickets.json        Auto-created ticket "database" (flat JSON file)
data/staff.json          Auto-created staff login list
```

## Notes for production
- Replace the flat-file JSON storage with a real database (SQLite/PostgreSQL).
- Hash staff passwords (`werkzeug.security.generate_password_hash`).
- Replace the rule-based chatbot with a real LLM API call if desired — the
  `/api/chat` route is a clean drop-in point.
- Add SMS/WhatsApp notifications on status change.
- Update ward/street data to match the official CCMC ward delimitation list.

---
**Designed and developed by Yoga Pradeep S & Team LiveUo**
