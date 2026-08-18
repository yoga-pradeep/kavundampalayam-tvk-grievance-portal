"""
TVK Makkal Sevai — Kavundampalayam
Citizen Grievance & Needs Portal for Kavundampalayam MLA Constituency
MLA: Dr. R.D. Kanimozhi Santhosh (Tamilaga Vettri Kazhagam)

Designed and developed by Yoga Pradeep S & Team LiveUo
"""
import json
import os
import random
import string
from datetime import datetime, timedelta

from flask import Flask, render_template, request, jsonify, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "tvk-kavundampalayam-dev-secret-change-in-production"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TICKETS_FILE = os.path.join(DATA_DIR, "tickets.json")
STAFF_FILE = os.path.join(DATA_DIR, "staff.json")

os.makedirs(DATA_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Constituency reference data — Kavundampalayam (AC 117), Coimbatore
# Wards drawn from CCMC West Zone ward numbers that fall inside the
# Kavundampalayam assembly segment.
# ---------------------------------------------------------------------------
WARDS = [
    {"no": "16", "name_en": "Ward 16 - Edayarpalayam / TVS Nagar", "name_ta": "வார்டு 16 - ஏடையாரப்பாளையம் / டி.வி.எஸ். நகர்"},
    {"no": "17", "name_en": "Ward 17 - Kavundampalayam", "name_ta": "வார்டு 17 - கவுண்டம்பாளையம்"},
    {"no": "33", "name_en": "Ward 33 - Somayampalayam", "name_ta": "வார்டு 33 - சோமையம்பாளையம்"},
    {"no": "34", "name_en": "Ward 34 - Vellakinar", "name_ta": "வார்டு 34 - வெள்ளக்கினார்"},
    {"no": "35", "name_en": "Ward 35 - Chinnavedampatti", "name_ta": "வார்டு 35 - சின்னவேடம்பட்டி"},
    {"no": "36", "name_en": "Ward 36 - Sanganoor", "name_ta": "வார்டு 36 - சங்கநூர்"},
    {"no": "37", "name_en": "Ward 37 - Thudiyalur", "name_ta": "வார்டு 37 - துடியலூர்"},
    {"no": "41", "name_en": "Ward 41 - Maniyakaranpalayam", "name_ta": "வார்டு 41 - மணியாகரன்பாளையம்"},
    {"no": "44", "name_en": "Ward 44 - Rathinapuri", "name_ta": "வார்டு 44 - ரத்தினபுரி"},
    {"no": "45", "name_en": "Ward 45 - Nallampalayam", "name_ta": "வார்டு 45 - நல்லம்பாளையம்"},
]

STREETS_BY_WARD = {
    "16": ["Menon Layout", "TVS Nagar 1st Street", "Edayarpalayam Main Road", "Punes Colony Cross Street"],
    "17": ["Punes Colony 5th Street", "Kavundampalayam Main Road", "Kalyanasundaram Nagar", "Bharathi Nagar Street"],
    "33": ["Somayampalayam Main Road", "Sri Ram Nagar", "Kongu Nagar 2nd Street", "Anna Nagar Extension"],
    "34": ["Vellakinar Main Road", "Periyar Nagar Street", "Vellakinar Pirivu Road", "Nehru Nagar Cross"],
    "35": ["Chinnavedampatti Main Road", "Saravanampatti By-pass Road", "Kalapatti Link Road", "Krishna Nagar Street"],
    "36": ["Sanganoor Main Road", "Sanganoor Palayam Street", "Karumbu Vinayagar Koil Street", "Muthu Nagar"],
    "37": ["Thudiyalur Main Road", "Kumar Nagar Street", "Alagesan Road Extension", "Vinayaga Nagar"],
    "41": ["Veerasivaji Street", "Maniyakaranpalayam Main Road", "Chettipalayam Road", "Sathya Nagar"],
    "44": ["Rathinapuri Main Road", "Lakshmi Nagar Street", "Gandhi Road", "Kamaraj Street"],
    "45": ["Annaiyappan Street", "Nallampalayam Main Road", "Ganapathy Bye-pass Road", "Sengunthar Nagar"],
}

CATEGORIES = [
    {"key": "road", "en": "Road Maintenance", "ta": "சாலை பராமரிப்பு"},
    {"key": "water", "en": "Metro Water / Drinking Water", "ta": "மெட்ரோ வாட்டர் / குடிநீர்"},
    {"key": "streetlight", "en": "Street Light Failure", "ta": "தெரு விளக்கு பழுது"},
    {"key": "garbage", "en": "Garbage Collection", "ta": "குப்பை அகற்றுதல்"},
    {"key": "drain", "en": "Rainwater / Drain Blockage", "ta": "மழைநீர் / சாக்கடை அடைப்பு"},
    {"key": "power", "en": "Power (TNEB) Outage", "ta": "மின்சாரம் (TNEB) தடங்கல்"},
    {"key": "health", "en": "Health & Sanitation", "ta": "சுகாதாரம்"},
    {"key": "education", "en": "Educational Facility", "ta": "கல்வி வசதி"},
    {"key": "welfare", "en": "Welfare Schemes", "ta": "நல திட்டங்கள்"},
    {"key": "housing", "en": "Housing Assistance", "ta": "வீட்டு உதவி"},
    {"key": "employment", "en": "Employment & Business", "ta": "வேலைவாய்ப்பு / தொழில்"},
    {"key": "legal", "en": "Legal & Document Assistance", "ta": "சட்ட / ஆவண உதவி"},
    {"key": "other", "en": "Other Grievances", "ta": "பிற புகார்கள்"},
]

PRIORITY_SLA_DAYS = {"Urgent": 2, "High": 4, "Medium": 7, "Low": 12}
URGENT_KEYWORDS = ["fire", "accident", "collapse", "flood", "emergency", "danger", "தீ", "விபத்து", "ஆபத்து"]


# ---------------------------------------------------------------------------
# Simple JSON "database" helpers
# ---------------------------------------------------------------------------
def _load(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default


def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_tickets():
    return _load(TICKETS_FILE, [])


def save_tickets(tickets):
    _save(TICKETS_FILE, tickets)


def load_staff():
    default = [
        {"email": "admin@tvkkavundampalayam.in", "password": "Kanimozhi@2026", "name": "MLA Office Admin"}
    ]
    return _load(STAFF_FILE, default)


if not os.path.exists(STAFF_FILE):
    _save(STAFF_FILE, load_staff())


def generate_ticket_id(kind="GR"):
    year = datetime.now().year
    rand = "".join(random.choices(string.digits, k=6))
    return f"TVK-{kind}-{year}-{rand}"


def detect_priority(description):
    text = (description or "").lower()
    if any(k in text for k in URGENT_KEYWORDS):
        return "Urgent"
    if len(text) > 300:
        return "High"
    return "Medium"


# ---------------------------------------------------------------------------
# Public routes
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html", wards=WARDS, categories=CATEGORIES, streets_by_ward=STREETS_BY_WARD)


@app.route("/api/streets/<ward_no>")
def api_streets(ward_no):
    return jsonify({"streets": STREETS_BY_WARD.get(ward_no, [])})


@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json(force=True)
    mode = data.get("mode", "complaint")  # complaint | need | voice
    tickets = load_tickets()

    priority = detect_priority(data.get("description", ""))
    sla_days = PRIORITY_SLA_DAYS.get(priority, 7)
    expected = (datetime.now() + timedelta(days=sla_days)).strftime("%Y-%m-%d")

    ticket = {
        "ticket_id": generate_ticket_id("EB" if mode != "need" else "ND"),
        "mode": mode,
        "name": data.get("name", "").strip(),
        "mobile": data.get("mobile", "").strip(),
        "address": data.get("address", "").strip(),
        "ward": data.get("ward", ""),
        "street": data.get("street", ""),
        "category": data.get("category", ""),
        "need_type": data.get("need_type", ""),
        "subject": data.get("subject", ""),
        "description": data.get("description", "").strip(),
        "priority": priority,
        "status": "received",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "expected_resolution": expected,
        "timeline": [
            {"status": "received", "label_en": "Complaint Received", "label_ta": "புகார் பெறப்பட்டது",
             "by": "System", "at": datetime.now().strftime("%Y-%m-%d %H:%M")}
        ],
    }

    if not ticket["name"] or not ticket["mobile"]:
        return jsonify({"error": "Name and mobile number are required."}), 400

    tickets.append(ticket)
    save_tickets(tickets)

    return jsonify({
        "ticket_id": ticket["ticket_id"],
        "priority": ticket["priority"],
        "expected_resolution": ticket["expected_resolution"],
    })


@app.route("/track")
def track_page():
    return render_template("track.html")


@app.route("/api/track/<ticket_id>")
def api_track(ticket_id):
    tickets = load_tickets()
    ticket_id_norm = ticket_id.strip().upper()
    for t in tickets:
        if t["ticket_id"].upper() == ticket_id_norm:
            return jsonify(t)
    return jsonify({"error": "not_found"}), 404


# ---------------------------------------------------------------------------
# Staff login (simple session-based, demo only)
# ---------------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        staff = load_staff()
        match = next((s for s in staff if s["email"].lower() == email and s["password"] == password), None)
        if match:
            session["staff_email"] = match["email"]
            session["staff_name"] = match["name"]
            return redirect(url_for("dashboard"))
        error = "Invalid email or password."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    if "staff_email" not in session:
        return redirect(url_for("login"))
    tickets = load_tickets()
    total = len(tickets)
    resolved = len([t for t in tickets if t["status"] in ("resolved", "closed")])
    in_progress = len([t for t in tickets if t["status"] in ("assigned", "in_progress", "escalated")])
    pending = total - resolved - in_progress
    return render_template(
        "dashboard.html",
        tickets=sorted(tickets, key=lambda t: t["created_at"], reverse=True),
        total=total, resolved=resolved, in_progress=in_progress, pending=pending,
        staff_name=session.get("staff_name"),
    )


@app.route("/dashboard/update/<ticket_id>", methods=["POST"])
def dashboard_update(ticket_id):
    if "staff_email" not in session:
        return jsonify({"error": "unauthorized"}), 401
    new_status = request.json.get("status")
    labels = {
        "assigned": ("Assigned to Officer", "அதிகாரிக்கு ஒப்படைக்கப்பட்டது"),
        "in_progress": ("Work in Progress", "பணி நடைபெறுகிறது"),
        "escalated": ("Escalated", "மேலிடத்திற்கு தெரிவிக்கப்பட்டது"),
        "resolved": ("Resolved", "தீர்க்கப்பட்டது"),
        "closed": ("Closed", "முடிக்கப்பட்டது"),
    }
    if new_status not in labels:
        return jsonify({"error": "invalid_status"}), 400

    tickets = load_tickets()
    for t in tickets:
        if t["ticket_id"] == ticket_id:
            t["status"] = new_status
            t["timeline"].append({
                "status": new_status,
                "label_en": labels[new_status][0],
                "label_ta": labels[new_status][1],
                "by": session.get("staff_name", "MLA Office"),
                "at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            save_tickets(tickets)
            return jsonify({"ok": True})
    return jsonify({"error": "not_found"}), 404


# ---------------------------------------------------------------------------
# Simple rule-based grievance assistant ("AI chatbot")
# ---------------------------------------------------------------------------
CHAT_RULES = [
    (["hi", "hello", "vanakkam", "வணக்கம்"],
     {"en": "Vanakkam! I am the Makkal Sevai Assistant for Kavundampalayam constituency. I can help you file a complaint, check a ticket status, or answer questions about our office. How can I help you today?",
      "ta": "வணக்கம்! நான் கவுண்டம்பாளையம் தொகுதி மக்கள் சேவை உதவியாளர். புகார் பதிவு செய்ய, டிக்கெட் நிலையை பார்க்க அல்லது எங்கள் அலுவலகம் பற்றி கேள்விகளுக்கு உதவ முடியும். இன்று எப்படி உதவலாம்?"}),
    (["track", "status", "ticket", "நிலை", "டிக்கெட்"],
     {"en": "To track your complaint, go to the 'Track Complaint' page in the top menu and enter your Ticket ID (format: TVK-EB-2026-XXXXXX).",
      "ta": "உங்கள் புகார் நிலையை அறிய, மேலே உள்ள 'Track Complaint' பக்கத்திற்குச் சென்று உங்கள் டிக்கெட் ஐடியை (TVK-EB-2026-XXXXXX) உள்ளிடவும்."}),
    (["complaint", "grievance", "புகார்"],
     {"en": "You can submit a new complaint using the form on our home page. Choose 'Complaint', fill your details, ward, street and description, then submit — you'll receive a Ticket ID instantly.",
      "ta": "முகப்புப் பக்கத்தில் உள்ள படிவத்தில் புதிய புகாரை பதிவு செய்யலாம். 'Complaint' தேர்ந்தெடுத்து, உங்கள் விவரங்கள், வார்டு, தெரு, விளக்கத்தை நிரப்பி சமர்ப்பிக்கவும் — உடனே டிக்கெட் ஐடி கிடைக்கும்."}),
    (["need", "help", "assistance", "தேவை", "உதவி"],
     {"en": "For personal needs like medical assistance, welfare schemes, housing or employment help, please use the 'Needs' tab on the home page form.",
      "ta": "மருத்துவ உதவி, நல திட்டங்கள், வீட்டு உதவி அல்லது வேலைவாய்ப்பு போன்ற தனிப்பட்ட தேவைகளுக்கு முகப்புப் பக்கத்தில் உள்ள 'Needs' தாவலைப் பயன்படுத்தவும்."}),
    (["office", "address", "location", "map", "அலுவலகம்"],
     {"en": "The Kavundampalayam MLA constituency office is located on Kavundampalayam Main Road, Coimbatore - 641030. See the office map at the bottom of the home page.",
      "ta": "கவுண்டம்பாளையம் MLA தொகுதி அலுவலகம் கவுண்டம்பாளையம் மெயின் ரோடு, கோயம்புத்தூர் - 641030 அமைந்துள்ளது. முகப்புப் பக்கத்தின் கீழே உள்ள வரைபடத்தைப் பார்க்கவும்."}),
    (["mla", "kanimozhi", "who"],
     {"en": "Dr. R.D. Kanimozhi Santhosh is the Member of Legislative Assembly (MLA) for Kavundampalayam constituency, representing Tamilaga Vettri Kazhagam (TVK).",
      "ta": "டாக்டர். ஆர்.டி. கனிமொழி சந்தோஷ் அவர்கள் தமிழக வெற்றிக் கழகம் (TVK) சார்பாக கவுண்டம்பாளையம் தொகுதியின் சட்டமன்ற உறுப்பினர் (MLA) ஆவார்."}),
    (["phone", "contact", "call", "mobile number", "தொலைபேசி"],
     {"en": "You can reach the constituency office at +91 94422 11117 or email kavundampalayam.tvk@gmail.com",
      "ta": "தொகுதி அலுவலகத்தை +91 94422 11117 அல்லது kavundampalayam.tvk@gmail.com மூலம் தொடர்பு கொள்ளலாம்."}),
    (["ward", "street", "வார்டு", "தெரு"],
     {"en": "Kavundampalayam constituency covers Wards 16, 17, 33-37, 41, 44 and 45 including Kavundampalayam, Thudiyalur, Vellakinar, Somayampalayam, Rathinapuri and Nallampalayam. Select your ward in the form to see your street list.",
      "ta": "கவுண்டம்பாளையம் தொகுதியில் வார்டு 16, 17, 33-37, 41, 44, 45 உள்ளிட்ட கவுண்டம்பாளையம், துடியலூர், வெள்ளக்கினார், சோமையம்பாளையம், ரத்தினபுரி, நல்லம்பாளையம் ஆகியவை அடங்கும். படிவத்தில் உங்கள் வார்டைத் தேர்ந்தெடுத்து தெரு பட்டியலைப் பாருங்கள்."}),
    (["thank", "நன்றி"],
     {"en": "You're welcome! We're here to serve you. Vanga, namma ooru nalla irukanum!",
      "ta": "வரவேற்கிறோம்! உங்களுக்கு சேவை செய்ய நாங்கள் இருக்கிறோம். நம்ம ஊரு நல்லா இருக்கணும்!"}),
]

DEFAULT_REPLY = {
    "en": "I can help you file a complaint, submit a need, or track a ticket. Try asking: 'how to submit a complaint' or 'track my ticket'. For urgent issues, please call +91 94422 11117 directly.",
    "ta": "புகார் பதிவு, தேவை பதிவு அல்லது டிக்கெட் நிலையை அறிய உதவ முடியும். 'complaint எப்படி பதிவு செய்வது' அல்லது 'track my ticket' எனக் கேட்டுப் பாருங்கள். அவசர விஷயங்களுக்கு நேரடியாக +91 94422 11117 எண்ணை அழைக்கவும்."}


@app.route("/api/chat", methods=["POST"])
def api_chat():
    payload = request.get_json(force=True)
    message = (payload.get("message") or "").lower()
    lang = payload.get("lang", "en")

    for keywords, reply in CHAT_RULES:
        if any(kw in message for kw in keywords):
            return jsonify({"reply": reply.get(lang, reply["en"])})

    return jsonify({"reply": DEFAULT_REPLY.get(lang, DEFAULT_REPLY["en"])})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
