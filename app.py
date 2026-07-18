from flask import Flask, jsonify, request, render_template
import psycopg2
import psycopg2.extras
import os
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/tanish_book"
)

# Hotel catalogue
HOTELS = [
    {"id": 1, "name": "Hotel 1", "city": "Delhi",
     "img": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=900&q=80",
     "rooms": [
         {"id": "1-std", "type": "Standard Room", "price": 3400,
          "img": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80"},
         {"id": "1-dlx", "type": "Deluxe Room", "price": 5000,
          "img": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=900&q=80"},
     ]},
    {"id": 2, "name": "Hotel 2", "city": "Goa",
     "img": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=900&q=80",
     "rooms": [
         {"id": "2-std", "type": "Standard Room", "price": 3800,
          "img": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80"},
         {"id": "2-dlx", "type": "Deluxe Room", "price": 5500,
          "img": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=900&q=80"},
     ]},
    {"id": 3, "name": "Hotel 3", "city": "Jaipur",
     "img": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=900&q=80",
     "rooms": [
         {"id": "3-std", "type": "Standard Room", "price": 4200,
          "img": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80"},
         {"id": "3-dlx", "type": "Deluxe Room", "price": 6000,
          "img": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=900&q=80"},
     ]},
    {"id": 4, "name": "Hotel 4", "city": "Mumbai",
     "img": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=900&q=80",
     "rooms": [
         {"id": "4-std", "type": "Standard Room", "price": 4600,
          "img": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80"},
         {"id": "4-dlx", "type": "Deluxe Room", "price": 6500,
          "img": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=900&q=80"},
     ]},
    {"id": 5, "name": "Hotel 5", "city": "Shimla",
     "img": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=900&q=80",
     "rooms": [
         {"id": "5-std", "type": "Standard Room", "price": 5000,
          "img": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80"},
         {"id": "5-dlx", "type": "Deluxe Room", "price": 7000,
          "img": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=900&q=80"},
     ]},
    {"id": 6, "name": "Hotel 6", "city": "Udaipur",
     "img": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=900&q=80",
     "rooms": [
         {"id": "6-std", "type": "Standard Room", "price": 5400,
          "img": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80"},
         {"id": "6-dlx", "type": "Deluxe Room", "price": 7500,
          "img": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=900&q=80"},
     ]},
]


# Database connection
def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id SERIAL PRIMARY KEY,
            hotel_id INTEGER NOT NULL,
            hotel_name TEXT NOT NULL,
            city TEXT NOT NULL,
            room_id TEXT NOT NULL,
            room_type TEXT NOT NULL,
            room_price INTEGER NOT NULL,
            nights INTEGER NOT NULL,
            guest_name TEXT NOT NULL,
            total INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'confirmed',
            created_at BIGINT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contact_messages (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at BIGINT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            name TEXT,
            email TEXT,
            phone TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


# Page route
@app.route("/")
def index():
    return render_template("index.html")


# Hotels API
@app.route("/api/hotels")
def api_hotels():
    destination = request.args.get("destination", "").strip().lower()
    if destination:
        results = [
            h for h in HOTELS
            if destination in h["city"].lower() or destination in h["name"].lower()
        ]
    else:
        results = HOTELS
    return jsonify(results)


# Bookings API
@app.route("/api/bookings", methods=["GET"])
def list_bookings():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bookings ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/bookings", methods=["POST"])
def create_booking():
    data = request.get_json(silent=True) or {}
    required = ["hotel_id", "hotel_name", "city", "room_id", "room_type",
                "room_price", "nights", "guest_name"]
    missing = [f for f in required if f not in data or data[f] in (None, "")]
    if missing:
        return jsonify({"error": f"Missing field(s): {', '.join(missing)}"}), 400

    try:
        nights = int(data["nights"])
        room_price = int(data["room_price"])
    except (ValueError, TypeError):
        return jsonify({"error": "Nights and room_price must be numbers"}), 400

    if nights < 1:
        return jsonify({"error": "Nights must be at least 1"}), 400

    guest_name = str(data["guest_name"]).strip()
    if not guest_name:
        return jsonify({"error": "Guest name is required"}), 400

    total = room_price * nights
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO bookings
        (hotel_id, hotel_name, city, room_id, room_type, room_price,
         nights, guest_name, total, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'confirmed', %s)
        RETURNING id
    """, (data["hotel_id"], data["hotel_name"], data["city"], data["room_id"],
          data["room_type"], room_price, nights, guest_name, total, int(time.time())))
    booking_id = cur.fetchone()["id"]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": booking_id, "total": total, "status": "confirmed"}), 201


@app.route("/api/bookings/<int:booking_id>/cancel", methods=["POST"])
def cancel_booking(booking_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM bookings WHERE id=%s", (booking_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return jsonify({"error": "Booking not found"}), 404
    cur.execute("UPDATE bookings SET status='cancelled' WHERE id=%s", (booking_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True})


# Contact API
@app.route("/api/contact", methods=["POST"])
def submit_contact():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    message = str(data.get("message", "")).strip()

    if not name or not message or "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"error": "Please provide a valid name, email, and message"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO contact_messages (name, email, message, created_at) VALUES (%s, %s, %s, %s)",
        (name, email, message, int(time.time())),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True}), 201


# Profile API
@app.route("/api/profile", methods=["GET"])
def get_profile():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name, email, phone FROM profile WHERE id=1")
    row = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify(dict(row) if row else {})


@app.route("/api/profile", methods=["POST"])
def save_profile():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    phone = str(data.get("phone", "")).strip()

    if not name or "@" not in email or not (phone.isdigit() and len(phone) == 10):
        return jsonify({"error": "Please provide a valid name, email, and 10-digit phone number"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO profile (id, name, email, phone)
        VALUES (1, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name,
                                        email = EXCLUDED.email,
                                        phone = EXCLUDED.phone
    """, (name, email, phone))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True})


init_db()

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "1") == "1"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
