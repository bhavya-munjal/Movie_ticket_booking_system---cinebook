# 🎬 CineBook — Online Movie Booking System

A full-featured movie ticket booking system built with FastAPI, Jinja2, and SQLite.

## Features

- 🎬 Browse movies with posters, ratings, genres
- 🕐 View showtimes grouped by date
- 🪑 Interactive seat selection with real-time locking (5-min TTL)
- 💳 Mock payment gateway (logs to console + saves to DB)
- 📧 Mock email notifications (logs to console, plug in SMTP/SendGrid)
- 🎟 Booking confirmation with unique reference number
- 📋 My Bookings with cancellation support
- 🛠 Admin panel: manage movies, showtimes, view all bookings
- 🔐 Session-based authentication (cookie)

## Quick Start (Docker — Recommended)

```bash
# 1. Clone / unzip the project
cd cinebook

# 2. Start the app
docker compose up --build

# 3. Open in browser
http://localhost:8000
```

That's it! The database is seeded automatically on first run.

## Demo Credentials

| Role  | Email                  | Password  |
|-------|------------------------|-----------|
| Admin | admin@cinebook.com     | admin123  |
| User  | user@cinebook.com      | user123   |

## Local Setup (without Docker)

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Project Structure

```
cinebook/
├── app/
│   ├── main.py              # App entry point, router registration
│   ├── config.py            # Settings via .env
│   ├── database.py          # SQLAlchemy setup
│   ├── models.py            # All DB models
│   ├── seed.py              # Initial data seeder
│   ├── routers/
│   │   ├── auth.py          # Login, register, logout
│   │   ├── movies.py        # Home, movie detail
│   │   ├── bookings.py      # Seat selection, checkout, confirm, my bookings
│   │   └── admin.py         # Admin CRUD
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── movie_service.py
│   │   ├── seat_service.py  # Seat locking logic
│   │   └── booking_service.py
│   ├── utils/
│   │   ├── auth.py          # Password hashing, session tokens
│   │   ├── email_service.py # ← Swap _send() with real SMTP/SendGrid
│   │   └── payment_service.py # ← Swap process_payment() with Razorpay/Stripe
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # CSS, JS
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

## Plugging In Real Integrations

### Real Email (SendGrid)
Edit `app/utils/email_service.py`, replace `_send()`:
```python
import sendgrid
def _send(to, subject, body):
    sg = sendgrid.SendGridAPIClient(api_key=os.environ['SENDGRID_API_KEY'])
    # ... send email
```

### Real Payment (Razorpay)
Edit `app/utils/payment_service.py`, replace `process_payment()`:
```python
import razorpay
def process_payment(user_id, booking_ref, amount, method='card'):
    client = razorpay.Client(auth=(KEY, SECRET))
    order = client.order.create({"amount": int(amount*100), "currency": "INR"})
    # return PaymentResult(...)
```

## Tech Stack

- **Backend**: Python 3.11, FastAPI
- **Frontend**: Jinja2, HTML5, CSS3, Vanilla JS
- **Database**: SQLite (via SQLAlchemy)
- **Auth**: itsdangerous signed cookies + bcrypt
- **Server**: Uvicorn
